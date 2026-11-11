#!/usr/bin/env python3
"""
AIEFS licensing / third-party / PII inventory  (read-only, auditable).

Usage:
    python3 inventory.py --repo <path to a clone of AIEFS> --out <output dir>

What it does (nothing here writes to, deletes from, or pushes the repo):
  1. Lists every file tracked by git (git ls-files) plus any untracked file in the
     working tree (excluding .git/).
  2. Extracts text from: PDF (poppler `pdftotext -layout`, page-aware via form feeds),
     ODT/DOCX (zip XML), ZIP archives (members are scanned recursively, nested
     PDF/DOCX/ODT included), NPZ (only string-typed arrays), and all text-like files.
  3. Runs regex scanners for: license headers, personal data (emails, phone numbers,
     IPv4 addresses, home-directory paths, street addresses, ORCID, secret/token
     patterns), and third-party publication markers (DOI, arXiv, publisher boilerplate).
  4. Applies the documented classification table MANUAL (below) plus rule-based
     fallbacks, and writes inventory.json and INVENTORY.md.

PRIVACY: matched personal values are NEVER written out. Only the type, a coarse
class (e.g. "personal webmail domain"), and location (file, page, line) are recorded.
The owner's git commit email is read from `git log` at runtime purely to label matches
as "owner"; it is never printed.
"""
import argparse, collections, hashlib, io, json, os, re, subprocess, sys, tempfile, zipfile
from pathlib import Path

# ---------------------------------------------------------------- manual decisions
# Each entry: category, reason. Categories:
#   1 = STANDALONE THIRD-PARTY (user decided: delete)
#   2 = THIRD-PARTY INSIDE CONVERSATIONS (user decided: keep)
#   UNSURE = needs the owner's decision
#   4 = OWN WORK
MANUAL = {
 "Papers/2804.05652v1.pdf": ("1",
   "Standalone copy of arXiv:2304.05652v1 'Adaptive Dynamical Networks' (Berner, Gross, Kuehn, "
   "Kurths, Yanchuk; later Physics Reports). arXiv licence is the non-exclusive distribution "
   "licence (no reuse rights for others). ALSO FLAGGED UNSURE: the AI transcript "
   "'Project Histories/Project Lead History 03.pdf' (around page 1518) discusses this paper, so it "
   "was evidently shown to a bot; but the PDF itself is a separate file, not embedded in a transcript. "
   "Deleting the PDF does not remove the discussion from the transcript.",
   "Standalone third-party PDF (rule says delete), but the paper was shown to and discussed with a bot in "
   "'Project Histories/Project Lead History 03.pdf'. Owner should decide; the conversation text survives either way."),
 "Papers/The Holland Atom_Paper_1_30.May.2026_v1.pdf": ("1",
   "Paper by John Edward Holland; page 1 says 'Copyright John Holland 2026. All rights reserved.' "
   "Only appears in the transcripts as a filename in `ls` directory listings (History 09/10); never discussed."),
 "Papers/The Holland Atom_Paper 2 Radius Variation 23.Jun.2026_v1.0.pdf": ("1",
   "Paper by John Edward Holland; page 1 'All rights reserved'. Only appears in `ls` listings in transcripts."),
 "Papers/H-Atom_Paper 3 Geometric Radius Scaling Law 19.Jul.2026_v1.0.pdf": ("1",
   "Paper by John Edward Holland; page 1 'All rights reserved'. Only appears in `ls` listings in transcripts."),
 "Project Origins/SSRH 001 stuff.pdf": ("2",
   "Export of an AI chat ('Thought for Ns' turn markers, AI 'Deep Dive' replies) in which the owner pasted "
   "the full text of many published papers for the bot to analyse."),
 "Project Histories/SSRH 000244 Stuff.odt": ("2",
   "Export of an AI chat (same 'Thought for Ns' / 'Deep Dive' format) with pasted full-text papers."),
 "Project Origins/SSH history part 002461.pdf": ("2",
   "Grok conversation export ('You' / 'Grok' speaker lines) with pasted full-text papers; it also refers "
   "to 'SSRH stuff.pdf' as the document the owner started the conversation with."),
 "Project Origins/grok ice 4009942.pdf": ("2",
   "AI conversation ('User Statement' / 'AI Agent Response') in which the owner pasted journal article "
   "text (e.g. a PNAS article with download watermarks)."),
 "Project Origins/grok ice 400994202.pdf": ("2",
   "AI conversation ('User Statement: Examine the attached documents'); the attached thesis on delay "
   "differential-algebraic equations is NOT in the repo; only the bot's summary is present."),
 "Project Histories/Project Lead History 03.pdf": ("2",
   "AIEF AI-chat transcript. Near pages ~1515-1525 the bot discusses two third-party papers the owner showed it "
   "(Martens & Bick on constrained adaptive networks; Berner et al. 'Adaptive Dynamical Networks'). "
   "Mostly commentary/paraphrase by the bot."),
 "Project Origins/SSRH stuff.pdf": ("2",
   "221-page AI-conversation export ('Statement:' user turns followed by AI 'deep dive' replies) and also the "
   "file the owner attached at the start of the Grok conversation in 'SSH history part 002461.pdf'. Third-party "
   "material is AI-written summaries plus bibliographic lists (titles/URLs); no full-text paper pastes found. "
   "Keep either way (conversation or own work)."),
}
# Directories / patterns treated as conversation transcripts (for rules + counting)
TRANSCRIPT_GLOBS = [r"^Project Histories/Project Lead History \d+\.pdf$"]

