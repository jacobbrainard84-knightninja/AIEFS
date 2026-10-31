#!/usr/bin/env bash
# Test harness for upload_new.sh / download_new.sh.
# Builds a throw-away simulation in a temp dir: a bare "GitHub" repo plus two clones
#   mine  = the owner's machine (where the scripts run)
#   other = another machine / the GitHub web UI / an agent pushing changes
# Never touches any real remote.  Usage: tests/run_tests.sh [path/to/git]   (log: stdout)
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UP="$HERE/../upload_new.sh"; DOWN="$HERE/../download_new.sh"
if [ -n "${1:-}" ]; then export PATH="$(dirname "$1"):$PATH"; fi
ROOT="$(mktemp -d /tmp/synctest.XXXXXX)"
export HOME="$ROOT/home"; mkdir -p "$HOME"
export GIT_CONFIG_NOSYSTEM=1
git config --global init.defaultBranch main
git config --global user.name "Test User"; git config --global user.email "test@example.invalid"
git config --global advice.detachedHead false
echo "git: $(git --version)   bash: $BASH_VERSION   sandbox: (temp dir)"

PASS=0; FAIL=0; FAILED=()
ok()   { PASS=$((PASS+1)); echo "  PASS: $*"; }
bad()  { FAIL=$((FAIL+1)); FAILED+=("$CUR_T: $*"); echo "  FAIL: $*"; }
check(){ local d="$1"; shift; if "$@"; then ok "$d"; else bad "$d"; fi; }
T()    { CUR_T="$1"; echo; echo "=== $1"; }
run()  { # run NAME cmd... : captures output in $OUT, rc in $RC
  local n="$1"; shift; OUT="$("$@" 2>&1)"; RC=$?; printf '%s\n' "$OUT" | while IFS= read -r l; do printf '    | %s\n' "$l"; done; echo "    rc=$RC"; }
has()  { printf '%s' "$OUT" | grep -qF -- "$1"; }
remote_has() { git --git-dir="$ROOT/github.git" cat-file -e "main:$1" 2>/dev/null; }
remote_head(){ git --git-dir="$ROOT/github.git" rev-parse main; }
mb() { head -c $(( $2 * 1024 * 1024 )) /dev/zero | tr '\0' 'a' > "$1"; }

# ---------- set up ----------
git init -q --bare "$ROOT/github.git"
git clone -q "$ROOT/github.git" "$ROOT/seed" 2>/dev/null
cd "$ROOT/seed"
printf '__pycache__/\n*.py[cod]\n*.log\n.lake/\n.env\n' > .gitignore
mkdir -p "AI Agent Audits" lean/AIEFProofs/.lake/build src
echo "audit v1" > "AI Agent Audits/report one.md"
echo "line1" > shared.txt; printf 'a\nb\nc\n' > conflict.txt
echo "print(1)" > src/main.py
echo "olean-v1" > lean/AIEFProofs/.lake/build/A.olean
echo "to be removed upstream" > old_upstream.txt
git add .gitignore "AI Agent Audits" shared.txt conflict.txt src old_upstream.txt
git add -f lean/AIEFProofs/.lake/build/A.olean      # simulate the historical mistake: tracked build file
git commit -q -m "seed" && git push -q origin main 2>/dev/null
git clone -q "$ROOT/github.git" "$ROOT/mine"; git clone -q "$ROOT/github.git" "$ROOT/other"
MINE="$ROOT/mine"; OTHER="$ROOT/other"
other_commit() { ( cd "$OTHER" && git pull -q --ff-only && "$@" && git add -A && git commit -q -m "other: change" && git push -q origin main ) >/dev/null 2>&1; }

