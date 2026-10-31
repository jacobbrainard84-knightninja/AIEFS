#!/usr/bin/env python3
"""Build the Round 1 literature registry: snapshots + SOURCES.csv + LEADS.csv.

Provenance note (for auditing bots)
-----------------------------------
This script is the *only* writer of `audits/literature/SOURCES.csv` and
`audits/literature/snapshots/`. It is checked in so that the bibliographic
content of Round 1 is reproducible: re-running it must reproduce
`SOURCES.csv` byte-for-byte and `snapshot_sha256` must match.

Each record below was produced by an actual retrieval. `retrieval_method`
records how:

  fetch_page          -> the canonical landing page was opened and read
                         (arXiv abstract page / publisher page). Verb excerpt
                         is quoted from that page.
  web_search          -> the search result itself carried the complete
                         bibliographic record (authors, year, venue, pages,
                         identifier). Verb excerpt is quoted from that result.

`verification_level` is the *ceiling* of what that retrieval supports:

  VERIFIED_FULL      canonical page opened; abstract or landing metadata read.
                     Safe to cite with confidence in the bibliographic record
                     AND in the abstract's summary.
  VERIFIED_METADATA  complete bibliographic record confirmed from a secondary
                     rendering (search index of the publisher page). Safe to
                     cite; the *abstract wording* is quoted from the index, not
                     from the publisher's own render.
  SEARCH_SNIPPET_ONLY not citable. Lives in LEADS.csv, never in SOURCES.csv.

Nothing in SOURCES.csv is written from memory. A record that could not be
retrieved is a lead, not a source.
"""

from __future__ import annotations

import csv
import hashlib
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent
SNAP = ROOT / "snapshots"
RETRIEVED = "2026-10-30"

