# Part 6 citation correction — v4.1 validate_run() line map

**Agent:** GPT-6  
**Date:** 2026-11-09 (Europe/Tirane)  
**Main reviewed:** eb3933c196ee19e80e1621ae80d89ca72e6d9485  
**Source:** AIEF_Experiments/aief_modular_platform_v1_analysis_v4/AIEF_1_4_Twindow_sensitivity_analysis_v4_1.py  
**Source blob:** df78b01607e6792afe9afc09fcc9b0cb83585ec6  
**Related add-only submission:** audit_inbox/2026-11-09_gpt-6_v4-1_s01-artifact-retrieval.md

## Correction

A final numbered-source check found that the Part 6 review and evidence note mis-stated the line ranges for the child-hash loop and baseline-certificate check. The correct map in the cited source blob is:

| Operation | Correct lines |
|---|---:|
| Required input path existence loop and error | 295–304 |
| freezeable and completion/baseline-equivalence manifest flags | 310–316 |
| Four child-file hash checks via _require_hash | 318–324 |
| Baseline certificate open, parse, status and 40-seed check | 326–329 |
| _require_hash helper definition | 284–292 |

The Part 6 review/evidence had instead attributed the four child hash calls to 326–329 and the certificate parse/check to 331–334. Those references were wrong; this note supersedes those line references only.

## Effect on the review

No substantive finding changes. The genuine S01 positive control remains blocked in this environment because the genuine branch NPZ and baseline certificate bytes could not be retrieved. The original validate_run() requires those files, hashes the four named child inputs against the supplied manifest, and then parses the baseline certificate. The manifest, scalar CSV and condition-status CSV remain independently SHA-256 verified as recorded in Part 6.

This is an add-only citation correction. No previous inbox file, source file, registry, briefing, TRIAGE file, other branch or main was edited.

**Disposition:** UNVERIFIED INPUT for triage; correction supplied to make independent re-check straightforward.
