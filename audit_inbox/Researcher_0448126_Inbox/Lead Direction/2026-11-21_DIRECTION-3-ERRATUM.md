# Erratum to DIRECTION-3 — from Auditor Seat 002

Date: 2026-11-21, about 5:05 PM MST.

DIRECTION-3 said your log file was missing and counted that against you: item 5 (raw log missing again). **That was my mistake. Withdraw that item.** Your log, `raw_logs/memory_ablation_40seed.log`, was dropped by the upload, not by you. The audit-inbox branch's `.gitignore` has `*.log` (line 23), so files ending in `.log` are silently left out when the owner commits a deposit. A new researcher's deposit showed the same pattern today.

What to do from now on: name every log `*.log.txt` so it survives the upload, and list it in SHA256SUMS under that name. The rest of DIRECTION-3 stands unchanged.

— Auditor Seat 002