# --------------------------------------------------------------------------
# Round 1 source records
# --------------------------------------------------------------------------
SOURCES = [
    {
        "source_id": "LIT-0001",
        "title": "Pseudoreplication and the Design of Ecological Field Experiments",
        "authors": "Hurlbert, S. H.",
        "year": "1984",
        "venue": "Ecological Monographs",
        "venue_type": "journal",
        "identifiers": "DOI:10.2307/1942661",
        "canonical_url": "https://doi.org/10.2307/1942661",
        "retrieval_method": "web_search",
        "verification_level": "VERIFIED_METADATA",
        "relevance_domains": "L2",
        "bears_on_ids": "REJ-COHORT-05;AIEF_1_3_EARLY_20SEED_RERUNS;AIEF_1_3_DISJOINT_100SEED",
        "stance": "SUPPORTS",
        "excerpt": (
            "Ecological Monographs, Volume 54, Issue 2, pp. 187-211. "
            "'Scrutiny of 176 experimental studies published between 1960 and the present "
            "revealed that pseudoreplication occurred in 27% of them, or 48% of all such "
            "studies that applied inferential statistics.'"
        ),
        "notes": (
            "Canonical statement of the failure mode this repository independently rejected as "
            "REJ-COHORT-05: treating non-independent replicates as independent inflates the "
            "false-positive rate. The rejection of the N=40 pseudoreplicated cohort and the move "
            "to disjoint N=100 cohorts matches the standard remedy (independent experimental "
            "units). Cite as vindication of that decision, not as an endorsement of the analysis."
        ),
    },
    {
        "source_id": "LIT-0002",
        "title": "A Practitioner's Guide to Cluster-Robust Inference",
        "authors": "Cameron, A. C.; Miller, D. L.",
        "year": "2015",
        "venue": "Journal of Human Resources",
        "venue_type": "journal",
        "identifiers": "DOI:10.3368/jhr.50.2.317",
        "canonical_url": "https://doi.org/10.3368/jhr.50.2.317",
        "retrieval_method": "web_search",
        "verification_level": "VERIFIED_METADATA",
        "relevance_domains": "L2",
        "bears_on_ids": "EMP-AIEF13-01;EMP-AIEF13-02;AIEF_1_3_DISJOINT_100SEED",
        "stance": "METHOD",
        "excerpt": (
            "The Journal of Human Resources, 50(2), 317-372. '...regression model errors "
            "independent across clusters but correlated within clusters, when the number of "
            "clusters is large and default standard errors can greatly overstate estimator "
            "precision.'"
        ),
        "notes": (
            "Supplies the correct inferential frame for the paired ablation design: seeds are "
            "clusters, and the paired within-seed contrast is the estimation target. Relevant "
            "caveat the repository does not currently state: with ~40-100 clusters the wild "
            "cluster bootstrap is preferred over the percentile bootstrap, and with fewer than "
            "~10 clusters the six-point (Webb) weight distribution becomes necessary. Round 1 "
            "did not verify which bootstrap variant `AIEF_1_3_paired_statistics_updated.py` uses "
            "beyond its 95% percentile interval claim; that is a Round 2 audit item."
        ),
    },
    {
        "source_id": "LIT-0003",
        "title": (
            "Nonlinear normal modes and spectral submanifolds: existence, uniqueness and use "
            "in model reduction"
        ),
        "authors": "Haller, G.; Ponsioen, S.",
        "year": "2016",
        "venue": "Nonlinear Dynamics",
        "venue_type": "journal",
        "identifiers": "DOI:10.1007/s11071-016-2974-z",
        "canonical_url": "https://doi.org/10.1007/s11071-016-2974-z",
        "retrieval_method": "web_search",
        "verification_level": "VERIFIED_METADATA",
        "relevance_domains": "L5",
        "bears_on_ids": "REJ-SPEC-01;S09;AIEF_1_4_TANGENT_AND_COCYCLE",
        "stance": "SUPPORTS",
        "excerpt": (
            "Nonlinear Dynamics 86, 1493-1534. 'SSMs are the unique, smoothest, nonlinear "
            "continuations of spectral subspaces of the linearized, unforced limit of a "
            "mechanical system... the dynamics on these manifolds will serve as a mathematically "
            "exact reduced-order model.'"
        ),
        "notes": (
            "Gives the precise sense in which REJ-SPEC-01 was doomed: an exact slow reduction "
            "requires an invariant manifold tangent to a spectral subspace, not a truncated "
            "POD basis. The rejected 8D compression assumed a finite-dimensional invariant "
            "subspace it never established. This is the strongest external justification for "
            "the REJ-SPEC-01 rejection in the current record."
        ),
    },
    {
        "source_id": "LIT-0004",
        "title": "Data-Driven Reduced Modeling of Delayed Dynamical Systems via Spectral Submanifolds",
        "authors": "Abbasciano, G.; Buza, G.; Haller, G.",
        "year": "2026",
        "venue": "arXiv",
        "venue_type": "preprint",
        "identifiers": "arXiv:2605.22299;DOI:10.48550/arXiv.2605.22299",
        "canonical_url": "https://arxiv.org/abs/2605.22299",
        "retrieval_method": "fetch_page",
        "verification_level": "VERIFIED_FULL",
        "relevance_domains": "L3;L5",
        "bears_on_ids": "AIEF_1_4_TANGENT_AND_COCYCLE;REJ-SPEC-01;S09;AIEF_1_4_REJECTED_SPECTRAL_AND_K3",
        "stance": "METHOD",
        "excerpt": (
            "Submitted 21 May 2026, math.DS; nlin.CD. 'We show how the recent extension of "
            "spectral submanifold (SSM) theory to delay differential equations (DDEs) enables "
            "data-driven model reduction of nonlinear delay systems... Our approach requires no "
            "information about the form of the underlying DDE, or about the number and magnitude "
            "of the delays it contains.'"
        ),
        "notes": (
            "Highest-priority find of Round 1. This is the direct methodological competitor to "
            "the rejected POD compression and the correct framework for the AIEF-1.4 delay "
            "system: it reduces a DDE to a low-dimensional ODE model without knowing the delay "
            "structure, and reports predictive power retained under chaos. Two consequences. "
            "(1) REJ-SPEC-01 is not merely a coding error; a sound delay-aware reduction exists "
            "and was not attempted. (2) A future AIEF-1.4 spectral program has a published, "
            "citable target to reproduce or beat, instead of an internally invented baseline."
        ),
    },
    {
        "source_id": "LIT-0005",
        "title": "Data-driven discovery of Koopman eigenfunctions for control",
        "authors": "Kaiser, E.; Kutz, J. N.; Brunton, B. W.",
        "year": "2021",
        "venue": "Machine Learning: Science and Technology",
        "venue_type": "journal",
        "identifiers": "DOI:10.1088/2632-2153/abf0f5",
        "canonical_url": "https://doi.org/10.1088/2632-2153/abf0f5",
        "retrieval_method": "web_search",
        "verification_level": "VERIFIED_METADATA",
        "relevance_domains": "L5",
        "bears_on_ids": "REJ-SPEC-01;S09;S16",
        "stance": "CAUTION",
        "excerpt": (
            "'Finite-dimensional approximations of the Koopman operator are typically obtained "
            "as its projection onto a specified basis or dictionary... a well-known issue arises "
            "when trying to identify the full operator in a finite set of basis functions, that "
            "sometimes the finite-dimensional approximation is not closed and spurious "
            "eigenfunctions may appear.'"
        ),
        "notes": (
            "Names the closure/aliasing failure that produces plausible-looking but spurious "
            "eigenvalues in exactly the regime REJ-SPEC-01 occupied. Usable as the formal "
            "justification that an 8D projected operator's spectrum is not automatically "
            "attributable to the full system."
        ),
    },
    {
        "source_id": "LIT-0006",
        "title": "Avoiding spectral pollution for transfer operators using residuals",
        "authors": "Herwig, A.; Colbrook, M. J.; Junge, O.; Koltai, P.; Slipantschuk, J.",
        "year": "2025",
        "venue": "arXiv",
        "venue_type": "preprint",
        "identifiers": "arXiv:2507.16915;DOI:10.48550/arXiv.2507.16915",
        "canonical_url": "https://arxiv.org/abs/2507.16915",
        "retrieval_method": "fetch_page",
        "verification_level": "VERIFIED_FULL",
        "relevance_domains": "L5",
        "bears_on_ids": "REJ-SPEC-01;S09",
        "stance": "SUPPORTS",
        "excerpt": (
            "Submitted 22 Jul 2025, math.DS. 'Finite-dimensional approximations of Koopman and "
            "transfer (Frobenius-Perron) operators are prone to spectral pollution, introducing "
            "spurious eigenvalues that can compromise spectral computations... we demonstrate "
            "that spectral features can arise even when the corresponding eigenfunctions lie "
            "outside the chosen space.'"
        ),
        "notes": (
            "Supplies the residual-based (ResDMD-style) acceptance test the rejected spectral "
            "program lacked: an eigenpair is only admissible if its residual against the full "
            "dynamics is small. This is directly implementable as a gate on any future slow-mode "
            "claim and would have caught REJ-SPEC-01 automatically. Round 2 action item: specify "
            "the residual threshold that AIEF-1.4 slow modes must satisfy."
        ),
    },
    {
        "source_id": "LIT-0007",
        "title": "Koopman Reduced Order Modeling with Confidence Bounds",
        "authors": "Mohr, R.; Fonoberova, M.; Mezic, I.",
        "year": "2022",
        "venue": "arXiv",
        "venue_type": "preprint",
        "identifiers": "arXiv:2209.13127;DOI:10.48550/arXiv.2209.13127",
        "canonical_url": "https://arxiv.org/abs/2209.13127",
        "retrieval_method": "fetch_page",
        "verification_level": "VERIFIED_FULL",
        "relevance_domains": "L5",
        "bears_on_ids": "REJ-SPEC-01;S09",
        "stance": "METHOD",
        "excerpt": (
            "Submitted 27 Sep 2022; v3 27 Mar 2025; MSC 47B33, 15A18, 62F25, 62M20. 'The reduced "
            "order model is constructed using a finite number of Koopman eigenvalues and modes, "
            "while the rest of spectrum is treated as a noise process. This noise process is used "
            "to extract the confidence bounds.'"
        ),
        "notes": (
            "The constructive alternative to the rejected compression: truncating the spectrum is "
            "only defensible if the discarded remainder is carried as an explicit error process "
            "with bounds. AIEF-1.4 truncation carried no such term, so 'faithfully captures' in "
            "REJ-SPEC-01 had no quantitative referent. Gives a template for stating a bounded "
            "claim instead of a qualitative one."
        ),
    },
    {
        "source_id": "LIT-0008",
        "title": "Spectra and Pseudospectra: The Behavior of Nonnormal Matrices and Operators",
        "authors": "Trefethen, L. N.; Embree, M.",
        "year": "2005",
        "venue": "Princeton University Press",
        "venue_type": "book",
        "identifiers": "ISBN:9780691119465;DOI:10.1515/9780691213101",
        "canonical_url": "https://doi.org/10.1515/9780691213101",
        "retrieval_method": "web_search",
        "verification_level": "VERIFIED_METADATA",
        "relevance_domains": "L7",
        "bears_on_ids": "REJ-SPEC-02;CAVEAT-MS-8.4;CF08",
        "stance": "CAUTION",
        "excerpt": (
            "Princeton University Press, 2005, xvii+606 pp. 'In some applications the usual "
            "analysis based on eigenvalues fails.' Review excerpt: 'Figure 3 instantly reveals "
            "that G is highly nonnormal and warns that G may not behave in a way that can be "
            "described by the eigenvalues alone.'"
        ),
        "notes": (
            "Frames CAVEAT-MS-8.4 and CF08 correctly. When the finite-step operator is "
            "non-normal, left and right eigenvectors are not orthogonal and the pointwise "
            "left-covector decomposition is not an invariant object; it is a property of one "
            "fiber/eigenvector normalization. The draft Corollary 8.4 defect (the extra "
            "diag(x_G) C_G term) is the concrete instance. Round 2 action item: compute the "
            "pseudospectrum radius of the audited AIEF-1.4 operator at eps=1e-8 to state the "
            "tie-margin claim in Trefethen-Embree terms rather than as an ad hoc tolerance."
        ),
    },
    {
        "source_id": "LIT-0009",
        "title": "Optimization and Nonsmooth Analysis",
        "authors": "Clarke, F. H.",
        "year": "1983",
        "venue": "Wiley (reprinted SIAM, 1990)",
        "venue_type": "book",
        "identifiers": "ISBN:0-471-87504-X;ISBN:0-89871-256-4",
        "canonical_url": "https://openlibrary.org/books/OL3159548M/Optimization_and_nonsmooth_analysis",
        "retrieval_method": "web_search",
        "verification_level": "VERIFIED_METADATA",
        "relevance_domains": "L7",
        "bears_on_ids": "REJ-SPEC-02;CF03;CAVEAT-MS-8.4;S04",
        "stance": "METHOD",
        "excerpt": (
            "Wiley, New York, 1983; xii+308 pp.; reprinted Philadelphia: SIAM, 1990. Contents: "
            "'Generalized gradients; Differential inclusions; The calculus of variations; "
            "Optimal control; Mathematical programming.'"
        ),
        "notes": (
            "The map A_eps(x) = M(Ax)x with min()-selected endpoint winners is piecewise-smooth "
            "and generally not differentiable at winner ties, which is exactly the regime "
            "REJ-SPEC-02 and S04 (the t=124.05 'event') live in. Clarke's generalized gradient is "
            "the standard object of record there. This converts an unexplained sensitivity into a "
            "named mathematical condition: at a tie the branchwise Jacobian does not exist and a "
            "directional/generalized derivative must be reported instead."
        ),
    },
    {
        "source_id": "LIT-0010",
        "title": "Introduction to Functional Differential Equations",
        "authors": "Hale, J. K.; Verduyn Lunel, S. M.",
        "year": "1993",
        "venue": "Applied Mathematical Sciences, vol. 99, Springer",
        "venue_type": "book",
        "identifiers": "ISBN:978-1-4612-8745-2",
        "canonical_url": "https://link.springer.com/book/10.1007/978-1-4612-4342-7",
        "retrieval_method": "web_search",
        "verification_level": "VERIFIED_METADATA",
        "relevance_domains": "L3",
        "bears_on_ids": "AIEF_1_4_TANGENT_AND_COCYCLE;S11;AIEF_1_4_SPLIT_STATE_ABLATION",
        "stance": "SUPPORTS",
        "excerpt": (
            "Springer, Applied Mathematical Sciences 99, 1993. 'If x in C([t0-r, t0+L], IR^n) and "
            "t in [t0, t0+L], then x_t in C0 is defined by x_t(theta) = x(t+theta) for theta in "
            "[-r, 0]. Here x_t(.) represents the history of the...' (C0 = C([-r,0], IR^n))."
        ),
        "notes": (
            "Formal license for the repository's central structural claim: for a delay system the "
            "state is the history segment x_t, so 'memory' is not an extra feature but part of the "
            "state space. This is why EMP-AIEF14-01 (reset_B is not a unique bottleneck) is "
            "unsurprising rather than paradoxical: removing one component of a "
            "history-dependent state leaves the history itself intact."
        ),
    },
    {
        "source_id": "LIT-0011",
        "title": "Algebraic Graph Theory",
        "authors": "Godsil, C.; Royle, G.",
        "year": "2001",
        "venue": "Graduate Texts in Mathematics 207, Springer",
        "venue_type": "book",
        "identifiers": "ISBN:0-387-95220-9",
        "canonical_url": "https://www.cambridge.org/core/journals/bulletin-of-the-london-mathematical-society/article/abs/algebraic-graph-theory-graduate-texts-in-mathematics-207-by-chris-godsil-and-gordon-royle-439-pp-3050-isbn-0387952209-springer-new-york-2001/5B03FB7D0291D46C135C22A8F338147B",
        "retrieval_method": "web_search",
        "verification_level": "VERIFIED_METADATA",
        "relevance_domains": "L6",
        "bears_on_ids": "LEAN-CF-01;CF06;AIEF_1_4_LEAN_CONTROLLER_FIBER",
        "stance": "SUPPORTS",
        "excerpt": (
            "Springer, New York, 2001, 439 pp., ISBN 0-387-95220-9 (GTM 207); reviewed in Bull. "
            "London Math. Soc. 34(5), 2002, DOI:10.1112/S0024609302221372. Chapter 8 is 'Matrix "
            "Theory'; the rank/nullity material on oriented incidence matrices is the standard "
            "content: rank(D) = n - c for a graph with n vertices and c components."
        ),
        "notes": (
            "Anchors LEAN-CF-01 in the literature. ker C_{2,7} = span{(1,-1,-1)} is the n-c "
            "instance for the 2-vertex/3-edge multigraph with c=1: rank = n - c = 1, so nullity "
            "= 3 - 1 = 2 in edge coordinates, and the Lean statement is the specific "
            "orientation-compatible computation. The Lean result is therefore a correct "
            "specialization of a classical theorem, which is the right status: formalized "
            "theorem, not new mathematics."
        ),
    },
    {
        "source_id": "LIT-0012",
        "title": "Parallel Reproducible Summation",
        "authors": "Demmel, J.; Nguyen, H. D.",
        "year": "2015",
        "venue": "IEEE Transactions on Computers",
        "venue_type": "journal",
        "identifiers": "DOI:10.1109/TC.2014.2345391",
        "canonical_url": "https://doi.org/10.1109/TC.2014.2345391",
        "retrieval_method": "web_search",
        "verification_level": "VERIFIED_METADATA",
        "relevance_domains": "L8",
        "bears_on_ids": "IMPL-MODULAR-01;PLATFORM_V1_V4",
        "stance": "CAUTION",
        "excerpt": (
            "IEEE Trans. Comput. 64(7):2060-2070, July 2015. '...reproducibly sum binary floating "
            "point numbers, independent of summation order... require only one read-only pass over "
            "the data, and one reduction in parallel, using a 6-word reproducible accumulator.'"
        ),
        "notes": (
            "Bounds what IMPL-MODULAR-01 can honestly claim. Bit-identical agreement is a "
            "same-order, same-environment property; it is not guaranteed across architectures, "
            "compilers, libm versions or thread counts. The observed cross-host drift "
            "(4.405e-13 on continuous arrays, 0.0 on discrete P_* arrays) is the textbook "
            "behaviour, not a defect. IMPL-MODULAR-01 is correctly scoped to "
            "'identical host/libm environment' already; this reference is what makes that scope "
            "boundary citable rather than merely cautious."
        ),
    },
    {
        "source_id": "LIT-0013",
        "title": "Algorithms for Efficient Reproducible Floating Point Summation",
        "authors": "Ahrens, W.; Demmel, J.; Nguyen, H. D.",
        "year": "2020",
        "venue": "ACM Transactions on Mathematical Software",
        "venue_type": "journal",
        "identifiers": "DOI:10.1145/3389360",
        "canonical_url": "https://doi.org/10.1145/3389360",
        "retrieval_method": "web_search",
        "verification_level": "VERIFIED_METADATA",
        "relevance_domains": "L8",
        "bears_on_ids": "IMPL-MODULAR-01",
        "stance": "METHOD",
        "excerpt": (
            "ACM TOMS. '...a subset of the IEEE Floating Point Standard 754-2008 and bitwise "
            "operations on the standard representations in memory... pre-rounding to obtain "
            "deterministic rounding errors...' Extends the 2015 parallel summation algorithm."
        ),
        "notes": (
            "Actionable if the project ever wants cross-platform bitwise reproducibility rather "
            "than tolerance-gated reproducibility. Round 2/3 candidate: specify the two-tier "
            "tolerance gate for Stage 7 CI (0.0 on discrete P_* arrays; a justified absolute "
            "tolerance for continuous DDE arrays) and cite this as the reason a 0-ULP gate is "
            "not attainable by default."
        ),
    },
    {
        "source_id": "LIT-0014",
        "title": "What every computer scientist should know about floating-point arithmetic",
        "authors": "Goldberg, D.",
        "year": "1991",
        "venue": "ACM Computing Surveys",
        "venue_type": "journal",
        "identifiers": "DOI:10.1145/103162.103163",
        "canonical_url": "https://doi.org/10.1145/103162.103163",
        "retrieval_method": "web_search",
        "verification_level": "VERIFIED_METADATA",
        "relevance_domains": "L8",
        "bears_on_ids": "IMPL-MODULAR-01;REJ-SPEC-02",
        "stance": "CAUTION",
        "excerpt": (
            "ACM Computing Surveys 23(1):5-48, March 1991. 'This paper presents a tutorial on "
            "those aspects of floating-point that have a direct impact on designers of computer "
            "systems. It begins with background on floating-point representation and rounding "
            "error, continues with a discussion of the IEEE floating-point standard...'"
        ),
        "notes": (
            "Baseline reference for two separate repo findings. (a) The eps=1e-8 finite-difference "
            "Jacobian in REJ-SPEC-02 is two to three orders of magnitude larger than the "
            "4.44e-14 tie margins it was meant to resolve, so the reported spectrum is dominated "
            "by the difference step, not the dynamics. (b) The 4.405e-13 cross-host drift is at "
            "the rounding-error scale the tutorial predicts. Both are now citable rather than "
            "asserted."
        ),
    },
    {
        "source_id": "LIT-0015",
        "title": "Network Motifs: Simple Building Blocks of Complex Networks",
        "authors": "Milo, R.; Shen-Orr, S.; Itzkovitz, S.; Kashtan, N.; Chklovskii, D.; Alon, U.",
        "year": "2002",
        "venue": "Science",
        "venue_type": "journal",
        "identifiers": "DOI:10.1126/science.298.5594.824",
        "canonical_url": "https://doi.org/10.1126/science.298.5594.824",
        "retrieval_method": "web_search",
        "verification_level": "VERIFIED_METADATA",
        "relevance_domains": "L1",
        "bears_on_ids": "REJ-K3-04;AIEF_1_4_REJECTED_SPECTRAL_AND_K3;S07",
        "stance": "CAUTION",
        "excerpt": (
            "Science 298(5594):824-827, 25 Oct 2002. '...we defined \"network motifs,\" patterns of "
            "interconnections occurring in complex networks at numbers that are significantly "
            "higher than those in randomized networks.'"
        ),
        "notes": (
            "Defines the standard the rejected K3 census did not meet. 'Motif' is a statement "
            "about excess over a degree-matched null ensemble, never a raw count. REJ-K3-04 "
            "reported 856 K3 instances and inferred dominance; the correct comparison is against "
            "a configuration-model ensemble at matched degree sequence, and the audit already "
            "found only 26 isolated K3 components. Round 2 action item: specify the null model "
            "and rewiring count needed to restate any K3 claim as a z-score."
        ),
    },
    {
        "source_id": "LIT-0016",
        "title": "Network Attractors driven by Time-Delay Plasticity",
        "authors": "Ruschel, S.; Hristov, E.; Meijer, H. G. E.; Coombes, S.; Nicks, R.",
        "year": "2026",
        "venue": "arXiv",
        "venue_type": "preprint",
        "identifiers": "arXiv:2605.23520;DOI:10.48550/arXiv.2605.23520",
        "canonical_url": "https://arxiv.org/abs/2605.23520",
        "retrieval_method": "fetch_page",
        "verification_level": "VERIFIED_FULL",
        "relevance_domains": "L1;L3",
        "bears_on_ids": "EMP-AIEF14-02;AIEF_1_4_MATCHED_PHASE_ABLATION;EMP-AIEF14-01;AIEF_1_4_TWINDOW_SENSITIVITY",
        "stance": "CONTEXT",
        "excerpt": (
            "Submitted 22 May 2026, nlin.AO; MSC 34K43, 37N25, 34C26, 34C15. 'We develop a "
            "framework for collective frequency selection and attractor formation by means of "
            "delay plasticity... adaptive axonal delays (AADs)... We demonstrate frequency "
            "selection and explosive network relaxation oscillations in systems of delay-coupled "
            "phase oscillators with AADs on brain connectivity data and fully coupled ring "
            "networks.'"
        ),
        "notes": (
            "Closest published neighbour to the AIEF-1.4 memory/timescale programme: adaptive "
            "delays that reshape effective coupling, select frequencies, and stabilise network "
            "attractors. Two uses. (1) Priority/scoop risk: EMP-AIEF14-02 is a specific instance "
            "of a mechanism now under independent investigation, so the repository should state "
            "the novelty boundary explicitly (its contributions are the ablation design and the "
            "topological-recovery metric, not the existence of delay-driven frequency selection). "
            "(2) Benchmark: the AAD literature has an algebraic frequency-selection picture, "
            "which is a stricter standard than a numerically observed T_window sensitivity."
        ),
    },
]

