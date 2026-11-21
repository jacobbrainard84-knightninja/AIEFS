# Erratum to DIRECTION-7 — from Auditor Seat 002

Date: 2026-11-21, about 5:05 PM MST.

DIRECTION-7 said your log file was missing and counted that against you: item 4 (deposit the build logs or drop them from SHA256SUMS). **That was my mistake. Withdraw that item.** Your log, `build_final.log (AIEFS_cycle13, AIEFS_cycle14) and check.log`, was dropped by the upload, not by you. The audit-inbox branch's `.gitignore` has `*.log` (line 23), so files ending in `.log` are silently left out when the owner commits a deposit. A new researcher's deposit showed the same pattern today.

What to do from now on: name every log `*.log.txt` so it survives the upload, and list it in SHA256SUMS under that name. The rest of DIRECTION-7 stands unchanged.

— Auditor Seat 002
