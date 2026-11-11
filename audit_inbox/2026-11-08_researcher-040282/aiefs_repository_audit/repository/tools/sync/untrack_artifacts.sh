#!/usr/bin/env bash
# untrack_artifacts.sh -- one-time cleanup: stop tracking build/cache/editor files that
# .gitignore already excludes, in ONE commit, keeping the files on your disk.
#
#   * Only touches files that are BOTH tracked and ignored (git ls-files -ci --exclude-standard)
#     AND look like clear artifacts: .lake/ build dirs, __pycache__/, *.pyc/*.pyo, *.olean/*.ilean,
#     office lock files (.~lock.*#), editor swap/backup files, .DS_Store, Thumbs.db.
#   * Everything else that is tracked-but-ignored (logs, data, PDFs...) is only LISTED for you.
#   * Uses `git rm --cached`: files stay on disk; history is NOT rewritten.
#   * Fast-forwards to GitHub first; refuses if diverged or if files are already staged.
#   * Shows the list and asks y/N before committing, and again before pushing. Never force-pushes.
#
# Usage: untrack_artifacts.sh [--dry-run] [--yes] [--no-push] [--remote NAME]
# Needs: bash, git >= 2.30, coreutils.  Run from anywhere inside the repository.
set -euo pipefail
PROG="untrack_artifacts.sh"; DRY_RUN=0; ASSUME_YES=0; NO_PUSH=0; REMOTE="origin"
die()  { printf '%s: ERROR: %s\n' "$PROG" "$*" >&2; exit 1; }
info() { printf '%s\n' "$*"; }
usage() { local n=0 l; while IFS= read -r l; do n=$((n+1)); if [ $n -ge 2 ] && [ $n -le 14 ]; then l="${l#\#}"; printf '%s\n' "${l# }"; fi; done < "$0"; }
while [ $# -gt 0 ]; do
  case "$1" in
    -n|--dry-run) DRY_RUN=1 ;; -y|--yes) ASSUME_YES=1 ;; --no-push) NO_PUSH=1 ;;
    --remote) [ $# -ge 2 ] || die "--remote needs a name"; REMOTE="$2"; shift ;;
    -h|--help) usage; exit 0 ;; *) die "unknown option: $1 (see --help)" ;;
  esac; shift
done
ask() { # ask "question" -> 0 if yes
  if [ "$ASSUME_YES" = 1 ]; then return 0; fi
  local a=""; if [ -r /dev/tty ]; then printf '%s [y/N] ' "$1" > /dev/tty; IFS= read -r a < /dev/tty || a=""; else die "no terminal to confirm; rerun with --yes"; fi
  case "$a" in y|Y|yes|YES) return 0 ;; *) return 1 ;; esac; }

TOP="$(git rev-parse --show-toplevel 2>/dev/null)" || die "not inside a git repository"; cd "$TOP"
for p in rebase-merge rebase-apply MERGE_HEAD CHERRY_PICK_HEAD REVERT_HEAD; do
  if [ -e "$(git rev-parse --git-path "$p")" ]; then die "a git operation is in progress ($p); finish or abort it first"; fi
done
BR="$(git symbolic-ref --quiet --short HEAD)" || die "HEAD is detached; git switch main first"
RREF="refs/remotes/$REMOTE/$BR"
if ! git diff --cached --quiet; then
  die "files are already staged (leftovers from an earlier 'git add'?). Unstage them first with:
    git restore --staged :/
  (this only unstages; your files are not changed), then rerun."
fi
info "== Fetching $REMOTE ..."; git fetch --prune "$REMOTE"
if git rev-parse -q --verify "$RREF" >/dev/null; then
  read -r AHEAD BEHIND < <(git rev-list --left-right --count "HEAD...$RREF")
  if [ "$AHEAD" -gt 0 ] && [ "$BEHIND" -gt 0 ]; then die "your branch and $REMOTE/$BR have diverged ($AHEAD local, $BEHIND remote commits). Sync first (download_new.sh --rebase), then rerun."; fi
  if [ "$BEHIND" -gt 0 ]; then
    if [ "$DRY_RUN" = 1 ]; then info "(dry-run: $BEHIND new commit(s) on GitHub would be fast-forwarded first; list below is for your current checkout)"
    else info "== Fast-forwarding $BEHIND commit(s) from GitHub ..."; git merge --ff-only --autostash "$RREF" || die "fast-forward failed; run download_new.sh first, then rerun"; fi
  fi