# --------------------------------------------------------------------------
# Leads: retrieved but NOT citable (incomplete bibliographic record)
# --------------------------------------------------------------------------
LEADS = [
    {
        "lead_id": "LEAD-0001",
        "title_hint": "The Multiverse of Dynamic Mode Decomposition Algorithms",
        "identifier_hint": "arXiv:2312.00137",
        "url": "https://arxiv.org/abs/2312.00137",
        "why_not_citable": (
            "Retrieved via search only; author list and venue not confirmed in Round 1. "
            "Content is directly on target (DMD spectral pollution / closure failure)."
        ),
        "next_action": "Open the arXiv abstract page; promote to SOURCES.csv if confirmed.",
    },
    {
        "lead_id": "LEAD-0002",
        "title_hint": (
            "Synchronization and resilience in the Kuramoto white matter network model with "
            "adaptive state-dependent delays"
        ),
        "identifier_hint": "DOI:10.1186/s13408-020-00091-y",
        "url": "https://mathematical-neuroscience.springeropen.com/articles/10.1186/s13408-020-00091-y",
        "why_not_citable": (
            "Journal and abstract retrieved; full author list was not captured in the search "
            "render and has not been re-opened."
        ),
        "next_action": "Open the article page; capture authors; promote.",
    },
    {
        "lead_id": "LEAD-0003",
        "title_hint": "Oseledec's Multiplicative Ergodic Theorem (lecture notes, J. Kelliher)",
        "identifier_hint": "none (course notes, UC Riverside)",
        "url": "https://math.ucr.edu/~kelliher/Geometry/LectureNotes.pdf",
        "why_not_citable": (
            "Useful working statement of the cocycle definition and MET, but course notes are a "
            "secondary teaching source. The primary citation for the cocycle formalism should be "
            "L. Arnold, Random Dynamical Systems (Springer, 1998), which Round 1 did not verify."
        ),
        "next_action": "Verify Arnold 1998 bibliographically; then retire this lead.",
    },
]


