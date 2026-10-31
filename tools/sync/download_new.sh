#!/usr/bin/env bash
# download_new.sh -- bring in new commits from GitHub without overwriting or losing local work.
#
#   * Clean tree: fast-forward.  Uncommitted changes: stash -> fast-forward -> unstash; conflicts
#     are reported and your changes stay in `git stash list` (nothing is discarded).
#   * Files deleted on GitHub are KEPT on your disk as untracked files (use --apply-deletions to
#     let them be removed). A backup copy of every local file that git would touch is made first.
#   * Local untracked/ignored files that GitHub now also has are never overwritten: it stops.
#   * Local commits AND new GitHub commits (diverged): stops and explains, unless --rebase.
#   * Never pushes, never resets, never force-checks-out.
#
# Usage: download_new.sh [--dry-run] [--rebase] [--apply-deletions] [--remote NAME] [--branch NAME]
# Needs: bash, git >= 2.30, coreutils.  Run from anywhere inside the repository.
set -euo pipefail

PROG="download_new.sh"
DRY_RUN=0; DO_REBASE=0; APPLY_DELETIONS=0; REMOTE="origin"; BRANCH=""
die()  { printf '%s: ERROR: %s\n' "$PROG" "$*" >&2; exit 1; }
info() { printf '%s\n' "$*"; }
usage() { local n=0 l; while IFS= read -r l; do n=$((n+1)); [ $n -ge 2 ] && [ $n -le 14 ] && { l="${l#\#}"; printf '%s\n' "${l# }"; }; done < "$0"; }

while [ $# -gt 0 ]; do
  case "$1" in
    -n|--dry-run) DRY_RUN=1 ;;
    --rebase) DO_REBASE=1 ;;
    --apply-deletions) APPLY_DELETIONS=1 ;;
    --remote) [ $# -ge 2 ] || die "--remote needs a name"; REMOTE="$2"; shift ;;
    --branch) [ $# -ge 2 ] || die "--branch needs a name"; BRANCH="$2"; shift ;;
    -h|--help) usage; exit 0 ;;
    *) die "unknown option: $1 (see --help)" ;;
  esac
  shift
done

command -v git >/dev/null 2>&1 || die "git not found"
TOP="$(git rev-parse --show-toplevel 2>/dev/null)" || die "not inside a git repository"
cd "$TOP"
G() { git -c core.quotepath=off --literal-pathspecs "$@"; }
for p in rebase-merge rebase-apply MERGE_HEAD CHERRY_PICK_HEAD REVERT_HEAD; do
  [ -e "$(git rev-parse --git-path "$p")" ] && die "a git operation is in progress ($p). Finish or abort it first (see git status)."
done
if [ -n "$(git diff --name-only --diff-filter=U)" ]; then die "there are unresolved conflicts (git status). Resolve them first."; fi
CUR="$(git symbolic-ref --quiet --short HEAD)" || die "HEAD is detached; check out a branch first (git switch main)"
BRANCH="${BRANCH:-$CUR}"
[ "$BRANCH" = "$CUR" ] || die "current branch is '$CUR' but --branch is '$BRANCH'; switch first"
git remote get-url "$REMOTE" >/dev/null 2>&1 || die "remote '$REMOTE' not configured"
RREF="refs/remotes/$REMOTE/$BRANCH"

info "== Fetching $REMOTE ..."
git fetch --prune "$REMOTE" || die "git fetch failed (network? credentials?)"
git rev-parse -q --verify "$RREF" >/dev/null || die "$REMOTE/$BRANCH does not exist on the remote"
OLD="$(git rev-parse HEAD)"; NEW="$(git rev-parse "$RREF")"
read -r AHEAD BEHIND < <(git rev-list --left-right --count "HEAD...$RREF")
info "   local is $AHEAD commit(s) ahead, $BEHIND behind $REMOTE/$BRANCH"
if [ "$BEHIND" -eq 0 ]; then
  info "Already up to date: nothing new on GitHub."
  if [ "$AHEAD" -gt 0 ]; then info "(You have $AHEAD local commit(s) not on GitHub; use upload_new.sh to send them.)"; fi
  exit 0