# =====================================================================
T "U1 upload --dry-run lists new/modified/skipped, changes nothing"
cd "$MINE/src"            # run from a subdirectory
echo "new audit" > "$MINE/AI Agent Audits/new file with spaces.md"
echo "x" > "$MINE/weird [name] *star*.txt"
echo "line1 changed" > "$MINE/shared.txt"
echo "SECRET=1" > "$MINE/.env"            # ignored by .gitignore -> must not appear at all
mkdir -p "$MINE/deploy"; echo "SECRET=2" > "$MINE/deploy/.env.production"   # NOT ignored -> secret filter
echo '{"k":1}' > "$MINE/credentials.json"; echo pw > "$MINE/vault.kdbx"; echo t > "$MINE/api_token.txt"
echo "harmless" > "$MINE/.env.example"
echo "fake" > "$MINE/id_rsa"
echo "token = "gh""p_abcdefghijklmnopqrstuvwxyz0123456789AB"" > "$MINE/notes_with_key.txt"
mkdir -p "$MINE/keys"; echo k > "$MINE/keys/server.pem"
mb "$MINE/big data.bin" 2
echo "log" > "$MINE/run.log"; mkdir -p "$MINE/__pycache__"; echo b > "$MINE/__pycache__/m.cpython-313.pyc"
mkdir -p "$MINE/nested"; ( cd "$MINE/nested" && git init -q && echo n > n.txt && git add n.txt && git commit -q -m n )
rm "$MINE/old_upstream.txt"
H0="$(remote_head)"
run u1 "$UP" --dry-run --max-size-mb 1
check "exit 0" [ "$RC" -eq 0 ]
check "lists file with spaces" has "AI Agent Audits/new file with spaces.md"
check "lists glob-char name" has "weird [name] *star*.txt"
check "lists modified shared.txt" has "[modified] shared.txt"
check "skips big file (size)" has "big data.bin  <- too large"
check "skips deploy/.env.production" has "deploy/.env.production  <- looks private"
check "skips credentials.json" has "credentials.json  <- looks private"
check "skips vault.kdbx" has "vault.kdbx  <- looks private: password database"
check "skips api_token.txt" has "api_token.txt  <- looks private: token file"
check "allows .env.example" has "[new] .env.example"
check "ignored .env not listed at all" bash -c '! printf "%s\n" "$1" | grep -qE "(^|[ /])\.env( |$)"' _ "$OUT"
check "skips id_rsa" has "id_rsa  <- looks private: SSH private key"
check "skips *.pem" has "keys/server.pem  <- looks private"
check "skips token content" has "notes_with_key.txt  <- contents look like a key/token"
check "skips nested git repo" has "nested  <- directory with its own .git"
check "ignored run.log not listed" bash -c '! printf "%s" "$1" | grep -q "run.log"' _ "$OUT"
check "ignored .pyc not listed" bash -c '! printf "%s" "$1" | grep -q "pyc"' _ "$OUT"
check "deletion reported but not staged" has "NOT deleted on GitHub"
check "remote unchanged" [ "$(remote_head)" = "$H0" ]
check "index still clean" git -C "$MINE" diff --cached --quiet

T "U2 upload --yes uploads only the allowed files, never deletions"
run u2 "$UP" --yes --max-size-mb 1
check "exit 0" [ "$RC" -eq 0 ]
check "remote has file with spaces" remote_has "AI Agent Audits/new file with spaces.md"
check "remote has glob-char file" remote_has "weird [name] *star*.txt"
check "remote shared.txt updated" [ "$(git --git-dir="$ROOT/github.git" show main:shared.txt)" = "line1 changed" ]
for f in .env deploy/.env.production credentials.json vault.kdbx api_token.txt id_rsa keys/server.pem notes_with_key.txt "big data.bin" run.log __pycache__/m.cpython-313.pyc nested; do
  check "remote lacks $f" bash -c '! git --git-dir="$1" cat-file -e "main:$2" 2>/dev/null' _ "$ROOT/github.git" "$f"
done
check "remote still has old_upstream.txt (no deletion)" remote_has old_upstream.txt
check "prints commit line" has "Uploaded. Commit:"
check "commit message timestamped" bash -c 'git -C "$1" log -1 --format=%s | grep -qE "^Upload via upload_new.sh [0-9]{4}-[0-9]{2}-[0-9]{2}T"' _ "$MINE"

T "U3 second run: nothing new"
run u3 "$UP" --yes --max-size-mb 1
check "exit 0" [ "$RC" -eq 0 ]
check "says nothing new" has "Nothing to upload"