# ---------------------------------------------------------------- regexes
TEXT_EXT = {".py",".md",".txt",".json",".csv",".log",".sh",".toml",".yml",".yaml",".ini",".lean",
            ".patch",".diff",".cfg",".gitignore",".html",".htm",".xml",".tex",".bib",""}
RE_EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}")
RE_PHONE = re.compile(r"(?<![\w.])(?:\+\d{1,3}[\s.-]?)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}(?![\w.])")
RE_PHONE_CTX = re.compile(r"(?i)\b(tel|phone|fax|mobile|cell)\b")
RE_IPV4 = re.compile(r"(?<![\d.])((?:25[0-5]|2[0-4]\d|1?\d?\d)(?:\.(?:25[0-5]|2[0-4]\d|1?\d?\d)){3})(?![\d.])")
RE_IP_CTX = re.compile(r"(?i)IP address|Downloaded from .{0,40} by")
RE_HOME = re.compile(r"(?:/home/|/Users/|C:\\\\?Users\\\\?)([A-Za-z0-9_.-]+)")
RE_STREET = re.compile(r"\b\d{1,5}\s+(?:[A-Z][a-z]+\s){1,3}(?:Street|St\.|Avenue|Ave\.?|Road|Rd\.|Lane|Drive|Dr\.|Boulevard|Blvd\.?|Court|Ct\.|Way)\b")
RE_ORCID = re.compile(r"\b\d{4}-\d{4}-\d{4}-\d{3}[\dX]\b")
RE_SECRET = re.compile(r"(ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|gho_[A-Za-z0-9]{30,}|sk-[A-Za-z0-9]{32,}|"
                       r"AKIA[0-9A-Z]{16}|xox[abpr]-[A-Za-z0-9-]{10,}|-----BEGIN [A-Z ]*PRIVATE KEY-----|"
                       r"AIza[0-9A-Za-z_-]{35})")
RE_LICENSE = re.compile(r"(SPDX-License-Identifier[^\n]*|Licensed under[^\n]{0,80}|Released under[^\n]{0,80}|"
                        r"Copyright\s*(?:\(c\)|©)?\s*\d{4}[^\n]{0,80}|©\s*\d{4}[^\n]{0,80}|All rights reserved)", re.I)
