#!/usr/bin/env bash
# upload_new.sh -- upload new/changed local files to GitHub, safely.
#
#   * Respects .gitignore (never uses `git add -f`).
#   * First fetches and integrates GitHub's changes (pull --rebase --autostash); stops on conflicts.
#   * Skips files over a size limit and files that look like secrets/private keys; says why.
#   * Shows exactly what will be uploaded and asks y/N (unless --yes).
#   * Never stages deletions unless --include-deletions.  Never force-pushes.
#
# Usage: upload_new.sh [--dry-run] [--yes] [-m MESSAGE] [--max-size-mb N]
#                      [--include-deletions] [--remote NAME] [--branch NAME]
# Env:   UPLOAD_MAX_MB (default 95)
# Needs: bash, git >= 2.30, coreutils.  Run from anywhere inside the repository.
set -euo pipefail

PROG="upload_new.sh"
DRY_RUN=0; ASSUME_YES=0; INCLUDE_DELETIONS=0; MESSAGE=""
MAX_MB="${UPLOAD_MAX_MB:-95}"; REMOTE="origin"; BRANCH=""

die()  { printf '%s: ERROR: %s\n' "$PROG" "$*" >&2; exit 1; }
info() { printf '%s\n' "$*"; }
usage() { local n=0 l; while IFS= read -r l; do n=$((n+1)); [ $n -ge 2 ] && [ $n -le 15 ] && { l="${l#\#}"; printf '%s\n' "${l# }"; }; done < "$0"; }

while [ $# -gt 0 ]; do
  case "$1" in
    -n|--dry-run) DRY_RUN=1 ;;
    -y|--yes) ASSUME_YES=1 ;;
    -m|--message) [ $# -ge 2 ] || die "-m needs a message"; MESSAGE="$2"; shift ;;
    --max-size-mb) [ $# -ge 2 ] || die "--max-size-mb needs a number"; MAX_MB="$2"; shift ;;
    --include-deletions) INCLUDE_DELETIONS=1 ;;
    --remote) [ $# -ge 2 ] || die "--remote needs a name"; REMOTE="$2"; shift ;;
    --branch) [ $# -ge 2 ] || die "--branch needs a name"; BRANCH="$2"; shift ;;
    -h|--help) usage; exit 0 ;;
    *) die "unknown option: $1 (see --help)" ;;
  esac
  shift
done
case "$MAX_MB" in ''|*[!0-9]*) die "--max-size-mb must be a whole number of MB" ;; esac
MAX_BYTES=$(( MAX_MB * 1024 * 1024 ))

command -v git >/dev/null 2>&1 || die "git not found"
TOP="$(git rev-parse --show-toplevel 2>/dev/null)" || die "not inside a git repository"
cd "$TOP"
G() { git -c core.quotepath=off --literal-pathspecs "$@"; }

# ---- refuse to run in the middle of another git operation -------------------------------
for p in rebase-merge rebase-apply MERGE_HEAD CHERRY_PICK_HEAD REVERT_HEAD; do
  [ -e "$(git rev-parse --git-path "$p")" ] && die "a git operation is in progress ($p). Finish it or abort it first (git status shows how)."
done
CUR="$(git symbolic-ref --quiet --short HEAD)" || die "HEAD is detached; check out a branch first (e.g. git switch main)"
BRANCH="${BRANCH:-$CUR}"
[ "$BRANCH" = "$CUR" ] || die "current branch is '$CUR' but --branch is '$BRANCH'; switch first"
git remote get-url "$REMOTE" >/dev/null 2>&1 || die "remote '$REMOTE' not configured"
RREF="refs/remotes/$REMOTE/$BRANCH"

# ---- refuse pre-staged changes (e.g. left over from an earlier `git add -f`) -------------
if ! git diff --cached --quiet; then
  info "Files are already staged (git diff --cached --name-only):"
  G diff --cached --name-only | while IFS= read -r l; do printf '    %s\n' "$l"; done
  if [ "$DRY_RUN" = 1 ]; then info "(dry-run: continuing; a real run would stop here)"; else
  die "the index already has staged changes. Review them, then unstage everything with
      git restore --staged :/
  (this keeps all files on disk) and run $PROG again."
  fi
