#!/bin/bash
# usage: check.sh pre <expected_head>   |  check.sh post <expected_parent> <path>...
cd /workspace/v4/r4b || exit 9
timeout 90 git fetch -q origin main || { echo "FETCH FAILED"; exit 8; }
H=$(git rev-parse origin/main)
if [ "$1" = pre ]; then
  [ "$H" = "$(git rev-parse $2)" ] && echo "PRE OK main=$H" || { echo "MAIN MOVED: $H"; exit 1; }
  exit 0
fi
P=$(git rev-parse origin/main^); exp=$(git rev-parse $2)
[ "$P" = "$exp" ] && echo "parent OK" || { echo "UNEXPECTED PARENT $P"; exit 1; }
echo "new head $H"; shift 2; rc=0
for f in "$@"; do
  if [ -e "$f" ]; then
    r=$(git rev-parse "origin/main:$f" 2>/dev/null); l=$(git hash-object "$f")
    m=$(git ls-tree origin/main -- "$f" | awk '{print $1}')
    s1=$(git cat-file -p "origin/main:$f" | sha256sum | cut -c1-64); s2=$(sha256sum < "$f" | cut -c1-64)
    cr=$(git cat-file -p "origin/main:$f" | grep -c $'\r')
    [ "$r" = "$l" ] && [ "$s1" = "$s2" ] && [ "$cr" = 0 ] && echo "OK $m ${s1:0:12} $f" || { echo "MISMATCH $m $f remote=$r local=$l"; rc=1; }
  else
    git cat-file -e "origin/main:$f" 2>/dev/null && { echo "STILL PRESENT $f"; rc=1; } || echo "DELETED OK $f"
  fi
done
git diff --name-only origin/main^ origin/main | sed 's/^/changed: /'
exit $rc