fi

# .gitignore lines this cleanup makes sure exist (appended if missing, in the same commit)
ADD_IGN=(".lake/" "lake-packages/" ".check_logs/" ".~lock.*#" "*.swp" "*.swo" "*~" ".#*")
MISSING=()
for l in "${ADD_IGN[@]}"; do
  found=0
  if [ -f .gitignore ]; then while IFS= read -r x || [ -n "$x" ]; do if [ "$x" = "$l" ]; then found=1; break; fi; done < .gitignore; fi
  if [ $found = 0 ]; then MISSING+=("$l"); fi
done
XARGS=(); for l in "${MISSING[@]}"; do XARGS+=(-x "$l"); done

is_artifact() { case "/$1" in
  */.lake/*|*/lake-packages/*|*/__pycache__/*|*.pyc|*.pyo|*.olean|*.ilean|*/.~lock.*\#|*.swp|*.swo|*~|*/.DS_Store|*/Thumbs.db) return 0 ;;
  *) return 1 ;; esac; }
ART=(); OTHER=()
while IFS= read -r -d '' f; do
  if is_artifact "$f"; then ART+=("$f"); else OTHER+=("$f"); fi
done < <(git ls-files -z -ci --exclude-standard ${XARGS[@]+"${XARGS[@]}"})

if [ ${#OTHER[@]} -gt 0 ]; then
  info ""; info "== Tracked but ignored, NOT artifacts -- left alone, your decision (${#OTHER[@]}):"
  for f in "${OTHER[@]}"; do printf '    %s\n' "$f"; done
  info "   (to keep tracking them cleanly, add e.g.  !path/**/*.log  to .gitignore; to stop tracking: git rm --cached PATH)"
fi
if [ ${#MISSING[@]} -gt 0 ]; then info ""; info "== Lines to add to .gitignore (${#MISSING[@]}):"; for l in "${MISSING[@]}"; do printf '    %s\n' "$l"; done; fi
info ""; info "== Artifacts to stop tracking (files stay on disk) (${#ART[@]}):"
for f in "${ART[@]}"; do printf '    %s\n' "$f"; done
if [ ${#ART[@]} -eq 0 ]; then info "   nothing to do."; exit 0; fi
if [ "$DRY_RUN" = 1 ]; then info ""; info "(dry-run: nothing changed)"; exit 0; fi
ask "Stop tracking these ${#ART[@]} file(s) (and update .gitignore) in one commit?" || die "aborted; nothing changed"

trap 'git reset -q' ERR
if [ ${#MISSING[@]} -gt 0 ]; then
  if [ -s .gitignore ] && [ -n "$(tail -c 1 .gitignore)" ]; then printf '\n' >> .gitignore; fi
  { printf '\n# Build outputs, local logs, editor lock/swap/backup files (added by untrack_artifacts.sh)\n'; printf '%s\n' "${MISSING[@]}"; } >> .gitignore
  git add .gitignore
fi
printf '%s\0' "${ART[@]}" | git rm -q --cached --pathspec-from-file=- --pathspec-file-nul
git commit -q -m "Stop tracking build/cache/editor artifacts already excluded by .gitignore" \
  -m "Untracked with git rm --cached (files kept on disk; history unchanged): ${#ART[@]} file(s). .gitignore lines added: ${#MISSING[@]}."
trap - ERR
info "== Committed $(git rev-parse --short HEAD) (local only so far)."
for f in "${ART[@]}"; do if [ ! -e "$f" ] && [ ! -L "$f" ]; then die "unexpected: $f missing from disk"; fi; done
if [ "$NO_PUSH" = 1 ]; then info "(--no-push: push later with: git push $REMOTE HEAD:$BR)"; exit 0; fi
if ask "Push this commit to $REMOTE/$BR now?"; then
  git push "$REMOTE" "HEAD:refs/heads/$BR" || die "push rejected (someone pushed meanwhile?). Run download_new.sh, then: git push $REMOTE HEAD:$BR"
  info "== Pushed $(git rev-parse HEAD)"
else info "Not pushed. Push later with: git push $REMOTE HEAD:$BR"; fi