RE_DOI = re.compile(r"\b10\.\d{4,9}/[^\s\"<>]+")
RE_ARXIV = re.compile(r"arXiv[: ]\s*(\d{4}\.\d{4,5})(v\d+)?", re.I)
RE_PUBLISHER = re.compile(r"(?i)Downloaded from|Open Access This article|licensee|Publisher.s note|"
                          r"Reprints and permissions|All rights reserved|©\s*\d{4}|Copyright\s*©?\s*\d{4}|"
                          r"\bReceived:?\s+\d{1,2}\s+\w+\s+\d{4}|Published online|Corresponding author|\bISSN\b")
RE_CITEBR = re.compile(r"\[\d+(?:[,–-]\s?\d+)*\]")
RE_HYPH = re.compile(r"[a-z]-\n\s*[a-z]")
RE_REFLINE = re.compile(r"(?m)^\s*\[?\d{1,3}[\].]\s+[A-Z][a-z]+,? [A-Z]\.")
BAD_TLDS = {"array","tld","shape","reshape","astype","mean","sum","py","md","T","item","values"}
RE_TURN = re.compile(r"(?m)^\s*(?:Thought for \d+s|You\s*$|Grok\s*$|User Statement:|AI Agent Response:|Worked for |Statement:)")
RE_DEEPDIVE = re.compile(r"(?m)^\s*(?:#+\s*)?(Deep (?:Dive|Investigation)[^\n]{0,200})")
WEBMAIL = {"gmail.com","hotmail.com","outlook.com","outlook.it","yahoo.com","icloud.com","proton.me",
           "protonmail.com","aol.com","live.com","gmx.de","gmx.net","mail.ru","qq.com","163.com"}
EXAMPLE_DOMAINS = {"example.com","example.org","example.invalid","example.net"}

def sh(*a, **kw):
    return subprocess.run(a, capture_output=True, text=True, **kw)

def classify_email(addr, owner_email):
    dom = addr.split("@",1)[1].lower()
    if dom.rsplit(".",1)[-1] in BAD_TLDS: return None
    if addr.lower().startswith("git@"): return None  # git SSH remote syntax, not a person
    if owner_email and addr.lower() == owner_email.lower():
        return "owner personal email (same as git commit email)"
    if dom in EXAMPLE_DOMAINS: return None
    if dom.endswith("noreply.github.com"): return "github noreply address"
    if dom in WEBMAIL: return "third-party personal webmail address"
    return "institutional/organisational email (domain TLD ." + dom.rsplit(".",1)[-1] + ")"

# ---------------------------------------------------------------- text extraction
def pdf_pages(path):
    r = subprocess.run(["pdftotext","-layout",str(path),"-"], capture_output=True)
    t = r.stdout.decode("utf-8","replace")
    return t.split("\f")

def odt_paras(data):
    z = zipfile.ZipFile(io.BytesIO(data))
    name = "content.xml" if "content.xml" in z.namelist() else "word/document.xml"
    x = z.read(name).decode("utf-8","replace")
    x = re.sub(r"<(text:p|text:h|w:p)[ >]", "\n<", x)
    x = re.sub(r"<[^>]+>", "", x)
    import html
    return html.unescape(x)

def units_for(relpath, data, depth=0):
    """Yield (location_label, text, kind) units. kind: page|para|line"""
    ext = Path(relpath).suffix.lower()
    if ext == ".pdf":
        with tempfile.NamedTemporaryFile(suffix=".pdf") as tf:
            tf.write(data); tf.flush()
            for i, p in enumerate(pdf_pages(tf.name), 1):
                yield (f"page {i}", p, "page")
    elif ext in (".odt", ".docx"):
        try: yield ("doc", odt_paras(data), "para")
        except Exception as e: yield ("doc", "", "para")
    elif ext == ".zip" and depth < 3:
        try:
            z = zipfile.ZipFile(io.BytesIO(data))
            for n in z.namelist():
                if n.endswith("/"): continue
                for loc, t, k in units_for(n, z.read(n), depth+1):
                    yield (f"member {n} {loc}", t, k)
        except zipfile.BadZipFile: pass
    elif ext == ".npz":
        try:
            import numpy as np
            with np.load(io.BytesIO(data), allow_pickle=False) as z:
                for k in z.files:
                    a = z[k]
                    if a.dtype.kind in "US":
                        yield (f"array {k}", "\n".join(map(str, a.ravel().tolist())), "line")
        except Exception: pass
    elif ext in TEXT_EXT or ext in (".bin",):
        if b"\x00" in data[:4096] and ext != ".bin": return
        if ext == ".bin" and data[:2] == b"PK":
            yield from units_for(relpath + ".docx", data, depth+1); return
        yield ("text", data.decode("utf-8","replace"), "line")

