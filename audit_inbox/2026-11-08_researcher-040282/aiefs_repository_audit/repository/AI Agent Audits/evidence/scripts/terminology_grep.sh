#!/usr/bin/env bash
# Run from the AIEFS repo root. Counts files / hits for key terms in non-PDF tracked text (point 11).
for t in cocycle Duhamel lineality biorthogonal "controller fiber" "spectral gap" Bregman projection Ehresmann holonomy "fiber bundle" gauge; do
  f=$(git grep -I -i -l -e "$t" -- ':!*.pdf' | wc -l); h=$(git grep -I -i -o -e "$t" -- ':!*.pdf' | wc -l)
  echo "$t: files=$f hits=$h"
done
echo "gauge occurrences:"; git grep -I -i -n -e gauge -- ':!*.pdf' | cut -c1-120
