import re, sys
def decls(p):
    s = open(p).read()
    out = {}
    for m in re.finditer(r"^(?:@\[[^\]]*\]\s*)?(theorem|lemma|def)\s+(\S+)(.*?)(?=:=)", s, re.M | re.S):
        out[m.group(2)] = " ".join((m.group(1) + m.group(3)).split())
    return out
a, b = decls(sys.argv[1]), decls(sys.argv[2])
assert list(a) == list(b) or sorted(a) == sorted(b), (list(a), list(b))
bad = [n for n in a if a[n] != b[n]]
print(f"{len(a)} declarations; order identical: {list(a)==list(b)}; statement mismatches: {bad}")