fi
BASE="$(git merge-base HEAD "$RREF")"

# ---- what is coming down (changes on GitHub since the common base) ------------------------
INC_A=(); INC_M=(); INC_D=()
while IFS= read -r -d '' st && IFS= read -r -d '' p; do
  case "$st" in A) INC_A+=("$p") ;; D) INC_D+=("$p") ;; *) INC_M+=("$p") ;; esac
done < <(git diff -z --no-renames --name-status "$BASE" "$RREF")

# local state
DIRTY=()
while IFS= read -r -d '' p; do DIRTY+=("$p"); done < <(git diff -z --name-only HEAD)
is_dirty() { local x; for x in "${DIRTY[@]}"; do [ "$x" = "$1" ] && return 0; done; return 1; }
in_head() { git cat-file -e "HEAD:$1" 2>/dev/null; }

# incoming files that already exist locally but are NOT tracked (untracked or ignored): git would
# refuse (untracked) or silently overwrite (ignored) them -> always stop instead.
COLLIDE=()
for p in "${INC_A[@]}" "${INC_M[@]}"; do
  if { [ -e "$p" ] || [ -L "$p" ]; } && ! in_head "$p"; then COLLIDE+=("$p"); fi
done
OVERLAP=(); for p in "${INC_M[@]}" "${INC_A[@]}"; do if is_dirty "$p"; then OVERLAP+=("$p"); fi; done
KEEP=(); for p in "${INC_D[@]}"; do if [ -e "$p" ] || [ -L "$p" ]; then KEEP+=("$p"); fi; done