T "U4 --include-deletions deletes on GitHub, custom -m"
run u4 "$UP" --yes --include-deletions -m "remove old file" --max-size-mb 1
check "exit 0" [ "$RC" -eq 0 ]
check "remote no longer has old_upstream.txt" bash -c '! git --git-dir="$1" cat-file -e main:old_upstream.txt 2>/dev/null' _ "$ROOT/github.git"
check "custom message" [ "$(git --git-dir="$ROOT/github.git" log -1 --format=%s main)" = "remove old file" ]

T "U5 remote ahead: upload integrates first (rebase), then pushes; history linear"
other_commit bash -c 'echo "from other" > other_new.txt'
echo "mine new" > "$MINE/mine_new.txt"
echo "dirty but uploaded" >> "$MINE/src/main.py"
run u5 "$UP" --yes --max-size-mb 1
check "exit 0" [ "$RC" -eq 0 ]
check "mine got other_new.txt" [ -f "$MINE/other_new.txt" ]
check "remote has mine_new.txt" remote_has mine_new.txt
check "no merge commits" [ -z "$(git -C "$MINE" rev-list --merges HEAD)" ]

T "U6 uncommitted local edit conflicts with remote: stops, nothing pushed, edit safe in stash"
other_commit bash -c 'printf "a\nREMOTE\nc\n" > conflict.txt'
printf 'a\nLOCAL\nc\n' > "$MINE/conflict.txt"
H0="$(remote_head)"
run u6 "$UP" --yes --max-size-mb 1
check "exit nonzero" [ "$RC" -ne 0 ]
check "explains stash" has "git stash list"
check "remote unchanged" [ "$(remote_head)" = "$H0" ]
check "local edit recoverable from stash or tree" bash -c 'cd "$1"; grep -q LOCAL conflict.txt || git stash show -p | grep -q "+LOCAL"' _ "$MINE"
# clean up for next test: keep local version as resolution
( cd "$MINE"; git checkout -q HEAD -- conflict.txt 2>/dev/null; git reset -q; git stash drop -q 2>/dev/null; true )

T "U7 committed local change conflicts with remote: rebase stops with instructions"
other_commit bash -c 'printf "a\nREMOTE2\nc\n" > conflict.txt'
( cd "$MINE" && printf 'a\nLOCAL2\nc\n' > conflict.txt && git commit -q -am "local conflicting" )
H0="$(remote_head)"
run u7 "$UP" --yes --max-size-mb 1
check "exit nonzero" [ "$RC" -ne 0 ]
check "rebase instructions" has "git rebase --abort"
check "remote unchanged" [ "$(remote_head)" = "$H0" ]
( cd "$MINE" && git rebase --abort && git reset -q --hard origin/main ) >/dev/null 2>&1

T "U8 refuses pre-staged changes (e.g. left by 'git add -f')"
( cd "$MINE" && echo l > forced.log && git add -f forced.log )
run u8 "$UP" --yes
check "exit nonzero" [ "$RC" -ne 0 ]
check "tells how to unstage" has "git restore --staged :/"
( cd "$MINE" && git restore --staged :/ && rm forced.log )

T "U9 refuses to push an unpushed commit that contains force-added ignored / oversized files"
( cd "$MINE" && echo l > forced2.log && git add -f forced2.log && git commit -q -m "oops add -f" )
H0="$(remote_head)"
run u9 "$UP" --yes
check "exit nonzero" [ "$RC" -ne 0 ]
check "names the ignored file" has "forced2.log"
check "suggests reset --mixed" has "git reset --mixed origin/main"
check "remote unchanged" [ "$(remote_head)" = "$H0" ]
( cd "$MINE" && git reset -q --mixed origin/main && rm forced2.log )

T "U10 no --yes and no answer -> aborts, nothing changed"
echo "needs confirm" > "$MINE/confirm.txt"; H0="$(remote_head)"
OUT="$(cd "$MINE" && setsid -w "$UP" < /dev/null 2>&1)"; RC=$?; echo "    rc=$RC"
check "exit nonzero" [ "$RC" -ne 0 ]
check "remote unchanged" [ "$(remote_head)" = "$H0" ]
rm "$MINE/confirm.txt"

