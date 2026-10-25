# Where the 18-coordinate "unique slow pole" result is cited (round 4, 2026-10-25)

Prepared for the owner. Nothing listed here was edited. Editing source scripts, generated reports and manuscripts is the owner's decision (AIEFS_audit_response_3.md, Part C).
Search: `rg -n -i "slow pole|EMA pole|unique slow|augmented spectr|18 fundamental|18-dim|18×18|18x18|fundamental.state"` over the tracked text files. The PDF/ODT manuscripts and histories were searched with `pdftotext -layout` / `unzip -p content.xml`. Line numbers for PDFs are `pdftotext -layout` output lines.

## A. The claim itself (generated report / manifest, at repo commit dc0250a)
| file:line | text |
|---|---|
| aief_1_4_augmented_spectrum/augmented_spectrum_report.txt:28 | "The EMA pole alpha IS the unique slow pole of the true augmented dynamics on this replay." |
| aief_1_4_augmented_spectrum/augmented_spectrum_report.txt:2 | "Augmented Spectral Audit (v2 — Fundamental-State Restriction)" |
| aief_1_4_augmented_spectrum/analysis_manifest.json:12, :18 | "h_old(3) + B(3) + C(12) = 18 fundamental vars"; "alpha is unique slow pole" |
| aief_1_4_augmented_spectrum.py:20-25, :115, :350, :417, :421 | docstring ("theta ... is derived from the phase_factor"; "If no eigenvalue ... alpha is the unique slow pole"), verdict text, manifest strings |
| Older files/aief_1_4_augmented_spectrum.py:22, :329 and Older files/aief_1_4_augmented_spectrum_02.py:25, :344 | earlier copies of the same verdict |

## B. Scripts that reuse the same 18-coordinate map (same `restore_state` without theta)
| file:line | note |
|---|---|
| aief_1_4_slow_eigenvector_analysis.py:6, :97, :530 | "Builds the 18x18 augmented Jacobian (fundamental-state restriction ...)"; restore_state omits theta |
| aief_1_4_slow_subspace_projection.py:6, :83, :200 | 18x18 Jacobian and EMA-cluster projector; restore_state omits theta |
| aief_1_4_operator_compression.py:90, :202-240 | 18x18 Jacobian, slow projector; restore_state omits theta |
| aief_1_4_observable_jacobian.py:7, :93, :210, :390 | observables differentiated w.r.t. "the 18 fundamental" variables; restore_state omits theta |
| aief_1_4_multiseed_geometry.py:90, :201 | 18x18 Jacobian per perturbation level; restore_state omits theta |
| aief_1_4_observable_jacobian/observable_jacobian_report.txt:10 | generated report |
| aief_1_4_slow_eigenvector_analysis/analysis_manifest.json:11 | generated manifest |
| Older files/aief_1_4_multiseed_geometry_{02,03,05,08,1,10,11}.py, Older files/aief_1_4_slow_subspace_projection{,_01}.py | older copies |

## C. A related but separate claim (different script, not the 18-coordinate map)
| file:line | text |
|---|---|
| aief_1_4_transverse_phase_jacobian/transverse_jacobian_report.txt:74-75 | "The EMA pole is the bottleneck. All downstream observables inherit r_EMA = 0.057133 from the single slow transverse mode." The corrected full-state run (results/full_state_spectrum.json) also contradicts "single slow mode". |

## D. Manuscripts / histories (PDF; owner-controlled; possible PII/copyright scope, not edited)
| file:line | note |
|---|---|
| Project Histories/Project Lead History 04.pdf:28923-29057 | the pasted v2 report, including "The EMA pole alpha IS the unique slow pole" (:28978) |
| Project Histories/Project Lead History 04.pdf:27208-27406, :28001, :30213-30543, :31011, :31176, :31512-31838, :31985-31986, :32102, :32691-32832, :35025 | review text that already says the 18-dimensional state is not closed and recommends quarantine/retirement of "unique slow pole" |
| Project Histories/Project Lead History 07.pdf:300-316 | "Spectral material quarantine" list, including "alpha is the unique slow pole of the full dynamics" |
| Project Histories/Project Lead History 10.pdf:7834 | "EMA pole" listed among accumulated maps |
| Results.pdf | no hit |

No hit in any tracked .md file outside "AI Agent Audits/".