print_list() { local t="$1"; shift; [ $# -gt 0 ] || return 0; info "$t ($#):"; printf '    %s\n' "$@"; }
info ""
info "== Coming down from GitHub ($BEHIND commit(s)):"
git --no-pager log -n 20 --format='    %h %ad %s' --date=short "HEAD..$RREF"
info ""
git --no-pager -c core.quotepath=off diff --shortstat "$BASE" "$RREF"
print_list "   new files"      "${INC_A[@]}"
print_list "   changed files"  "${INC_M[@]}"
if [ "$APPLY_DELETIONS" = 1 ]; then print_list "   deleted on GitHub (will be removed locally)" "${INC_D[@]}"
else print_list "   deleted on GitHub (your local copy is KEPT as an untracked file)" "${INC_D[@]}"; fi
print_list "!! also changed locally (your edits are stashed and re-applied; may conflict)" "${OVERLAP[@]}"
if [ "${#COLLIDE[@]}" -gt 0 ]; then
  print_list "!! exist locally as untracked/ignored files and would be overwritten" "${COLLIDE[@]}"
  info "   Move or rename these local files (or commit them under another name), then rerun."
fi
if [ "$AHEAD" -gt 0 ]; then
  info "!! DIVERGED: you have $AHEAD local commit(s) that GitHub does not have:"
  git --no-pager log -n 20 --format='    %h %s' "$RREF..HEAD"
fi
if [ "$DRY_RUN" = 1 ]; then info ""; info "(dry-run: nothing changed)"; exit 0; fi

[ "${#COLLIDE[@]}" -eq 0 ] || die "stopped: local untracked/ignored files would be overwritten (listed above). Nothing changed."
if [ "$AHEAD" -gt 0 ] && [ "$DO_REBASE" = 0 ]; then
  die "stopped: your branch and GitHub have diverged; nothing changed. Options:
  * rerun with --rebase to replay your $AHEAD local commit(s) on top of GitHub's, or
  * run upload_new.sh (it rebases and then uploads), or
  * inspect with: git log --oneline --graph HEAD $REMOTE/$BRANCH"
fi

# ---- backup everything git might touch ----------------------------------------------------
TS="$(date -u +%Y%m%dT%H%M%SZ)"
BK="$(git rev-parse --absolute-git-dir)/download_new_backup/$TS"
backup() { local p="$1"; mkdir -p -- "$BK/$(dirname -- "$p")"; cp -a -- "$p" "$BK/$p"; }
NB=0
for p in "${DIRTY[@]}" "${KEEP[@]}"; do
  if { [ -e "$p" ] || [ -L "$p" ]; } && ! { [ -e "$BK/$p" ] || [ -L "$BK/$p" ]; }; then backup "$p"; NB=$((NB+1)); fi
done
[ "$NB" -gt 0 ] && info "== Backed up $NB local file(s) to $BK"

# files deleted upstream: detach them from git's control first so the update cannot conflict
KEPT_DIRTY=()
if [ "$APPLY_DELETIONS" = 0 ] && [ "${#KEEP[@]}" -gt 0 ]; then
  for p in "${KEEP[@]}"; do
    if is_dirty "$p"; then KEPT_DIRTY+=("$p"); G restore --source=HEAD --staged --worktree -- "$p"; fi
  done
fi

STASHED=0
if ! git diff --quiet HEAD; then
  git stash push -q -m "download_new.sh autostash $TS" || die "could not stash local changes; nothing changed"
  STASHED=1; info "== Stashed your uncommitted changes (stash: 'download_new.sh autostash $TS')"
fi

if [ "$AHEAD" -gt 0 ]; then
  info "== Rebasing your $AHEAD local commit(s) onto $REMOTE/$BRANCH ..."
  if ! git rebase "$RREF"; then
    die "rebase stopped on a conflict. Nothing is lost:
  * fix the files 'git status' lists, 'git add' them, then 'git rebase --continue'
  * or undo the rebase completely with 'git rebase --abort'
  $( [ "$STASHED" = 1 ] && echo "* afterwards re-apply your uncommitted work with 'git stash pop'" )
  * copies of your local files are in $BK"
  fi
else
  info "== Fast-forwarding to $REMOTE/$BRANCH ..."
  git merge -q --ff-only "$RREF" || {
    [ "$STASHED" = 1 ] && git stash pop -q || true
    die "fast-forward failed; your changes were restored. See messages above."; }
fi

# restore kept copies of upstream-deleted files (now untracked)
if [ "$APPLY_DELETIONS" = 0 ]; then
  for p in "${KEEP[@]}"; do
    if [ ! -e "$p" ] && [ ! -L "$p" ] && { [ -e "$BK/$p" ] || [ -L "$BK/$p" ]; }; then
      mkdir -p -- "$(dirname -- "$p")"; cp -a -- "$BK/$p" "$p"
    fi
  done
fi

CONFLICT=0
if [ "$STASHED" = 1 ]; then
  if git stash pop -q; then info "== Re-applied your uncommitted changes"
  else CONFLICT=1; fi
fi

info ""
info "== Done: $(git rev-parse --short "$OLD") -> $(git rev-parse --short HEAD)"
NA=0; NM=0; ND=0
while IFS= read -r -d '' st && IFS= read -r -d '' p; do
  case "$st" in A) NA=$((NA+1)); info "   + $p" ;; D) ND=$((ND+1)); info "   - $p" ;; *) NM=$((NM+1)); info "   M $p" ;; esac
done < <(git diff -z --no-renames --name-status "$OLD" HEAD)
info "   summary: $NA new, $NM changed, $ND deleted-on-GitHub"
if [ "$APPLY_DELETIONS" = 0 ] && [ "${#KEEP[@]}" -gt 0 ]; then
  info "   ${#KEEP[@]} file(s) deleted on GitHub were kept on your disk (now untracked; ignored ones are hidden from git status)."
fi
[ "${#KEPT_DIRTY[@]}" -gt 0 ] && print_list "   (these had local edits; your edited version is what was kept)" "${KEPT_DIRTY[@]}"
if [ "$CONFLICT" = 1 ]; then
  info ""
  info "!! Your uncommitted changes conflicted with GitHub's changes in:"
  git -c core.quotepath=off diff --name-only --diff-filter=U | while IFS= read -r l; do printf '    %s\n' "$l"; done
  info "   Nothing was discarded: your changes are still in 'git stash list' (top entry) and copies are in"
  info "   $BK. Edit the conflicted files, then 'git add' them and 'git stash drop'."
  exit 2
fi
exit 0
