"""Adjudications for the 24 AUD-* claims in the pinned baseline.

Split out of _build_round05.py so that file stays reviewable. Imported there.

Every row here must cite at least one source, and every cited source must list the
claim in its bears_on_ids. The source->claim half of that mapping is extended by
_build_round08.py, which touches bears_on_ids only and never a snapshot.
"""

AUD_ADJ = [
    dict(
        claim_id="AUD-CORR-0995", claim_class="EMPIRICAL", literature_role="INTERPRETATION",
        verdict="SUPPORTED_WITH_SCOPE", mapping_health="COMPLETE",
        producing_code="PRESENT", severity="MEDIUM",
        verdict_basis=(
            "The claim's own caveat - 'scope: chosen omega only' - is exactly the condition the "
            "literature imposes. LIT-0040 (Seliger, Young & Tsimring) shows that in a plastic "
            "Kuramoto network the synchronized state is robust against noise and SMALL variations "
            "in natural frequencies, with clusters selectable by external driving at a chosen "
            "frequency. That is the mechanism by which a statistic computed at one hand-picked "
            "frequency vector is not a statement about the model class. The repository reached "
            "this by measurement (0.995 at repo omega, ~0.71 uniform, 0.59-0.63 clustered); "
            "LIT-0040 supplies the reason it had to be true. The claim is unusually well "
            "self-scoped - it already says 'not a tautology, but dominated by persistence', which "
            "is the correction of its own original overstatement."
        ),
        required_change=(
            "Attach LIT-0040 as the mechanism-level justification for the omega-scope caveat, so "
            "the caveat is citable rather than merely cautious."
        ),
    ),
    dict(
        claim_id="AUD-TOPO-OMEGA", claim_class="EMPIRICAL", literature_role="INTERPRETATION",
        verdict="SUPPORTED_WITH_SCOPE", mapping_health="COMPLETE",
        producing_code="PRESENT", severity="MEDIUM",
        verdict_basis=(
            "This is the sharpest methodological claim in the audit corpus and it is written the "
            "way a claim should be: 'informative predictor (not a superset), exact only for "
            "repo-omega no_delay; for generic omega selection is multistable'. LIT-0039 reviews "
            "exactly the class where multistability is the norm rather than an anomaly, and "
            "LIT-0040 demonstrates cluster selection by driving. So 'multistable for generic "
            "omega' is the expected behaviour for an adaptive network, not a defect of this one. "
            "The claim's refusal to call the closed-form rule a superset - it reports precision "
            "0.59-0.98 against recall 0.18-0.57 - is the reason it survives adjudication at all; "
            "the original 'topology is fixed by omega' did not."
        ),
        required_change=(
            "Attach LIT-0039 and LIT-0040. Consider promoting the 'multistable for generic omega' "
            "clause from caveat to primary statement: it is the part the literature supports most "
            "strongly and it is currently buried."
        ),
    ),
    dict(
        claim_id="AUD-GATE", claim_class="FORMAL", literature_role="FORMALIZATION",
        verdict="SUPPORTED_WITH_SCOPE", mapping_health="COMPLETE",
        producing_code="PRESENT", severity="HIGH",
        verdict_basis=(
            "THE FORM IS NOW SETTLED FROM THE CODE, not from inference. "
            "AIEF_1_3_falsification_updated.py:446-447 reads: scale = np.minimum(1.0, cap / "
            "(row_sum_pre + ZERO_TOL)); B *= np.minimum.outer(scale, scale). So each EDGE is "
            "multiplied by the MINIMUM OF TWO NODE-SPECIFIC FACTORS - not by a single global "
            "factor, and nothing is subtracted. That is neither of Miller & MacKay's (LIT-0043) "
            "two enforcement methods: their multiplicative case rescales the whole weight vector "
            "by ONE common factor, which is what preserves direction and makes the dynamics "
            "converge to the principal eigenvector of the unconstrained operator; their "
            "subtractive case pulls weights to the bounds. Because AIEF's factor varies edge by "
            "edge, the gate does NOT preserve the direction of B, so LIT-0043's convergence "
            "theorem simply does not apply to it. The label 'node-strength multiplicative "
            "normalisation' is half defensible - weights ARE multiplied, and the scale IS derived "
            "from node strength - but 'multiplicative' there means 'not additive', which is a "
            "different property from the one that generates Miller-MacKay's result. The no-go "
            "half of the claim is correct and well argued: it is not a metric, KL or Bregman "
            "projection onto the capacity set."
        ),
        required_change=(
            "Rename to something like 'per-edge capped admissibility scaling' and state the "
            "property that matters: the rescaling factor is per-edge (min of two node factors), "
            "so it does not preserve the direction of B and LIT-0043's convergence theorem is "
            "inapplicable. Keep the no-go statement verbatim - it is correct. Consider adding the "
            "three-way comparison as a testable claim: global-multiplicative, subtractive, and "
            "this per-edge cap should be run on one small network and their attractors compared."
        ),
    ),
    dict(
        claim_id="AUD-SCOPE-1.4", claim_class="EMPIRICAL", literature_role="INFERENCE",
        verdict="SUPPORTED", mapping_health="COMPLETE",
        producing_code="NOT_APPLICABLE", severity="LOW",
        verdict_basis=(
            "A scope statement that separates a 40-seed cohort result from a single-seed case "
            "study, which is the right distinction and one the project earned the hard way (its "
            "own audit M2 made the same point about one frozen replay). LIT-0002 supplies the "
            "inferential rule that makes the separation mandatory rather than tidy: with n=1 there "
            "is no cluster structure to account for, no within-seed contrast to estimate, and no "
            "interval to report - so a single-seed result cannot be phrased as a cohort finding "
            "in any defensible way. 'Do not generalise single-seed results to the cohort' is "
            "therefore not stylistic caution; it is the boundary of what the design can support."
        ),
        required_change=(
            "Attach LIT-0002 to make the n=1 boundary citable, and note the seed is the same "
            "exceptional seed named in round 3's F17 and in audit finding M2."
        ),
    ),
    dict(
        claim_id="AUD-SLOWPOLE", claim_class="REJECTION", literature_role="METHOD_VALIDITY",
        verdict="VALIDATED_REJECTION", mapping_health="COMPLETE",
        producing_code="PRESENT", severity="LOW",
        verdict_basis=(
            "Quarantined on the strongest possible ground - the derivation is invalid, not merely "
            "superseded - and the literature validates every leg of it. (1) LIT-0009: at "
            "nonsmooth points (clipping, gate, endpoint minima, controller ties) the map has no "
            "branchwise Jacobian, so a central-difference matrix is a generalized response object, "
            "which the caveat already records via the J+ vs J- difference of 0.49937. (2) "
            "LIT-0022: finite differencing is unsuitable for nonsmooth functions because it steps "
            "across nonsmooth points - a property of the method, not the step size. (3) LIT-0008: "
            "for a non-normal finite-time map, eigenvalues are not the right object; singular "
            "values are, which the caveat reaches independently. (4) LIT-0006: a residual-based "
            "acceptance test is what would have caught this automatically."
        ),
        required_change=(
            "Cite LIT-0008/0009/0022/0006 in the caveat. The claim currently reaches the right "
            "conclusions by argument; the literature makes them citable."
        ),
    ),
    dict(
        claim_id="AUD-RATELAW", claim_class="FORMAL", literature_role="FORMALIZATION",
        verdict="SUPPORTED_WITH_SCOPE", mapping_health="COMPLETE",
        producing_code="PRESENT", severity="MEDIUM",
        verdict_basis=(
            "The strongest formal claim in the corpus: an exact one-step multiplier lambda = "
            "(1-gamma*dt) s_J on the unsigned-incidence controller kernel, with five explicitly "
            "stated hypotheses, checked on 374 components, and a residual it does not explain. "
            "LIT-0043 is the external anchor the repository reached for, but round 9 shows the "
            "mapping is looser than that: the gate multiplies each edge by min of two node "
            "factors (see the AUD-GATE row), so it is not Miller-MacKay multiplicative "
            "enforcement and the -1/T_w + k*eta/c structure is NOT explained by that paper's "
            "mechanism. The rate law may still be exactly right - it is verified to 2.1e-8 - but "
            "its DERIVATION currently has no cited basis, and AIEFS_salvage.md's claim that "
            "multiplicative normalisation produces it is unsupported as stated. On the unexplained ~2e-8 residual, the claim's "
            "own suspicion (finite-difference error on a component with delta in [1e-9, 1e-8)) is "
            "the literature-consistent one: LIT-0014 puts a difference step of that size at the "
            "edge of representable precision against a 2.1e-10 agreement for the well-resolved "
            "cases, and the correct test is the step-size sweep the claim already asks for."
        ),
        required_change=(
            "Attach LIT-0043 (normalisation-as-decay mechanism) and LIT-0014 (why the residual is "
            "most likely a difference-step artefact). Keep the residual open - do not close it by "
            "citing a plausible cause."
        ),
    ),
    dict(
        claim_id="AUD-KAPPA-TW", claim_class="FORMAL", literature_role="FORMALIZATION",
        verdict="SUPPORTED_WITH_SCOPE", mapping_health="COMPLETE",
        producing_code="PRESENT", severity="LOW",
        verdict_basis=(
            "kappa_k(T_w) = k*eta/c - 1/T_w is the continuous limit of AUD-RATELAW's discrete rate, "
            "verified across 292 slow components with the k-distribution reported (k=2: 1, k=3: 88, "
            "k=4: 24, k=5: 179) rather than pooled, which is what makes the fit checkable. Roughly "
            "half the fitted terms (179 of 292 at k=5) sit at the top of the k range, so the fit is "
            "dominated by the largest cliques and is thinnest exactly where k=2 is: a single "
            "component. The claim says so itself by stating that the k=2 value 'applies only to "
            "the single exceptional K3'. LIT-0043 supplies the mechanism for the k*eta/c term; the "
            "-1/T_w term is the EMA decay and is not a normalisation effect at all, which the claim "
            "correctly keeps separate."
        ),
        required_change=(
            "Attach LIT-0043. Flag the k=2 point as n=1 in the statement, not only in the caveat - "
            "a k=2 coefficient supported by one component should not read as a fitted law."
        ),
    ),
    dict(
        claim_id="AUD-FROZEN-TOPO", claim_class="EMPIRICAL", literature_role="SCOPE_ONLY",
        verdict="CONTEXT_ONLY", mapping_health="COMPLETE",
        producing_code="PRESENT", severity="NONE",
        verdict_basis=(
            "A pure finite numerical observation - 0 of 29,040 edges change threshold status - and "
            "no external literature can attest a count. What literature can do is explain why the "
            "result is unsurprising, and LIT-0010 does: in a delay system the state IS the history "
            "segment, so a frozen binary topology is a frozen PROJECTION of a still-moving state, "
            "not a frozen system. The claim's own caveat ('continuous weights may still move') is "
            "the same point reached empirically. The two together are stronger than either: the "
            "topology is frozen because it is thresholded, and the state keeps evolving because it "
            "is a history object."
        ),
        required_change=(
            "Attach LIT-0010 as framing for the caveat. The claim is correctly scoped already; do "
            "not promote it to a statement about the dynamics."
        ),
    ),
    dict(
        claim_id="AUD-DELAY", claim_class="EMPIRICAL", literature_role="INTERPRETATION",
        verdict="SUPPORTED_WITH_SCOPE", mapping_health="COMPLETE",
        producing_code="PRESENT", severity="LOW",
        verdict_basis=(
            "Written with unusual care: 'not necessary but not inert', and it explicitly labels "
            "its statistic a sample-diversity count, not a basin count. LIT-0028 independently "
            "establishes that delay effects are not recoverable from a phase-reduced description, "
            "and LIT-0035 names the mechanism class (delay changes which states coexist) while "
            "LIT-0039 places multistability among the standard phenomena of adaptive networks. So "
            "'more distinct topologies under delay' is the predicted direction. The claim's "
            "refusal to call it a basin count is what keeps it honest - a basin count would need a "
            "sampling design the study does not have."
        ),
        required_change=(
            "Attach LIT-0028, LIT-0035 and LIT-0039. Restate the headline as 'delay increases the "
            "diversity of sampled outcomes' rather than implying a landscape count."
        ),
    ),
    dict(
        claim_id="AUD-K3", claim_class="FORMAL", literature_role="FORMALIZATION",
        verdict="SUPPORTED_WITH_SCOPE", mapping_health="COMPLETE",
        producing_code="PRESENT", severity="LOW",
        verdict_basis=(
            "The mathematical content is sound and narrow in the right way: strict K3 components "
            "have zero lineality and one-sided controller-selection rays, and are not eigenmodes. "
            "LIT-0011 supplies the algebraic fact underneath - the kernel of the unsigned "
            "incidence matrix of K3 is trivial (dim m - n = 3 - 3 = 0), which is exactly why there "
            "can be no two-sided fiber for a strict K3, and why a two-sided fiber exists only for "
            "the exceptional resolved one. The claim's insistence that K3s are 'not eigenmodes' is "
            "the distinction the perturbed spectrum needed and did not have."
        ),
        required_change=(
            "Attach LIT-0011 and state the trivial-kernel fact explicitly: dim ker A_J = m - n = 0 "
            "for K3 is the reason, not an empirical observation about one component."
        ),
    ),
    dict(
        claim_id="AUD-TIES", claim_class="FORMAL", literature_role="FORMALIZATION",
        verdict="SUPPORTED_WITH_SCOPE", mapping_health="COMPLETE",
        producing_code="PRESENT", severity="LOW",
        verdict_basis=(
            "The best-behaved claim in the entire registry, and worth saying so plainly. It derives "
            "nonadditivity 1/sqrt(2k(k-1)) and odd defect sqrt(2/(k+1)) for an all-tied equal-edge "
            "K_n, then volunteers that the formulas are NOT universal: an unequal-edge K4 with "
            "equal row sums gives 0.2003 against a predicted 0.2887, the figure depends on which "
            "adjacent edge pair is perturbed, and the refuting configuration is not itself a fixed "
            "point so it refutes universality without being a counterexample. Claims that derive "
            "their own counterexample are rare. LIT-0021 licenses the derivative being used "
            "(lexicographic, unique once a basis is fixed); LIT-0022 supplies the implementable "
            "rules for the min/max/mid/abs primitives the gate is built from; LIT-0009 gives the "
            "generalized-gradient frame for the tie itself; LIT-0033 shows the approach is current "
            "practice rather than local."
        ),
        required_change=(
            "Attach LIT-0009/0021/0022/0033. Promote the equal-edge hypothesis from caveat to "
            "statement - it is a real hypothesis, not a technicality, and the counterexample "
            "depends on it."
        ),
    ),
    dict(
        claim_id="AUD-REPRO13", claim_class="IMPLEMENTATION", literature_role="METHOD_VALIDITY",
        verdict="SUPPORTED", mapping_health="COMPLETE",
        producing_code="PRESENT", severity="NONE",
        verdict_basis=(
            "The claim already makes the distinction the literature requires, unprompted: 500/500 "
            "bit-exact on the 7 arrays and 4 headline scalars, but only 78/500 on all 38 keys, "
            "with the remainder differing in derived scalars by <=4.9e-15. That is precisely "
            "LIT-0012's point - bit-identical agreement is a same-order, same-environment property "
            "of the primitives, and derived quantities accumulate order-dependent rounding that "
            "does not indicate a defect. Reporting both numbers instead of the favourable one is "
            "the behaviour that makes the rest of the audit corpus credible."
        ),
        required_change=(
            "Attach LIT-0012/0014/0038. No change to the claim; record that 'bit-exact on "
            "declared keys' is the correct form of a reproducibility result, not a compromise."
        ),
    ),
    dict(
        claim_id="AUD-REPRO-B2A95", claim_class="IMPLEMENTATION", literature_role="METHOD_VALIDITY",
        verdict="SUPPORTED_WITH_SCOPE", mapping_health="COMPLETE",
        producing_code="PRESENT", severity="LOW",
        verdict_basis=(
            "A single run hash reproducing an official run to 6.7e-16 with identical NaN patterns "
            "is a strong same-environment result. LIT-0013 is the reason the scope line matters: "
            "reproducible summation algorithms exist precisely because default summation is not "
            "associative, so a 6.7e-16 agreement tells you the code and environment match, not "
            "that the computation is platform-invariant. The caveat already pins numpy 2.5.4, "
            "pandas 3.0.6 and python 3.13.5, which is the right thing to pin. LIT-0038 makes the "
            "point at policy level: agreement within a stated tolerance is what 'reproduced' means, "
            "and exactness is not required."
        ),
        required_change=(
            "Attach LIT-0013/0012/0014/0038. State that one run hash is one data point and name "
            "what a second independent hash would add."
        ),
    ),
    dict(
        claim_id="AUD-LABEL", claim_class="EMPIRICAL", literature_role="SCOPE_ONLY",
        verdict="SUPPORTED", mapping_health="COMPLETE",
        producing_code="NOT_APPLICABLE", severity="MEDIUM",
        verdict_basis=(
            "The claim was blocked in round 8 for lack of any methodology source; that gap is now "
            "closed and the claim survives intact. What it asserts is a labelling rule - audit "
            "analyses are 'controlled exploratory analyses with a fixed recorded design' and "
            "'nothing in the repo was preregistered' - and LIT-0044 supplies exactly the "
            "distinction it needs: postdiction versus prediction, with preregistration as the "
            "operation that separates them. The key point from that paper is that the failure mode "
            "is not dishonesty but hindsight bias - a vague prediction can be rationalised after "
            "the fact as having been supported - which is why 'exploratory with a fixed recorded "
            "design' is a coherent and honest category rather than a hedge. LIT-0045 names the "
            "thing the label is avoiding: HARKing, presenting a post hoc hypothesis as an a priori "
            "one. The claim does the opposite of HARKing - it discloses the absence of "
            "preregistration - and the literature says that disclosure costs the confirmatory "
            "interpretation while leaving the exploratory one intact. That is the correct trade and "
            "the claim already makes it."
        ),
        required_change=(
            "Attach LIT-0044 and LIT-0045. State the consequence rather than only the rule: no "
            "result in this repository may be described as confirmatory, and 'fixed recorded "
            "design' does not substitute for preregistration because it is still post hoc. That "
            "belongs in the claim, not only in the audit conversation."
        ),
    ),
    dict(
        claim_id="AUD-HELDOUT-LABEL", claim_class="EMPIRICAL", literature_role="INFERENCE",
        verdict="SUPPORTED_WITH_SCOPE", mapping_health="COMPLETE",
        producing_code="PRESENT", severity="MEDIUM",
        verdict_basis=(
            "The verification is thorough - the two labels are identical in all 440 runs, 0 of "
            "29,040 edges differ, and no P_future value lies within 1e-6 of the 0.5 boundary - and "
            "the point-biserial observation is correct. The scope limit is inferential rather than "
            "numerical. LIT-0023 defines the predictability notion the held-out test implements "
            "(causality as incremental predictability conditional on history), and LIT-0024 shows "
            "that for strongly coupled, state-dependent, nonseparable systems that notion is "
            "contested. So establishing that two labels coincide establishes that the AUC table is "
            "readable under either name; it does not establish that a held-out predictability gain "
            "is evidence of a causal mechanism, and the claim should not let a reader infer the "
            "second from the first."
        ),
        required_change=(
            "Attach LIT-0023/0024 and add one line: label equivalence makes the AUC table "
            "unambiguous, it does not upgrade predictability to causation. LIT-0024 is the reason "
            "that distinction is load-bearing here rather than pedantic."
        ),
    ),
    dict(
        claim_id="AUD-CYCLE-KERNEL", claim_class="FORMAL", literature_role="FORMALIZATION",
        verdict="SUPPORTED", mapping_health="COMPLETE",
        producing_code="PRESENT", severity="NONE",
        verdict_basis=(
            "The most carefully worded claim in the baseline. It states that the round-2 "
            "central-difference matrix at a tie was not a Jacobian (correct, and LIT-0020's "
            "piecewise-smooth frame says why), identifies the correct object as the one-step "
            "multiplier on the controller kernel K = ker A_J, gives dim K = m - n = n(n-3)/2 for "
            "an all-tied K_n, checks it on 373/373 components, and separately flags that only 292 "
            "of 406 replay components agree with the slow multiplier to 4.5e-4. LIT-0011 is the "
            "classical source for the kernel dimension. The ERRATA E6 note that K is the UNSIGNED "
            "incidence kernel and NOT the graph cycle space is what keeps this claim from being a "
            "false statement about a real matrix, and this is the object my round-5 attribution "
            "got wrong."
        ),
        required_change=(
            "Attach LIT-0011. Keep the E6 naming note attached permanently - without it the claim "
            "reads as a statement about the cycle space, which for non-bipartite K_n would be "
            "wrong by exactly one dimension."
        ),
    ),
    dict(
        claim_id="AUD-V4-HELDEVENT", claim_class="IMPLEMENTATION", literature_role="METHOD_VALIDITY",
        verdict="SUPPORTED", mapping_health="COMPLETE",
        producing_code="NOT_APPLICABLE", severity="LOW",
        verdict_basis=(
            "This claim is a floating-point boundary defect and LIT-0014 is its textbook citation: "
            "_held_index computes searchsorted(times, times[index] + duration, side='left'), so an "
            "event held EXACTLY the required duration is rejected whenever times[index] + duration "
            "lands one ulp above the saved sample. The claim quantifies it on v4's own grid - 32 of "
            "605 valid start positions missed, first at t = 16.01 to 33.51 where v4 effectively "
            "requires 18.0 - and, importantly, bounds its own blast radius: only grid-multiple hold "
            "durations can be hit, so the 17.5029 x rho nominal holds and the non-held estimands "
            "are unaffected. That is a defect report with a scope analysis attached, which is what "
            "makes it actionable rather than alarming."
        ),
        required_change=(
            "Attach LIT-0014. Note that the correct fix is a relative tolerance on the end check, "
            "which is what the unaudited v4.1 candidate does - but the candidate must be audited "
            "before it can be cited."
        ),
    ),
    dict(
        claim_id="AUD-MODULAR-ORACLE", claim_class="IMPLEMENTATION", literature_role="METHOD_VALIDITY",
        verdict="SUPPORTED_WITH_SCOPE", mapping_health="COMPLETE",
        producing_code="NOT_APPLICABLE", severity="HIGH",
        verdict_basis=(
            "The claim is accurate and its implication is stronger than it states. The oracle test "
            "that would certify the modular platform is skipped unless AIEF_MODULAR_RUN is set and "
            "a pre-generated data directory is supplied, so a default run of the suite reports 40 "
            "passed / 2 skipped without ever testing oracle equivalence. LIT-0038 gives this a "
            "policy consequence the claim does not draw: an artifact is 'Artifacts Evaluated - "
            "Functional' only if 'documented, consistent, complete, EXERCISABLE, and include "
            "appropriate evidence of verification and validation'. A certification test that is "
            "skipped by default is not exercisable by a reviewer following the documented "
            "instructions, so the platform cannot claim that badge on the strength of a green "
            "default suite. The claim already notes that neither run re-tests the 344-array "
            "max_abs_diff = 0 identity of IMPL-MODULAR-01, which is the same point."
        ),
        required_change=(
            "Attach LIT-0038 and draw the consequence: IMPL-MODULAR-01's 344-array identity is "
            "uncertified in CI, and a skipped-by-default oracle test does not satisfy ACM's "
            "'exercisable' criterion. Either make the oracle test runnable without a secret "
            "environment or stop presenting the default suite as certification."
        ),
    ),
    dict(
        claim_id="AUD-TIMESTEP", claim_class="EMPIRICAL", literature_role="SCOPE_ONLY",
        verdict="SUPPORTED_WITH_SCOPE", mapping_health="COMPLETE",
        producing_code="NOT_APPLICABLE", severity="HIGH",
        verdict_basis=(
            "An open item stated plainly: no dt / dt-half / dt-quarter convergence study has been "
            "run, so reported trajectories, rates and topologies hold for dt = 0.01 only. The "
            "literature makes this a bigger gap than 'unverified integration step' sounds. "
            "LIT-0035 states that numerically solving retarded functional differential equations "
            "'cannot be founded on the mere adaptation of well-known methods for ordinary ... "
            "equations', and that convergence analysis for these equations is organised around the "
            "solution map and the propagation of discontinuity points - not around a local "
            "truncation error argument. LIT-0029 gives the method-of-steps error analysis. So a "
            "timestep study for the AIEF engine is not routine due diligence on an ODE; it is the "
            "first required step of validating a DDE integrator, and its absence means the "
            "convergence order of the frozen results is unknown rather than merely unstated."
        ),
        required_change=(
            "Attach LIT-0029/0035 and restate in the literature's terms: the missing study is a "
            "convergence analysis of the solution map, not a truncation-error check. Raise its "
            "priority accordingly - this and AUD-NOVELTY are the two open items that gate "
            "publication-grade claims."
        ),
    ),
    dict(
        claim_id="AUD-B-SCAFFOLD", claim_class="EMPIRICAL", literature_role="INTERPRETATION",
        verdict="SUPPORTED_WITH_SCOPE", mapping_health="COMPLETE",
        producing_code="NOT_APPLICABLE", severity="LOW",
        verdict_basis=(
            "An open item that says a piece of audit wording was never turned into a testable "
            "claim, and that declines to treat it as a finding against EMP-AIEF14-01 - which is "
            "the right call, since reset_B reconstruction stands independently. The literature can "
            "supply the missing formulation rather than only the frame. LIT-0010 says the state of "
            "a delay system is the history segment; 'B is a scaffold' therefore has a testable "
            "reading - B's influence is subsumed by the history it co-evolved with - and that is "
            "precisely what EMP-AIEF14-01 measured by resetting B and recovering the topology from "
            "delay state. LIT-0018 gives the dimension count (N + N^2) that makes the subsumption "
            "expected rather than surprising."
        ),
        required_change=(
            "Attach LIT-0010/0018 and convert the wording into the testable claim it almost is: "
            "'the contribution of B after the split is not identifiable separately from the delayed "
            "history state that produced it.' That is a statement reset_B can actually test."
        ),
    ),
    dict(
        claim_id="AUD-CORR-0995-SCOPE", claim_class="EMPIRICAL", literature_role="INTERPRETATION",
        verdict="SUPPORTED_WITH_SCOPE", mapping_health="COMPLETE",
        producing_code="PRESENT", severity="MEDIUM",
        verdict_basis=(
            "The scoping record for Corr_physical ~0.995, and it does the job properly: fixed-omega "
            "0.995 against random-omega means of ~0.71 uniform and 0.59-0.63 clustered, with the "
            "defined-run counts given rather than silently dropped (60/60, 37/60, 39/60). Its "
            "per-run replication medians - uniform baseline 0.978, clustered 0.449 - show the "
            "correlation is bimodal rather than shiftable, which a mean alone would hide. LIT-0040 "
            "supplies the mechanism: in a plastic network the selected state depends on the "
            "frequency vector and on driving, so a correlation conditioned on one hand-picked "
            "vector is a statement about that run, not about the model."
        ),
        required_change=(
            "Attach LIT-0040. Keep the note that the inline side branch fix/corr-0995-scope was "
            "deliberately not merged and that ERRATA E9 is the record - the pinning discipline is "
            "working and should be visible."
        ),
    ),
    dict(
        claim_id="AUD-RESP1-UNIFORM", claim_class="EMPIRICAL", literature_role="INFERENCE",
        verdict="SUPPORTED", mapping_health="COMPLETE",
        producing_code="PRESENT", severity="LOW",
        verdict_basis=(
            "A self-issued erratum that corrects an overstatement in the audit's own response: "
            "past R 'adds over delta-omega-only' holds for uniform no_delay on log loss (0.240 vs "
            "0.396) but NOT on held-out AUC (0.850 vs 0.883). That is the right shape of "
            "correction - the original wording is kept visible, the corrected scope is stated "
            "per metric, and no number is changed. LIT-0023/0024 are the frame for why metric "
            "disagreement is expected rather than embarrassing: for a coupled nonlinear system, "
            "AUC and log loss can rank two predictors oppositely because they weight regions of "
            "the score distribution differently, so a claim about 'adds over' must name its metric."
        ),
        required_change=(
            "Attach LIT-0023/0024 and generalise the lesson into a house rule: any comparative "
            "predictive claim must name its metric, because AUC and log loss can disagree in sign "
            "on the same data - which is exactly what happened here."
        ),
    ),
]