fi

if [ "$DRY_RUN" = 0 ]; then
  if ! git config user.name >/dev/null || ! git config user.email >/dev/null; then
    die "git user.name / user.email not set (git config --global user.name 'Your Name'; git config --global user.email you@example.com)"
  fi
fi

# ---- 1. fetch and integrate remote changes ---------------------------------------------
info "== Fetching $REMOTE ..."
git fetch --prune "$REMOTE" || die "git fetch failed (network? credentials?)"
if git rev-parse -q --verify "$RREF" >/dev/null; then
  read -r AHEAD BEHIND < <(git rev-list --left-right --count "HEAD...$RREF")
  info "   local is $AHEAD commit(s) ahead, $BEHIND behind $REMOTE/$BRANCH"
  if [ "$BEHIND" -gt 0 ]; then
    if [ "$DRY_RUN" = 1 ]; then
      info "   (dry-run: would first run: git pull --rebase --autostash $REMOTE $BRANCH)"
    else
      STASH_BEFORE="$(git rev-parse -q --verify refs/stash || true)"
      info "== Integrating $BEHIND new commit(s) from GitHub (pull --rebase --autostash) ..."
      if ! git pull --rebase --autostash "$REMOTE" "$BRANCH"; then
        die "integrating GitHub's changes failed; nothing was uploaded.
  If a rebase is in progress: fix the files listed by 'git status', 'git add' them, then
  'git rebase --continue'  -- or undo everything with 'git rebase --abort'.
  If git refused because untracked files would be overwritten, move those files aside and rerun.
  Your local changes are never discarded; if they were auto-stashed, see 'git stash list'."
      fi
      STASH_AFTER="$(git rev-parse -q --verify refs/stash || true)"
      if [ "$STASH_AFTER" != "$STASH_BEFORE" ] || [ -n "$(git diff --name-only --diff-filter=U)" ]; then
        die "GitHub's changes were integrated, but re-applying your uncommitted changes conflicted.
  Your changes are safe in 'git stash list' (top entry) and/or marked in 'git status'.
  Resolve the conflicted files, then 'git stash drop' once satisfied, and rerun $PROG."
      fi
    fi
  fi
else
  info "   $REMOTE/$BRANCH does not exist yet; it will be created by the push"
  AHEAD=0
fi

