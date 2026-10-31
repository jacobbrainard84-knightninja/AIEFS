# Push notes: known limitations of this upload

1. **File modes.** The files on this branch were uploaded through a tool that
   cannot set file modes, so every file it wrote is `100644` (not executable).
2. **Executable bits to restore.** These scripts need their executable bit
   restored with a real `git push` from the owner's clone:
   - Already `100644` on `main` since commit `6b49a7b` (they were `100755` before it):
     - `lean/AIEFProofs/check_lean.sh`
     - `tools/sync/download_new.sh`
     - `tools/sync/tests/run_tests.sh`
     - `tools/sync/untrack_artifacts.sh`
   - New on this branch, `100755` in local commit `487d5a9`, `100644` here:
     - `audits/engineering/verify_inventory.py`
     - `tools/ci/check_manifest.py`
     - `tools/ci/hygiene_scan.py`
     - `tools/ci/lint_claims.py`

   Fix, from a clone of this branch:

   ```
   git update-index --chmod=+x lean/AIEFProofs/check_lean.sh tools/sync/download_new.sh tools/sync/tests/run_tests.sh tools/sync/untrack_artifacts.sh audits/engineering/verify_inventory.py tools/ci/check_manifest.py tools/ci/hygiene_scan.py tools/ci/lint_claims.py
   git commit -m "Restore executable bits"
   ```

   `.github/workflows/repo-checks.yml` runs `lint_claims.py`, `hygiene_scan.py`
   and `check_manifest.py` as `python tools/ci/<script>.py`, so CI does not
   depend on the executable bit.
3. **Binaries left out.** Three binary files from `487d5a9` were not uploaded
   because the tool cannot write binary files. They are listed with size and
   SHA-256 in
   `audits/github_reconciliation/recovered_from_workspace_019ff402/zip_only_files/BINARIES_NOT_UPLOADED.md`.
4. **Line endings (CRLF -> LF).** The upload tool converted CRLF line endings
   to LF. The following files use CRLF in local commit `487d5a9`, so on this
   branch they differ from `487d5a9` **only in line endings** (verified
   byte-for-byte after stripping `\r`). Their SHA-256 on this branch therefore
   differs from the local value:
   - `audits/engineering/python_path_dependencies.csv` (local sha256 `45bf9ac1565b8264bd7fb38f85af575fadf310c395be985c26af0de24d761ab3`)
   - `audits/github_reconciliation/recovered_from_workspace_019ff402/zip_only_files/AIEF_1_4_CONTROLLER_FIBER_CLAIM_REGISTRY.csv` (local sha256 `2fb5517d31f0fba87e629e5de4c373065224fa98b0c10cfbb337318b3ae0f791`) **pinned**
   - `audits/github_reconciliation/recovered_from_workspace_019ff402/zip_only_files/AIEF_1_4_analysis_lineage.csv` (local sha256 `a633819df8a2c512d7ade3378b40e85c2288527a513b6a6d86c823b836a481a6`) **pinned**
   - `audits/github_reconciliation/runs_cohort_reconciliation.csv` (local sha256 `bcd363e0da2fdef7aeeccc7440076c0d185242b9d1af82617c49f74cb3571351`)
   - `audits/github_reconciliation/zip_vs_tree_comparison.csv` (local sha256 `c30c0736217296cb43c11837befd9a79042bbd635da4b962e460428155b217d2`)
   - `registry/artifacts.csv` (local sha256 `813c71a7c70bcffdc20ff248709f921d3de1740a8e142332a6f128009b5300fd`)
   - `registry/claims.csv` (local sha256 `b9c31612216d78c7d843f925ed4e1454e49acad81edaf6dfe85e311ef75821a6`)
   - `registry/lineage_reconciliation.csv` (local sha256 `dc4a54c9f8c7620c34f2352f33a02a9d58fa98ebf3678940ef2ec2e8e9a94271`)
   - `registry/relocation_map.csv` (local sha256 `6d6b2c42a1576df010d6b76712a2eaa015d34937278fbc9fad8f0025e237d8e9`)
   - `registry/studies.csv` (local sha256 `07ffc520afaffd2ced57fe78b295de78d483f28baab7e75119e1f8f0af76ac57`)
   - `registry/supersessions.csv` (local sha256 `6c2d83f5f7e2308d3361d2926040b770c11af4b97d892dace3117b08ede2b3b4`)

   The two files marked **pinned** have their local (CRLF) SHA-256 recorded in
   `audits/github_reconciliation/recovered_from_workspace_019ff402/PROVENANCE.json`,
   the freeze manifests in that `zip_only_files/` folder,
   `audits/github_reconciliation/zip_vs_tree_comparison.csv` and
   `registry/artifacts.csv`, so a hash check on this branch will report them as
   changed. To restore the exact bytes, check the files out from local commit
   `487d5a9` in the owner's clone and push with git (also restore CRLF in the
   other files listed above if exact bytes matter).

   Update (local branch `work/post-push-1`, commit a60b0d9): the two **pinned**
   files were restored to their original CRLF bytes from `487d5a9` and now match
   their pins; `.gitattributes` marks exactly these two paths `-text`. The other
   nine files above stay LF (unpinned; the registry build scripts now write LF).