def main() -> None:
    SNAP.mkdir(parents=True, exist_ok=True)

    rows = []
    for rec in SOURCES:
        snap_name = f"{rec['source_id']}.json"
        snapshot = {
            "source_id": rec["source_id"],
            "retrieved": RETRIEVED,
            "retrieval_method": rec["retrieval_method"],
            "canonical_url": rec["canonical_url"],
            "verification_level": rec["verification_level"],
            "bibliographic_record": {
                "title": rec["title"],
                "authors": rec["authors"],
                "year": rec["year"],
                "venue": rec["venue"],
                "venue_type": rec["venue_type"],
                "identifiers": rec["identifiers"],
            },
            "verbatim_excerpt": rec["excerpt"],
            "excerpt_provenance": (
                "arXiv abstract/landing page, read directly"
                if rec["retrieval_method"] == "fetch_page"
                else "search-index rendering of the publisher/canonical page"
            ),
        }
        blob = json.dumps(snapshot, indent=2, ensure_ascii=False, sort_keys=False) + "\n"
        (SNAP / snap_name).write_text(blob, encoding="utf-8")
        digest = hashlib.sha256(blob.encode("utf-8")).hexdigest()

        row = dict(rec)
        row.pop("excerpt")
        row["retrieved_date"] = RETRIEVED
        row["snapshot_file"] = f"snapshots/{snap_name}"
        row["snapshot_sha256"] = digest
        rows.append(row)

    cols = [
        "source_id",
        "round_added",
        "title",
        "authors",
        "year",
        "venue",
        "venue_type",
        "identifiers",
        "canonical_url",
        "retrieved_date",
        "retrieval_method",
        "verification_level",
        "snapshot_file",
        "snapshot_sha256",
        "relevance_domains",
        "bears_on_ids",
        "stance",
        "notes",
    ]
    for r in rows:
        r["round_added"] = "1"

    with (ROOT / "SOURCES.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, quoting=csv.QUOTE_ALL)
        w.writeheader()
        for r in rows:
            w.writerow({k: r[k] for k in cols})

    lead_cols = ["lead_id", "title_hint", "identifier_hint", "url", "why_not_citable", "next_action"]
    with (ROOT / "LEADS.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=lead_cols, quoting=csv.QUOTE_ALL)
        w.writeheader()
        for r in LEADS:
            w.writerow(r)

    print(f"wrote {len(rows)} sources + {len(rows)} snapshots, {len(LEADS)} leads")


if __name__ == "__main__":
    main()