# ---- 2. classify working-tree changes ----------------------------------------------------
is_secret_name() {   # $1 = repo-relative path
  local p="$1" b lc
  b="${p##*/}"; lc="${b,,}"
  case "/${p,,}/" in */.ssh/*|*/.gnupg/*|*/.aws/*|*/.password-store/*) echo "private directory"; return 0 ;; esac
  case "$lc" in
    .env.example|.env.sample|.env.template) return 1 ;;
    .env|.env.*|*.env)                    echo "environment/secrets file"; return 0 ;;
    *.key|*.pem|*.p12|*.pfx|*.jks|*.keystore|*.ppk|*.asc|*.gpg|*.der|*.crt|*.csr) echo "key/certificate file"; return 0 ;;
    id_rsa*|id_dsa*|id_ecdsa*|id_ed25519*) echo "SSH private key"; return 0 ;;
    *.kdbx|*.kdb|*.agilekeychain|*.1pif)  echo "password database"; return 0 ;;
    credentials*|*credentials.json|*credential*.*) echo "credentials file"; return 0 ;;
    token|tokens|token.*|tokens.*|*.token|*_token*|*-token*|*access_token*) echo "token file"; return 0 ;;
    *secret*|.netrc|_netrc|.git-credentials|.npmrc|.pypirc|.htpasswd|*.ovpn|.pgpass|service-account*.json) echo "secret/credential config"; return 0 ;;
  esac
  return 1
}
SECRET_RE='-----BEGIN ([A-Z]+ )?PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}|AKIA[0-9A-Z]{16}|xox[abprs]-[A-Za-z0-9-]{10,}|sk-[A-Za-z0-9_-]{32,}|AIza[0-9A-Za-z_-]{35}'
has_secret_content() { git grep --no-index -I -q -E -e "$SECRET_RE" -- "$1" 2>/dev/null; }
fsize() { stat -c %s -- "$1" 2>/dev/null || wc -c < "$1"; }

UPLOAD=(); UPLOAD_KIND=(); SKIP=(); SKIP_WHY=(); DELS=()
consider() {   # $1 path, $2 kind (new|modified)
  local p="$1" k="$2" why sz
  if [ -L "$p" ]; then UPLOAD+=("$p"); UPLOAD_KIND+=("$k (symlink)"); return; fi
  if [ -d "$p" ]; then SKIP+=("$p"); SKIP_WHY+=("directory with its own .git (would become a broken gitlink/submodule)"); return; fi
  [ -f "$p" ] || { SKIP+=("$p"); SKIP_WHY+=("not a regular file"); return; }
  if why="$(is_secret_name "$p")"; then SKIP+=("$p"); SKIP_WHY+=("looks private: $why"); return; fi
  sz="$(fsize "$p")"
  if [ "$sz" -gt "$MAX_BYTES" ]; then SKIP+=("$p"); SKIP_WHY+=("too large: $(( sz / 1048576 )) MB > ${MAX_MB} MB limit"); return; fi
  if has_secret_content "$p"; then SKIP+=("$p"); SKIP_WHY+=("contents look like a key/token"); return; fi
  UPLOAD+=("$p"); UPLOAD_KIND+=("$k")
}
while IFS= read -r -d '' entry; do
  X="${entry:0:1}"; Y="${entry:1:1}"; P="${entry:3}"
  case "$X" in R|C) IFS= read -r -d '' _orig || true ;; esac
  if [ "$X$Y" = "??" ]; then consider "${P%/}" new
  elif [ "$Y" = "D" ] || [ "$X" = "D" ]; then DELS+=("$P")
  elif [ "$Y" != " " ]; then consider "$P" modified
  fi
done < <(git -c core.quotepath=off status --porcelain=v1 -z --untracked-files=all)

# ---- 3. check already-committed but unpushed commits ----------------------------------------
UNPUSHED=()
if [ "${AHEAD:-0}" -gt 0 ] || ! git rev-parse -q --verify "$RREF" >/dev/null; then
  if git rev-parse -q --verify "$RREF" >/dev/null; then BASE="$(git merge-base "$RREF" HEAD)"
  else BASE="$(git hash-object -t tree /dev/null)"; fi
  BAD=0
  while IFS= read -r -d '' p; do
    UNPUSHED+=("$p")
    sz="$(git cat-file -s "HEAD:$p" 2>/dev/null || echo 0)"
    if [ "$sz" -gt "$MAX_BYTES" ]; then info "   unpushed commit contains '$p' ($(( sz / 1048576 )) MB > ${MAX_MB} MB)"; BAD=1; fi
    if why="$(is_secret_name "$p")"; then info "   unpushed commit contains '$p' ($why)"; BAD=1; fi
    if [ -n "$(git ls-files -ci --exclude-standard -- ":(literal)$p")" ] && ! git cat-file -e "$RREF:$p" 2>/dev/null; then
      info "   unpushed commit contains '$p', which .gitignore excludes (was it added with 'git add -f'?)"; BAD=1; fi
  done < <(git diff -z --name-only --diff-filter=AM "$BASE" HEAD)
  if [ "$BAD" = 1 ]; then
    die "local commits that are not on GitHub contain files that should not be uploaded (see above).
  Undo those commits but keep every file on disk with:   git reset --mixed $REMOTE/$BRANCH
  then rerun $PROG (it will skip those files)."
  fi
fi

# ---- 4. report -----------------------------------------------------------------------------
info ""
info "== Files to upload (${#UPLOAD[@]}):"
for i in "${!UPLOAD[@]}"; do printf '    [%s] %s\n' "${UPLOAD_KIND[$i]}" "${UPLOAD[$i]}"; done
if [ "${#UNPUSHED[@]}" -gt 0 ]; then
  info "== Already committed locally, not yet on GitHub ($AHEAD commit(s), ${#UNPUSHED[@]} file(s)):"; printf '    %s\n' "${UNPUSHED[@]}"
fi
if [ "${#SKIP[@]}" -gt 0 ]; then
  info "== Skipped (${#SKIP[@]}) -- NOT uploaded:"
  for i in "${!SKIP[@]}"; do printf '    %s  <- %s\n' "${SKIP[$i]}" "${SKIP_WHY[$i]}"; done
fi
if [ "${#DELS[@]}" -gt 0 ]; then
  if [ "$INCLUDE_DELETIONS" = 1 ]; then info "== Deletions to upload (${#DELS[@]}) -- these files will be REMOVED on GitHub:"
  else info "== Missing locally but NOT deleted on GitHub (${#DELS[@]}; use --include-deletions to delete them there):"; fi
  printf '    %s\n' "${DELS[@]}"
fi
NDEL=0; if [ "$INCLUDE_DELETIONS" = 1 ]; then NDEL="${#DELS[@]}"; fi
if [ "${#UPLOAD[@]}" -eq 0 ] && [ "$NDEL" -eq 0 ] && [ "${#UNPUSHED[@]}" -eq 0 ]; then
  info ""; info "Nothing to upload. GitHub already has everything (that is not ignored/skipped)."; exit 0
fi
if [ "$DRY_RUN" = 1 ]; then info ""; info "(dry-run: nothing staged, committed or pushed)"; exit 0; fi

# ---- 5. confirm, stage, commit, push --------------------------------------------------------
if [ "$ASSUME_YES" = 0 ]; then
  [ -r /dev/tty ] || die "no terminal for confirmation; rerun with --yes to proceed non-interactively"
  printf '\nUpload these to %s/%s? [y/N] ' "$REMOTE" "$BRANCH"
  read -r ans < /dev/tty || ans=""
  case "$ans" in y|Y|yes|YES) ;; *) info "Aborted; nothing changed."; exit 1 ;; esac
fi

STAGED=0
cleanup_index() { if [ "$STAGED" = 1 ]; then git reset -q -- . 2>/dev/null || true; fi; }
trap 'rc=$?; if [ $rc -ne 0 ]; then cleanup_index; fi; exit $rc' EXIT

if [ "${#UPLOAD[@]}" -gt 0 ] || [ "$NDEL" -gt 0 ]; then
  STAGED=1
  if [ "${#UPLOAD[@]}" -gt 0 ]; then
    printf '%s\0' "${UPLOAD[@]}" | G add --pathspec-from-file=- --pathspec-file-nul || die "git add failed; nothing committed (index reset)"
  fi
  if [ "$NDEL" -gt 0 ]; then
    printf '%s\0' "${DELS[@]}" | G rm -q --cached --pathspec-from-file=- --pathspec-file-nul || die "staging deletions failed; nothing committed (index reset)"
  fi
  if [ -z "$MESSAGE" ]; then
    MESSAGE="Upload via upload_new.sh $(date -u +%Y-%m-%dT%H:%M:%SZ) (${#UPLOAD[@]} file(s)"
    if [ "$NDEL" -gt 0 ]; then MESSAGE="$MESSAGE, $NDEL deletion(s)"; fi
    MESSAGE="$MESSAGE)"
  fi
  git commit -q -m "$MESSAGE" || die "git commit failed; nothing pushed (index reset)"
  STAGED=0
fi
info "== Pushing to $REMOTE/$BRANCH (no force) ..."
if ! git push "$REMOTE" "HEAD:refs/heads/$BRANCH"; then
  die "push was rejected (probably someone pushed meanwhile). Your commit is safe locally.
  Rerun $PROG: it will integrate GitHub's new commits first and push again."
fi
SHA="$(git rev-parse HEAD)"
info ""; info "Uploaded. Commit: $(git log -1 --format='%h %s' HEAD)"
URL="$(git remote get-url "$REMOTE")"
case "$URL" in
  https://github.com/*|git@github.com:*|ssh://git@github.com/*)
    R="${URL#https://github.com/}"; R="${R#git@github.com:}"; R="${R#ssh://git@github.com/}"; R="${R%/}"; R="${R%.git}"
    info "        https://github.com/$R/commit/$SHA" ;;
  *) info "        $SHA" ;;
esac