T "U11 push rejected race is reported (simulated via pre-receive hook), commit kept locally"
printf '#!/bin/sh\necho "simulated rejection" >&2\nexit 1\n' > "$ROOT/github.git/hooks/pre-receive"; chmod +x "$ROOT/github.git/hooks/pre-receive"
echo "race" > "$MINE/race.txt"
run u11 "$UP" --yes
check "exit nonzero" [ "$RC" -ne 0 ]
check "explains rerun" has "Rerun upload_new.sh"
check "commit kept locally" bash -c 'git -C "$1" log -1 --format=%s | grep -q "Upload via"' _ "$MINE"
rm "$ROOT/github.git/hooks/pre-receive"
run u11b "$UP" --yes
check "rerun pushes it" remote_has race.txt

# =====================================================================
T "D1 download --dry-run shows incoming, changes nothing"
other_commit bash -c 'mkdir -p "AI Agent Audits/round 4" && echo r4 > "AI Agent Audits/round 4/new report.md" && echo v2 > "AI Agent Audits/report one.md"'
H="$(git -C "$MINE" rev-parse HEAD)"
run d1 "$DOWN" --dry-run
check "exit 0" [ "$RC" -eq 0 ]
check "lists new file with spaces" has "AI Agent Audits/round 4/new report.md"
check "lists changed file" has "AI Agent Audits/report one.md"
check "HEAD unchanged" [ "$(git -C "$MINE" rev-parse HEAD)" = "$H" ]

T "D2 clean tree: fast-forward"
run d2 "$DOWN"
check "exit 0" [ "$RC" -eq 0 ]
check "new file arrived" [ -f "$MINE/AI Agent Audits/round 4/new report.md" ]
check "at origin/main" [ "$(git -C "$MINE" rev-parse HEAD)" = "$(remote_head)" ]
check "summary printed" has "summary: 1 new, 1 changed"

T "D3 dirty tree, non-overlapping: stash -> ff -> unstash"
other_commit bash -c 'echo more >> other_new.txt'
echo "local wip" >> "$MINE/mine_new.txt"; echo "untracked wip" > "$MINE/wip untracked.txt"
run d3 "$DOWN"
check "exit 0" [ "$RC" -eq 0 ]
check "local edit kept" grep -q "local wip" "$MINE/mine_new.txt"
check "untracked kept" [ -f "$MINE/wip untracked.txt" ]
check "remote change arrived" grep -q more "$MINE/other_new.txt"
check "stash empty" [ -z "$(git -C "$MINE" stash list)" ]

T "D4 dirty tree overlapping with remote edit: conflict reported, nothing lost"
other_commit bash -c 'printf "a\nREMOTE3\nc\n" > conflict.txt'
printf 'a\nLOCAL3\nc\n' > "$MINE/conflict.txt"
run d4 "$DOWN"
check "exit 2" [ "$RC" -eq 2 ]
check "names conflicted file" has "conflict.txt"
check "stash kept" [ -n "$(git -C "$MINE" stash list)" ]
check "local text recoverable" bash -c 'cd "$1"; git stash show -p | grep -q "+LOCAL3"' _ "$MINE"
check "backup copy exists" bash -c 'grep -rq LOCAL3 "$1/.git/download_new_backup"' _ "$MINE"
( cd "$MINE" && git checkout -q HEAD -- conflict.txt 2>/dev/null; git reset -q; git checkout -q -- . ; git stash drop -q; true )

