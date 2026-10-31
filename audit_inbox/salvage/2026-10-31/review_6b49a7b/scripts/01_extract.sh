#!/usr/bin/env bash
# Read-only extraction of the new items in commit 6b49a7b. Writes only under ../scratch.
set -euo pipefail
cd "$(dirname "$0")/.."
R=repo
for f in "Origin Document.pdf" "Origin Document 01.pdf" "Origin Document 02.pdf"; do
  b="${f%.pdf}"; b="${b// /_}"
  pdfinfo "$R/Project Origins/$f" > "scratch/pdf/$b.info.txt"
  pdftotext -layout "$R/Project Origins/$f" "scratch/pdf/$b.txt"
done
for z in "$R"/"Project Histories"/workspace-019fb8fc*.zip "$R"/"Project Histories"/workspace-019fc7dc*.zip "$R"/"Project Histories"/workspace-019ff425*.zip; do
  n=$(basename "$z" .zip)
  rm -rf "scratch/zips/$n"; mkdir -p "scratch/zips/$n"
  unzip -l "$z" > "scratch/zips/$n.listing.txt"
  unzip -q "$z" -d "scratch/zips/$n"
done