# ---------------------------------------------------------------- main scan
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    repo = Path(a.repo).resolve(); out = Path(a.out).resolve()
    head = sh("git","-C",str(repo),"rev-parse","HEAD").stdout.strip()
    tracked = sh("git","-C",str(repo),"-c","core.quotepath=off","ls-files","-z").stdout.split("\0")
    tracked = [t for t in tracked if t]
    allfiles = set(tracked)
    for root, dirs, files in os.walk(repo):
        dirs[:] = [d for d in dirs if d != ".git"]
        for f in files:
            allfiles.add(str(Path(root, f).relative_to(repo)))
    allfiles = sorted(allfiles)
    authors = sh("git","-C",str(repo),"log","--format=%ae%n%ce").stdout.split()
    owner_email = next((e for e in authors if not e.endswith("noreply.github.com")), None)
    commit_email_counts = collections.Counter(
        "personal webmail (gmail)" if e == owner_email else ("github noreply" if "noreply" in e else "other")
        for e in sh("git","-C",str(repo),"log","--format=%ae").stdout.split())

    files = []; pii = []; lic = []; tp_units = {}
    for rel in allfiles:
        p = repo / rel
        if not p.is_file(): continue
        data = p.read_bytes()
        rec = {"path": rel, "size": len(data), "sha256": hashlib.sha256(data).hexdigest(),
               "tracked": rel in tracked, "ext": p.suffix.lower()}
        if rec["ext"] == ".pdf":
            info = sh("pdfinfo", str(p)).stdout
            md = dict(re.findall(r"(?m)^(Title|Author|Pages|Creator|Producer|CreationDate):\s*(.*)$", info))
            rec["pdfinfo"] = md
        # skip deep content scan of the big numeric data files except strings in npz
        per_file = {"turn_markers":0, "dois":set(), "arxiv":set(), "pages":0, "flagged_pages":[],
                    "deep_dives":[], "publisher_hits":0}
        for loc, text, kind in units_for(rel, data):
            if kind == "page": per_file["pages"] += 1
            per_file["turn_markers"] += len(RE_TURN.findall(text))
            per_file["dois"].update(d.rstrip(".,;)") for d in RE_DOI.findall(text))
            per_file["arxiv"].update(m[0] for m in RE_ARXIV.findall(text))
            ph = len(RE_PUBLISHER.findall(text)); per_file["publisher_hits"] += ph
            for m in RE_DEEPDIVE.findall(text):
                if len(per_file["deep_dives"]) < 400: per_file["deep_dives"].append(re.sub(r"\s+"," ",m).strip()[:200])
            chunks = [(loc, text)] if kind == "page" else (
                [(f"{loc} lines {i+1}-{i+60}", "\n".join(text.split("\n")[i:i+60]))
                 for i in range(0, len(text.split("\n")), 60)] if kind == "para" else [])
            for cloc, ctext in chunks:
                cb = len(RE_CITEBR.findall(ctext)); hy = len(RE_HYPH.findall(ctext))
                rl = len(RE_REFLINE.findall(ctext)); pc = len(RE_PUBLISHER.findall(ctext))
                if pc >= 1 or hy >= 4 or cb >= 5 or rl >= 5:
                    per_file["flagged_pages"].append(cloc)
            lines = text.split("\n")
            for ln, line in enumerate(lines, 1):
                where = {"path": rel, "unit": loc, "line": ln}
                for m in RE_LICENSE.finditer(line):
                    if rec["ext"] in (".npz",): continue
                    lic.append({**where, "match": m.group(0).strip()[:160]})
                for m in RE_EMAIL.finditer(line):
                    c = classify_email(m.group(0), owner_email)
                    if c: pii.append({**where, "type": "email", "class": c})
                for m in RE_SECRET.finditer(line):
                    pii.append({**where, "type": "secret/token", "class": m.group(0)[:4] + "... pattern"})
                for m in RE_HOME.finditer(line):
                    u = m.group(1)
                    cls = "OS username in home path (value not recorded)"
                    pii.append({**where, "type": "home-directory path", "class": cls})
                for m in RE_ORCID.finditer(line):
                    if re.search(r"(?i)orcid", line):
                        pii.append({**where, "type": "ORCID iD", "class": "author identifier"})
                if RE_IP_CTX.search(line) or RE_IP_CTX.search(lines[ln-2] if ln > 1 else ""):
                    for m in RE_IPV4.finditer(line):
                        pii.append({**where, "type": "IPv4 address", "class": "publisher download watermark (downloader's IP)"})
                if RE_PHONE_CTX.search(line) and rec["ext"] not in (".csv",".npz",".json"):
                    for m in RE_PHONE.finditer(line):
                        pii.append({**where, "type": "phone number", "class": "phone/fax near 'tel/phone/fax' label"})
                if rec["ext"] not in (".csv",".npz",".json",".py",".log"):
                    for m in RE_STREET.finditer(line):
                        pii.append({**where, "type": "street address", "class": "street-address pattern"})
        per_file["dois"] = sorted(per_file["dois"]); per_file["arxiv"] = sorted(per_file["arxiv"])
        rec["evidence"] = {k: v for k, v in per_file.items()}
        # ---- classification
        if rel in MANUAL:
            rec["category"], rec["reason"] = MANUAL[rel][:2]
            rec["unsure"] = MANUAL[rel][2] if len(MANUAL[rel]) > 2 else None
        elif any(re.match(g, rel) for g in TRANSCRIPT_GLOBS):
            rec["category"], rec["reason"] = "4", "AIEF AI-chat transcript (owner's own conversation); no embedded third-party paper text detected"
        else:
            rec["category"], rec["reason"] = "4", "own work (code, data, results, docs, audits)"
        files.append(rec)

    # ---- references to category-1 files anywhere in the repo (text files + extracted text)
    cat1 = [f for f in files if f["category"] == "1"]
    refs = {f["path"]: [] for f in cat1}
    for f in cat1:
        base = Path(f["path"]).name; stem = Path(base).stem
        keys = {base, stem}
        g = sh("git","-C",str(repo),"grep","-n","-I","-F", *sum((["-e",k] for k in keys), []))
        for line in g.stdout.splitlines():
            fn, ln, _ = line.split(":", 2)
            refs[f["path"]].append({"path": fn, "line": int(ln), "kind": "text file"})
    for f in files:
        if f["ext"] in (".pdf",".odt",".docx",".zip"):
            for loc, text, kind in units_for(f["path"], (repo/f["path"]).read_bytes()):
                flat = re.sub(r"\s+", " ", text)
                for c in cat1:
                    base = Path(c["path"]).name
                    if base in text or base in flat:
                        refs[c["path"]].append({"path": f["path"], "unit": loc, "kind": "inside document (e.g. ls listing)"})
    for f in cat1: f["references"] = refs[f["path"]]

    summary = collections.Counter(f["category"] for f in files)
    result = {"repo": str(repo), "head": head, "generated_by": "scripts/inventory.py",
              "file_count": len(files), "category_counts": dict(summary),
              "git_history_commit_emails": dict(commit_email_counts),
              "files": files, "pii_findings": pii, "license_headers": lic}
    (out/"inventory.json").write_text(json.dumps(result, indent=1, ensure_ascii=False))
    print(json.dumps({"files": len(files), "categories": dict(summary), "pii": len(pii), "license_hits": len(lic)}))

if __name__ == "__main__":
    main()