T "D5 upstream untracks build files (the .lake cleanup) while they are modified locally: kept, no conflict"
echo "olean-rebuilt-locally" > "$MINE/lean/AIEFProofs/.lake/build/A.olean"     # lake rebuilt it
other_commit bash -c 'git rm -q --cached lean/AIEFProofs/.lake/build/A.olean && git rm -q shared.txt'
run d5 "$DOWN"
check "exit 0" [ "$RC" -eq 0 ]
check "local .olean kept with local content" grep -q rebuilt "$MINE/lean/AIEFProofs/.lake/build/A.olean"
check "olean no longer tracked" bash -c '! git -C "$1" ls-files --error-unmatch lean/AIEFProofs/.lake/build/A.olean >/dev/null 2>&1' _ "$MINE"
check "shared.txt kept on disk (untracked)" [ -f "$MINE/shared.txt" ]
check "git status clean except kept untracked" bash -c 'cd "$1"; [ -z "$(git status --porcelain --untracked-files=no)" ]' _ "$MINE"
rm -f "$MINE/shared.txt"

T "D6 --apply-deletions removes upstream-deleted files"
other_commit bash -c 'git rm -q other_new.txt'
run d6 "$DOWN" --apply-deletions
check "exit 0" [ "$RC" -eq 0 ]
check "file removed" [ ! -e "$MINE/other_new.txt" ]

T "D7 local untracked and ignored files that GitHub now adds: stop, never overwrite"
other_commit bash -c 'echo remote > collide.txt && echo remote > collide.log && git add -f collide.log'
echo "my local" > "$MINE/collide.txt"; echo "my local log" > "$MINE/collide.log"
H="$(git -C "$MINE" rev-parse HEAD)"
run d7 "$DOWN"
check "exit nonzero" [ "$RC" -ne 0 ]
check "lists both" bash -c 'printf "%s" "$1" | grep -q "collide.txt" && printf "%s" "$1" | grep -q "collide.log"' _ "$OUT"
check "local untracked untouched" grep -q "my local" "$MINE/collide.txt"
check "local ignored untouched" grep -q "my local log" "$MINE/collide.log"
check "HEAD unchanged" [ "$(git -C "$MINE" rev-parse HEAD)" = "$H" ]
mv "$MINE/collide.txt" "$ROOT/collide.txt.mine"; mv "$MINE/collide.log" "$ROOT/collide.log.mine"
run d7b "$DOWN"; check "after moving aside it downloads" [ "$RC" -eq 0 ]

T "D8 diverged: stop and explain; --rebase replays local commit"
other_commit bash -c 'echo r > remote_only.txt'
( cd "$MINE" && echo l > local_only.txt && git add local_only.txt && git commit -q -m "local only" )
run d8 "$DOWN"
check "exit nonzero" [ "$RC" -ne 0 ]
check "says diverged" has "diverged"
check "remote file not yet here" [ ! -e "$MINE/remote_only.txt" ]
run d8b "$DOWN" --rebase
check "exit 0" [ "$RC" -eq 0 ]
check "both files present" bash -c '[ -f "$1/remote_only.txt" ] && [ -f "$1/local_only.txt" ]' _ "$MINE"
check "local commit on top of remote" [ "$(git -C "$MINE" rev-parse HEAD~1)" = "$(remote_head)" ]

T "D9 diverged with conflicting commit + --rebase: stops with instructions, abort restores"
other_commit bash -c 'printf "a\nREMOTE4\nc\n" > conflict.txt'
( cd "$MINE" && printf 'a\nLOCAL4\nc\n' > conflict.txt && git commit -q -am "local conflict 4" )
H="$(git -C "$MINE" rev-parse HEAD)"
run d9 "$DOWN" --rebase
check "exit nonzero" [ "$RC" -ne 0 ]
check "abort instructions" has "git rebase --abort"
git -C "$MINE" rebase --abort >/dev/null 2>&1
check "abort restores original commit" [ "$(git -C "$MINE" rev-parse HEAD)" = "$H" ]

T "D10 nothing new"
( cd "$MINE" && git reset -q --hard origin/main )
run d10 "$DOWN"
check "exit 0 + up to date" bash -c '[ "$1" -eq 0 ] && printf "%s" "$2" | grep -q "Already up to date"' _ "$RC" "$OUT"

echo
echo "RESULT: $PASS passed, $FAIL failed"
for f in "${FAILED[@]}"; do echo "  FAILED: $f"; done
rm -rf "$ROOT"
[ "$FAIL" -eq 0 ]
