# Builds claims_map.csv, totals.json, inconsistencies.csv and MAP_NOTES.md for the AIEFS project map (2026-10-29).
# Revision 2 (2026-10-29): applies Auditor Seat 002's prioritized fix list (see REVISION block below).
# Sources read via `git show` from research/freezing (cc31533) and research/lean-kn (2fc1110); nothing edited.
import csv, json, collections, os
HERE=os.path.dirname(os.path.abspath(__file__))
L,X,F,A,U,R = "Lean-proved","exact computation","floating-point numerics","argument only","unverified","retracted/corrected"
TH,NO,CJ,DF,LK = "theorem","numerical observation","conjecture","definition","literature-known"
CL = "registry/claims.csv:{} (research/freezing cc31533)"
rows=[]
def add(id,stmt,typ,ev,evd,scope,nums,nov,novc,redisc,redb,gaps,src,cond="no",errata="",corr="no",lean="",reg="registered",status=""):
    rows.append(dict(id=id,registry=reg,status_in_registry=status,plain_statement=stmt,type=typ,evidence_level=ev,evidence_detail=evd,
      lean_project_and_axioms=lean,conditional=cond,errata=errata,wording_or_status_corrected=corr,scope_conditions=scope,
      key_numbers=nums,novelty=nov,novelty_citation=novc,independent_rediscovery_validation=redisc,rediscovery_basis=redb,
      open_gaps=gaps,source=src))
P="Single exceptional seed (1 of 40) of AIEF-1.4"
# ---------- registry: empirical ----------
add("EMP-AIEF13-01","Shuffling the coherence history (shuffle_R) wipes out most of the lasting network compared with the normal run.",NO,F,"100 disjoint paired seeds (200 runs); re-run 2026-10-28 matches","AIEF-1.3 parameters, repo omega, N=12, dt=0.01","D_B=+0.3059 [0.2989,0.3130], dz=8.43","unchecked","","no","necessity ablation, not a literature result","Outcome forced by construction (shuffled mean R 0.371 < 0.4286 so D_B=0); not preregistered",CL.format(2),status="Frozen; audit-qualified")
add("EMP-AIEF13-02","Turning off the adaptive feedback (no_mu) shrinks the lasting network a lot; turning off the delay alone changes it only a little.",NO,F,"100 disjoint paired seeds; re-run matches","AIEF-1.3 parameters, repo omega","no_mu D_B=+0.271 dz=4.90; no_delay D_B=-0.027 dz=-0.76","known-variant","Delay+Hebbian Kuramoto: Timms & English 2014; Madadi Asl 2017 (literature Page row e)","unclear","audit wording 'not necessary but not inert' came with the salvage literature list","Registry caveat 'feedback rather than delay drives persistence' is broader than the audit wording",CL.format(3),status="Frozen; audit-qualified")
add("EMP-AIEF14-01","If you erase the weights B at the split time, the rest of the state (phases, history, EMA) rebuilds the same network.",NO,F,"40 paired seeds","AIEF-1.4, repo omega, rho=1","reset_B Jaccard 1.000 vs continue; B_split AUC 1.0 (predictive, not causal)","unchecked","","no","","Note mixes scope: '0/29040 edges' is from the 440 audit runs, not the 40-seed cohort; 'B is a scaffold' untested (AUD-B-SCAFFOLD)",CL.format(4),errata="E3",corr="yes (audit rewording)",status="Frozen; reworded")
add("EMP-AIEF14-02","With matched phases at the split, one similarity score goes up but mean persistence goes down; no 'mediation' is claimed.",NO,F,"40 seeds","AIEF-1.4 matched-phase design (exploratory)","Weighted_similarity_late +0.064 [0.041,0.089] (31/40); P_mean_late -0.018 [-0.027,-0.009]","unchecked","","no","","Exploratory only",CL.format(5),errata="E4",corr="yes ('mediates' withdrawn)",status="Exploratory")
add("EMP-AIEF14-03","Separating fixed physical time windows from EMA-scaled windows removes a confound in the window-length study.",NO,F,"200 conditions (5 rho x 40 seeds); DID estimand NOT tested by audits","rho in {0.5,0.75,1,1.5,2}","200 conditions","unchecked","","no","","DID claim untested; held-event rows blocked by AUD-V4-HELDEVENT; 'recovery' wording (AUD-V4-RECOVERY-WORDING)",CL.format(6),corr="yes (Frozen->Exploratory, MERGE_CHECK)",status="Exploratory")
add("IMPL-MODULAR-01","The modular code gives exactly the same arrays as the original single-file code on the same machine.",NO,F,"344 condition arrays (arena record); not re-tested","same host/libm; cross-host needs 1e-11 tolerance","max_abs_diff 0.0","n/a (software)","","n/a","","The 344-array identity was not re-run (AUD-MODULAR-ORACLE)",CL.format(7),status="Supported")
add("LEAN-CF-01","The 2x3 matrix [[1,1,0],[1,0,1]] has a 1-dimensional null space spanned by (1,-1,-1); checked by computer proof.",TH,L,"Lean 4 AIEFProofs; 7/7 PASS","pure linear algebra; says nothing about dynamics","kernel span(1,-1,-1)","known (elementary)","standard linear algebra","no","trivial fact","Physical relevance needs CF05 (single seed)",CL.format(8),lean="AIEFProofs; propext, Classical.choice, Quot.sound",status="Supported")
add("CAVEAT-MS-8.4","Draft Corollary 8.4 claims too much: the left-covector identity holds only at equal-edge points, not on general kernel perturbations.",TH,R,"arena's own correction (registry caveat; no errata number)","strict winner cone","n/a","unchecked","","n/a","","Audits did not re-derive 8.4; manuscript text unchanged",CL.format(9),cond="yes",corr="yes (registry caveat)",status="Exploratory")
for i,(s,ev,evd,nums,cond) in enumerate([
 ("The directions you can move without breaking the capacity limits are found by zeroing inactive edges and keeping active row sums exact.",A,"paper proof (controller-fiber package)","n/a","yes"),
 ("A clipped row is strictly inside the gated (node-strength-normalised) output when epsilon>0.",A,"algebraic proof; audit found the same margin numerically","margin ~6.7e-13 (epsilon-level)","yes"),
 ("The admissibility map is exactly affine on the multiplier-controller pieces, ties included.",A,"paper proof","n/a","yes"),
 ("Keeping a kernel fixed is the same as a factorisation C D = Gamma C.",A,"pure linear algebra; not re-checked","n/a","yes"),
 ("In the exceptional run, the winner pattern of the K3 triangle stays (7,2,7) in all 32,001 saved states.",F,"1 seed, 32,001 states; not re-checked by audit","32,001 states","no"),
 ("Given that winner pattern, the exceptional controller kernel is span(1,-1,-1).",L,"kernel part = LEAN-CF-01; applicability rests on CF05","span(1,-1,-1)","yes"),
 ("The fixed right carrier v is invariant exactly when s2 = s7.",A,"paper proof (direct matrix algebra)","n/a","yes"),
 ("After right closure, u(r) is an exact normalised left covector at each point.",A,"paper proof","n/a","yes"),
 ("If proposal differences go to zero (one-sided), the K3 branch matrices converge to a fixed analytic family.",A,"paper proof (conditional limit); not re-derived","n/a","yes"),
 ("By the last saved time, the K3 block is very close to that analytic family.",F,"1 seed; finite residuals","small final residuals","no")]):
    cid="CF%02d"%(i+1)
    nov="unchecked" if cid not in ("CF04",) else "known (standard linear algebra)"
    add(cid,s,(NO if ev==F else TH),ev,evd,P,nums,nov,"audit salvage:23 calls this vocabulary renamed standard linear algebra" ,"no" if cid!="CF04" else "unclear","" if cid!="CF04" else "standard identity; files give a proof but no literature comparison",
        "Single seed; infinite-time branch persistence open (CF12)",CL.format(9+i+1),cond=cond,lean=("AIEFProofs (kernel only); 3 std axioms" if cid=="CF06" else ""),
        corr=("yes (reworded 'projected'->'gated', 2026-10-28)" if cid=="CF02" else "no"),status="Supported")
add("CF11","Conjecture: the alignment residuals keep shrinking after t=320.",CJ,U,"none beyond the finite replay",P,"t<=320","unchecked","","n/a","","Open",CL.format(20),status="Exploratory")
add("CF12","Conjecture: the winning branch persists forever (infinite-time branch persistence).",CJ,U,"none",P,"n/a","unchecked","","n/a","","Open; load-bearing for the whole CF chain",CL.format(21),status="Exploratory")
retired=["B is the unique memory carrier","the gate is a rare repair","the mature system is at equilibrium","a real active-face switch at t=124.05","a bare-gamma edge mode","controller equilibrium holds on all nodes","K4-K6 components are only a hypothesis","one Euclidean coordinate predicts both K3 directions","POD Rayleigh quotient is the exact memory rate","a shared two-state (a,g) model is identified","complex EMA difference decays homogeneously","symmetrisation creates the resonance mode","the alignment law has no cancellation","lambda_B/alpha_EMA is a loop gain","rank-one tangent implies a 1-D attractor","the defect direction is only an empirical POD mode","source forcing is negligible (~1e-5)","phase stabilisation because terms vanish separately"]
for i,t in enumerate(retired):
    add("S%02d"%(i+1),"RETIRED older interpretation: "+t+". The registry gives the replacement wording.",NO,R,"retired in registry; E3 maps the legacy lists","AIEF-1.4 synthesis docs","n/a","n/a","","n/a","","S01 replacement wording was itself struck by audit" if i==0 else "",CL.format(22+i),errata="E3",corr="yes (retired)",status="Superseded")
for id,s,ln in [("REJ-SPEC-01","REJECTED: an 8-D POD slow subspace faithfully captures the post-split dynamics.",40),("REJ-SPEC-02","REJECTED: a finite-difference Jacobian at eps=1e-8 resolves the exact spectrum near ties.",41),("REJ-LOCK-03","REJECTED: mature frequencies satisfy bare zero-sum locking omega_i + G_i = 0.",42),("REJ-K3-04","REJECTED: 856 K3 triangles dominate mature networks (corrected count: 26 isolated K3).",43),("REJ-COHORT-05","REJECTED: the early 20-seed folder gives N=40 independent pairs (it does not).",44)]:
    add(id,s,NO,R,"registry Rejected (no errata number)","AIEF-1.4 / 1.3","REJ-K3-04: 856 vs 26" if id=="REJ-K3-04" else "","n/a","","n/a","","",CL.format(ln),corr="yes (rejected)",status="Rejected")
# ---------- registry: audits ----------
add("AUD-CORR-0995","The 0.995 link between past coherence and lasting edges holds only for the repo's hand-picked frequencies; with random frequencies it drops to about 0.71 (uniform) and 0.59-0.63 (clustered).",NO,F,"100 runs repo omega; 20 uniform + 20 clustered draws; 440 held-out runs","N=12, repo parameters, dt=0.01","0.995 vs 0.71 / 0.59-0.63; held-out AUC 0.99999 vs 0.972 (repo omega)","known-variant","Chauhan et al. 2022, Sci Rep 12:15003 (ERRATA E12:194)","yes","0.995 association measured in arena files present at first commit add81e6 (2026-10-18), before the first literature search (2026-10-23) and the Chauhan citation (E12, 2026-10-29)","Scope is one omega vector; no dt study",CL.format(45),errata="E1,E8,E9,E12",corr="yes",status="Supported")
add("AUD-TOPO-OMEGA","Which edges survive is largely set by the natural frequencies; the simple rule is informative but not exact, and random frequencies give several possible end networks.",NO,F,"random omega draws, 4 seeds each","N=12, repo parameters","mean pairwise Jaccard 0.514; 1-4 distinct topologies per omega","known-variant","Chauhan 2022; Seliger, Young & Tsimring 2002 (salvage:74)","unclear","audit found it in the same round that listed Seliger 2002; derivation vs recall cannot be separated","Uses mu/(eta+mu)=0.4286 rule; E12 says the settle-above-B_c threshold is 0.4543",CL.format(46),status="Supported")
add("AUD-GATE","The capacity gate is node-strength multiplicative normalisation; it is idempotent but not a metric/KL/Bregman projection.",TH,A,"no-go argument (resp3 2.1) + exact idempotence check","stated domain","idempotent","known","Miller & MacKay 1994, Neural Comput 6:100 (salvage:78,137)","unclear","the audit named it with the citation in hand; the arena had called it a projection","Manuscript/abstract still say 'projected'",CL.format(47),cond="yes",status="Supported (audit-derived)")
add("AUD-SCOPE-1.4","Scope rule: the memory ablation is a 40-seed result; the whole operator/fiber pipeline is a single-seed case study.",DF,A,"scope ruling","AIEF-1.4","1 of 40 seeds","n/a","","n/a","","CF03-CF12 single-seed",CL.format(48),status="Supported")
add("AUD-SLOWPOLE","QUARANTINED: 'the EMA pole is the unique slow pole' was derived from a non-closed 18-coordinate state; on the full 966-dim state 10 rates lie in the gap.",NO,R,"invalid derivation; audit proposal = 1 replay, finite differences","one replay","10 gap rates (0.1893x2, 0.2524x5, 0.6504, 0.6620, 0.6689)","n/a","","n/a","","966-dim result is a proposal, not a proof",CL.format(49),errata="E2",corr="yes (quarantined)",status="Rejected")
add("AUD-RATELAW","On complete, saturated, locked components the exact one-step multiplier on the row-sum-preserving kernel is lambda = (1-gamma dt) s_J (conditions a-e).",TH,A,"derivation + census on replays (finite differences)","conditions (a)-(e); h in ker A_J","374 components; 263 well-resolved agree within 2.1e-10; max gap 2.04e-8 unexplained","known-variant","multiplicative normalisation gives weight-proportional decay: Miller & MacKay 1994 (literature Page row d)","yes (partial)","degree-generated rates (eta/c=6/95) appear in arena file AIEF_HISTORIC_UNFOLDING.md:543 at first commit 2026-10-18, before Miller-MacKay was cited (2026-10-23)","2e-8 gap waits on dt sweep (E5)",CL.format(50),cond="yes",errata="E4,E5",corr="yes",status="Supported")
add("AUD-KAPPA-TW","The slow rate for a component is kappa_k = k*eta/c - 1/T_w (k controlling edges); matches the measured rate.",TH,F,"292 slow components in 200 replays (160 bit-exact)","k=2..5; T_w sweep rho in {0.5..2}","agreement within 5.3e-6; max diff 2.5e-14 on bit-exact","known-variant","as AUD-RATELAW","yes (partial)","same as AUD-RATELAW","Per-degree law; 2eta/c only for k=2",CL.format(51),cond="yes",errata="E4",corr="yes",status="Supported")
add("AUD-FROZEN-TOPO","After the split, no edge ever crosses the threshold again, so predicting the final network from the split state is expected.",NO,F,"440 runs (200 archived repo-omega + 240 random-omega), 29,040 edge records","window up to the run end","0 of 29,040 change; 0 non-binary P_future","n/a","","n/a","","Finite window only; infinite-time needs O1",CL.format(52),status="Supported")
add("AUD-DELAY","Delay is not necessary but not inert: with delay, sampled ensembles show more distinct end networks.",NO,F,"sampled 4-seed ensembles","N=12, tau=0.5 vs 0","diversity statistic, not a basin count","known-variant","Timms & English 2014; Madadi Asl 2017","unclear","audit result; literature listed in the same round","No basin count",CL.format(53),status="Supported")
add("AUD-K3","Ordinary K3 triangles have no two-sided flat direction, only one-sided rays; they are not eigenmodes. Only the exceptional K3 has a two-sided fiber.",TH,A,"argument + census","complete saturated K3","26 isolated K3 (REJ-K3-04)","unchecked","","n/a","","Manuscript 8.2 still says K2/K3 'spectrally silent'",CL.format(54),cond="yes",status="Supported")
add("AUD-TIES","For a fully tied K_n with equal edge weights the one-sided gate derivative has non-additivity 1/sqrt(2k(k-1)) and odd defect sqrt(2/(k+1)); not universal.",TH,A,"derived; K4 counterexample shows non-universality","equal edge weights only","K4: 0.2003 vs 0.2887","unchecked","","n/a","","General ties open (O2)",CL.format(55),cond="yes",corr="yes (equal-weight hypothesis added)",status="Supported")
add("AUD-REPRO13","AIEF-1.3 re-runs reproduce bit-for-bit on the main arrays.",NO,X,"500/500 runs bit-exact on 7 arrays + 4 scalars","same environment","500/500; 78/500 on all 38 keys (rest <=4.9e-15)","n/a","","n/a","","",CL.format(56),status="Supported")
add("AUD-REPRO-B2A95","Run b2a95dfbfbe3 reproduces official run 5a9f093a2fe0 from committed code.",NO,F,"40 seeds","one run hash","max diff 6.7e-16; NaN patterns identical","n/a","","n/a","","E10 NaN check lives on audit/nanfix-v2 (not merged here)",CL.format(57),status="Supported")
add("AUD-NOVELTY","Novelty is not established either way; the ingredients are prior art.",CJ,U,"first-pass search only","whole project","n/a","n/a","","n/a","","Partly stale: an outside literature Page and research/freezing novelty section exist",CL.format(58),errata="E12 (pointer)",status="Incomplete")
add("AUD-LABEL","Labelling rule: audit analyses are 'controlled exploratory analyses with a fixed recorded design'; nothing was preregistered.",DF,A,"rule","audit analyses","n/a","n/a","","n/a","","",CL.format(59),status="Supported")
add("AUD-HELDOUT-LABEL","The held-out target B_final>B_C and P_future>0.5 are the same label in all 440 runs, so per-run 'Pearson' values are point-biserial.",NO,X,"exact label comparison over 440 runs","these 440 runs","0 of 29,040 differ","known (textbook point-biserial)","standard statistics","n/a","","",CL.format(60),status="Supported")
add("AUD-CYCLE-KERNEL","For a fully tied complete graph K_n the relevant kernel (unsigned incidence, not the cycle space) has dimension n(n-3)/2: K3 0, K4 2, K5 5, K6 9.",TH,L,"dimension formula Lean-proved (n=3..6 AIEFProofs; all n>=3 AIEFProofsKn on research/lean-kn); census 373/373 components","non-bipartite K_n, char != 2","373/373; 292/406 agree with slow multiplier (max rel diff 4.5e-4)","known","van Nuffelen 1976; Grossman, Kulkarni & Schochetman 1994 (lean/AIEFProofsKn/README.md:111)","yes","q_s = C(s,2)-s derived in arena file AIEF_HISTORIC_UNFOLDING.md:548 at first commit 2026-10-18, before any literature search","Naming fixed by E6; manuscript Prop 8.1 is the same fact",CL.format(61),cond="yes",errata="E6",corr="yes (naming)",lean="AIEFProofs (n=3..6) + AIEFProofsKn; propext, Classical.choice, Quot.sound",status="Supported (audit-derived)")
add("LEAN-R4","The round-4 Lean package (controller fiber, quotient, complete-graph incidence n=3..6) builds with no sorry and only standard axioms.",TH,L,"7/7 PASS, 115 declarations, 0 warnings (cached build 886daf6)","linear algebra only; no dynamics","115 decls","known (elementary)","","no","","ART-0744/0746 stale hashes (E7); not all projects in lean.yml",CL.format(62),errata="E7",corr="yes (files changed after audit)",lean="AIEFProofs; propext, Classical.choice, Quot.sound",status="Supported")
add("AUD-V4-HELDEVENT","Blocker: v4 held-event detection can miss exact-duration boundaries because of float rounding.",NO,F,"synthetic series only (32 of 605 starts affected)","fixed_physical 17.5 holds","32/605 synthetic","n/a","","n/a","","Real v4 rows not re-checked; v4.1 fix unaudited",CL.format(63),status="Supported")
add("AUD-V4-RECOVERY-WORDING","v4 calls some events 'recovery' that are really retention (never dropped).",DF,A,"code reading + synthetic test","v4 analysis","not counted","n/a","","n/a","","Count of affected events unknown",CL.format(64),status="Supported")
add("AUD-MODULAR-ORACLE","The modular platform is not oracle-certified by the repo tests (oracle test skipped).",NO,F,"pytest: 40 passed/2 skipped default; 41/1 with slow tests","platform tests","40/2; 41/1","n/a","","n/a","","344-array identity not re-run",CL.format(65),status="Supported")
add("AUD-TIMESTEP","OPEN: no dt, dt/2, dt/4 convergence study exists; every number holds for dt=0.01 only.",CJ,U,"none","all numerics","dt=0.01 only","n/a","","n/a","","Load-bearing for all numeric claims",CL.format(66),status="Incomplete")
add("AUD-B-SCAFFOLD","OPEN: 'B is a conditional scaffold' has not been stated as a testable claim or tested.",CJ,U,"none","AIEF-1.4","n/a","n/a","","n/a","","Untested",CL.format(67),status="Incomplete")
add("AUD-CORR-0995-SCOPE","Scope record for 0.995: replication with 15+15 frequency sets x 4 seeds gives uniform mean ~0.75 (median ~0.98) and clustered ~0.53-0.55 with many undefined runs.",NO,F,"20+20 sets first pass; 15+15 sets x 4 seeds replication","N=12, repo parameters","uniform 0.71/0.75; clustered 0.59-0.63 / 0.53-0.55; 37-39 of 60 defined","known-variant","Chauhan 2022 (E12)","yes","same as AUD-CORR-0995","",CL.format(68),errata="E8,E9,E12",corr="yes",status="Supported")
add("AUD-RESP1-UNIFORM","Correction: for uniform frequencies past R beats the frequency-gap predictor on log loss, but on AUC only with delay on.",NO,R,"re-read of audit's own table","uniform omega","no_delay AUC 0.850 vs 0.883","n/a","","n/a","","",CL.format(69),errata="E8",corr="yes",status="Supported (erratum)")
add("RES-FREEZE-01","Conditional freezing theorem: IF every edge's coherence stays in a certified band from step T on, THEN the set of strong edges stops changing after T+N steps, gate included.",TH,A,"paper proof (Lemma 1, Thms 2-3, Cor 4); Lean covers only the per-edge core (upper_geom, eventually_off/on, edge_eventually_off/on; existential N); numerics: 12 runs, 1,412 certified (run,T) pairs, 0 violations over [T,80000)","real arithmetic; default engine path; margin >= 1e-9 guard; repo parameters for numerics","k=6 clique ON margin 0.0067 (5.6% of B_c); 249 of 1,412 pairs have N>0 (max N 1,428); 7-clique gated-OFF needs R spread <= ~2e-4","plausibly new (narrow, elementary)","research/freezing/REPORT.md:276-321 novelty search; nearest: DeLellis et al. 2010 edge snapping","no","no literature match found","O1 closed-loop locking (load-bearing), O2 ties, O3 which support, O4 a-priori N; Lean has existential N only; not in lean.yml",CL.format(70),cond="yes",errata="E12 (pointer)",lean="AIEFFreezeCore (core only, 5 decls); standard axioms",status="Supported (conditional)")
for i,(s,n) in enumerate([("delay cross-feedback gives parametric amplification up to 1e8","1e8"),("QBO imprints in sunspots correlate with Rieger periods","r=0.92 [0.84,0.97], dAIC 12.4"),("60Fe deposits correlate with tidal beats","r=0.85"),("superionic ice phases correlate with piezoelectricity","r=0.92"),("QBO-sunspot tidal model","r=0.75 [0.62,0.85], dAIC 8.2"),("Faraday rotation probes resonantly amplified fields","RM 10-100 rad/m^2"),("SINDy hypergraph inference","F1 ~0.88")]):
    add("SSRH-ORIG-%02d"%(i+1),"ORIGIN idea (not part of the AIEF model): "+s+".",CJ,U,"numbers only in AI-chat text; no script or data in repo","pre-AIEF physics",n,"unchecked","","n/a","","No data, no code",CL.format(71+i),errata="E4",corr="yes (status set to speculative)",status="Speculative")
add("LEAN-KN-01","For every complete graph K_n with n>=3 the unsigned incidence kernel has dimension C(n,2)-n (K12: 54); computer-proved for all n.",TH,L,"Lean 4 AIEFProofsKn, 52 declarations, 7/7 PASS (local); r001_branches audit CLEAN WITH NOTES","n>=3, field of char != 2, connected non-bipartite","K12 = 54","known","van Nuffelen 1976; Grossman, Kulkarni & Schochetman 1994","no","proof route rinv = M^T Q^-1 came from the research sweep (lean/AIEFProofsKn/README.md:109); the fact itself was already rediscovered (see AUD-CYCLE-KERNEL)","Not in lean.yml on this branch (false green until 14c29fe matrix merges); E11 cites README pin but ART-0748 hash stale","registry/claims.csv:70 (research/lean-kn 2fc1110)",lean="AIEFProofsKn; propext, Classical.choice, Quot.sound",errata="E11 (lean-kn branch)",status="Supported")
# ---------- unregistered ----------
MS="AIEF_1_4_OPERATOR_THEORY_MANUSCRIPT.md:{}"
UR="unregistered"
def u(id,stmt,typ,ev,evd,scope,nums,nov,novc,red,redb,gaps,src,cond="yes"):
    add(id,stmt,typ,ev,evd,scope,nums,nov,novc,red,redb,gaps,src,cond=cond,reg=UR,status="not in registry")
u("U-MODEL","Model definition: 12 delay-coupled adaptive Kuramoto oscillators on 66 edges; B+ = lambda*max(0,(1-h)B + h*u), h=gamma*dt, min-endpoint gate lambda=min(1,c/(s+eps)), c=(a-delta)/q=0.6333.",DF,X,"freezing re-implementation matches the engine exactly (0.0) on 80k steps x 3 seeds","dt=0.01, tau=0.5, eta=0.04, gamma=0.015, mu=0.03, B_c=0.12","c=0.6333, T_w=17.5029","known-variant","adaptive Kuramoto (Seliger 2002; Berner et al.)","n/a","","No dt study",  "research/freezing/REPORT.md:109; CURRENT_STATUS.md:88-93",cond="no")
u("U-THRESH","Threshold fact: an ungated edge settles above B_c iff R > (mu+gamma B_c)/(eta+mu) = 0.4543; B*=0 at R=3/7=0.4286.",TH,X,"closed-form algebra (E12)","ungated, constant R","0.4543 vs 0.4286","known (elementary)","","n/a","","AUD-TOPO-OMEGA and the earlier literature Page still use 0.4286 as the rule","ERRATA_2026-10-28.md:188-189")
u("U-CLIQUE","Gated fixed point of a locked k-clique is c/(k-1): k=6 gives 0.12667 (ON, margin 0.0067), k>=7 are OFF ('too many friends').",TH,A,"exact algebra in REPORT; matches runs (19/22/25 ON edges)","fully locked clique, gate active","k=6: 0.12667; margin 5.6% of B_c","known-variant","proportional-share fixed point of multiplicative normalisation, Miller & MacKay 1994 sec 5","unclear","Miller-MacKay was already cited in the audit salvage (2026-10-23) before the freezing note (2026-10-29)","Margin is thin (5.6%)","research/freezing/REPORT.md:127-136,202")
u("U-O1","Open conjecture O1: the closed loop (phases+delay+EMA+gate) always produces locking/drift with a margin, so the freezing theorem applies.",CJ,U,"supported only by 12 finite runs and the 440-run audit record","general","0 violations in 1,412 pairs (finite window)","unchecked","","n/a","","THE most load-bearing gap","research/freezing/REPORT.md:224-232")
u("U-MULTISTAB","Different seeds at the same frequencies end in different networks: 19, 22 or 25 strong edges across 5 repo seeds.",NO,F,"5 repo seeds + 1 no-delay","repo omega","19/22/25 ON edges","known-variant","multistability in adaptive oscillator networks (Berner et al. 2019-2021, salvage:76)","unclear","","Which support appears is open (O3)","research/freezing/results.json; REPORT.md:228",cond="no")
u("U-FLOATGATE","The float gate test agrees with the exact rational test (audit scan +/-40 ulp + 200k random).",NO,X,"exact rational comparison","engine float64","0 disagreements","n/a","","n/a","","Audit-only; not in repo","box-only audit notes (not in repo), AUDIT.md:110-118",cond="no")
u("U-MS-2.1","Manuscript Props 2.1/2.2: the gated map factorises and is linear on each controller fiber.",TH,A,"paper proof","strict branch","n/a","unchecked","salvage:23","n/a","","Not registered; not audited",MS.format("114,134"))
u("U-MS-2.4","Manuscript Props 2.4/2.5/2.7: strict-branch Jacobian, endpoint-tie one-sided derivative, branch persistence.",TH,A,"paper proof","strict branch / ties","n/a","unchecked","","n/a","","2.7 persistence is the same gap as CF12",MS.format("193,234,255"))
u("U-MS-2.14","Manuscript Prop 2.14: dual closure of the fiber.",TH,A,"paper proof","strict branch","n/a","unchecked","","n/a","","Not registered",MS.format(461))
u("U-MS-3","Manuscript Props 3.1/3.2: directed phase increment and EMA tracking-error recurrence.",TH,A,"paper proof (exact identities)","engine update","n/a","known-variant","exponential moving average algebra","unclear","","3.1 uses retired 'projected output' wording",MS.format("534,588"))
u("U-MS-4","Manuscript Props 4.1-4.5: squared-magnitude and alignment identities.",TH,A,"paper proof","engine update","n/a","unchecked","","n/a","","Not registered",MS.format("641-785"))
u("U-MS-5-6","Manuscript Props 5.1-5.2 and 6.1-6.6: fixed-winner K3 block, carrier, nested invariant families (overlap CF06-CF09).",TH,A,"paper proof",P,"n/a","unchecked","","n/a","","Single seed; overlaps registered CF rows",MS.format("831-1049"))
u("U-MS-7.1","Manuscript Prop 7.1: shape of the projected defect matrices (relates to S16 replacement).",TH,A,"paper proof + POD match",P,"n/a","unchecked","","n/a","","'projected' wording",MS.format(1130))
u("U-MS-8.1","Manuscript Prop 8.1 / Cor 8.2: complete-component lineality dimension C(s,2)-s; K2 and K3 'spectrally silent'.",TH,A,"paper proof; dimension part later Lean-proved (LEAN-KN-01)","complete saturated components","K3 0, K4 2, K5 5, K6 9","known","van Nuffelen 1976; Grossman et al. 1994","yes","present at first commit 2026-10-18, before any literature search","'Spectrally silent' wording retired by AUD-K3 but still in manuscript (no erratum)",MS.format("1198,1248"))
u("U-MS-8.3","Manuscript Props 8.3/8.5: frozen-driver scalar action and finite-step contraction rate (overlap AUD-RATELAW).",TH,A,"paper proof","locked saturated components","eta/c = 6/95","known-variant","Miller & MacKay 1994","yes (partial)","as AUD-RATELAW","2e-8 gap",MS.format("1303,1392"))
u("U-MS-9","Manuscript Props 9.1/9.2: biorthogonal scalar recurrence and Duhamel decomposition.",TH,A,"paper proof",P,"n/a","known-variant","standard variation-of-constants (Duhamel) formula","unclear","no literature comparison in files","Not registered",MS.format("1470,1504"))
u("U-MS-10","Manuscript Props 10.1-10.3: under a resonant source the EMA tracking error has a Jordan-type n*r^n solution.",TH,A,"paper proof",P,"n*r^n form","known","repeated-root solutions of linear recurrences (e.g. Elaydi, An Introduction to Difference Equations, 3rd ed. 2005, ch. 2); citation added by this map, not in repo","yes","derived with proof in the manuscript present at first commit 2026-10-18; no literature cited in the files","Not registered",MS.format("1534-1597"))
u("U-MS-11","Manuscript Prop 11.1: relative-retention memory rate (replaces the retired 'loop gain' S14).",TH,A,"paper proof (conditional triangular reduction)",P,"n/a","unchecked","","n/a","","Not registered",MS.format(1667))
u("U-CPE","Proposal-equalization note Thm 6.2 and Thm 10.1: alignment decay => resonance equalization => proposal equalization => branch-matrix closure.",TH,A,"paper proof; alignment decay itself is an observed input",P,"t<=320","unchecked","","n/a","","Alignment decay not derived from the dynamics; bridge note calls it 'supported on the finite record'","AIEF_1_4_CONDITIONAL_PROPOSAL_EQUALIZATION_THEOREM.md:346,544")
u("U-CFTP","Controller-fiber package Props 2.1-10.1; open theorem in sec 13.",TH,A,"paper proofs",P,"n/a","unchecked","","n/a","","Sec 13 open","AIEF_1_4_CONTROLLER_FIBER_THEOREM_PACKAGE.md:640")
u("U-NONRESULTS","Manuscript sec 14 non-results list (e.g. no full-system Jordan block established).",DF,A,"explicit list","whole program","n/a","n/a","","n/a","","",MS.format(1794),cond="no")
# ---------- write ----------
# ================= REVISION 2: Auditor Seat 002 fix list (2026-10-29) =================
# Every change below is keyed to the audit's fix-list item (F1..F8) or new-inconsistency number (N1..N11).
RID={r["id"]:r for r in rows}
for r in rows: r["lean_in_ci"]=""
def setr(i,**kw):
    for k,v in kw.items(): RID[i][k]=v
YARD=("yardstick: derived before THAT specific paper was cited (dated via chat histories h01-h10 and later commits); "
      "the Berner et al. 2023 review (arXiv:2304.05652) was already in the repo at add81e6, so 'before any literature' is not claimed")
# F1/F2: validation column rewritten against the per-paper yardstick
for i in ["AUD-CYCLE-KERNEL","U-MS-8.1"]:
    setr(i,independent_rediscovery_validation="yes (textbook-level)",
         rediscovery_basis="derived in manuscript Prop 8.1 (MS:1198, add81e6) and chat history h03:16759 before van Nuffelen / Grossman et al. were cited (lean-kn README:111, bot-added); caveat: h03:43270 states the general rank theorem from memory (recall). "+YARD)
setr("U-MS-10",independent_rediscovery_validation="yes (textbook-level)",
     rediscovery_basis="derived with proof in MS:1534 (add81e6) and h03:25869; Elaydi citation added by this map, not in repo; caveat: h03:26349 calls it 'the canonical discrete Jordan block' (recall). "+YARD)
for i in ["AUD-CORR-0995","AUD-CORR-0995-SCOPE"]:
    setr(i,independent_rediscovery_validation="no (designed-in; see E12)",novelty_citation="closest prior art: Seliger, Young & Tsimring 2002 PRE 65:041906, cited in the Berner 2023 review present at add81e6 (paper.txt:5308); Chauhan 2022 moved to AUD-TOPO-OMEGA",
         rediscovery_basis="E12 (ERRATA:188-196) calls the association 'the mechanism working as designed'; Chauhan 2022 reports a frequency-degree correlation, a loose match to this statistic. "+YARD)
setr("AUD-TOPO-OMEGA",independent_rediscovery_validation="yes (partial)",novelty_citation="Chauhan et al. 2022 Sci Rep 12:15003 (frequency-degree correlation; cited via E12); Seliger, Young & Tsimring 2002",
     rediscovery_basis="Chauhan's frequency-degree result fits this row better than the 0.995 statistic; derivation order vs Chauhan cannot be dated precisely from git (bulk uploads), so partial. "+YARD,
     open_gaps="States the rule symbolically as mu/(eta+mu) (=3/7=0.4286, where B*=0); E12 gives 0.4543 as the settle-above-B_c threshold")
setr("U-MULTISTAB",independent_rediscovery_validation="no (literature in repo first)",novelty_citation="Berner et al. 2023 Physics Reports review (arXiv:2304.05652) sec 14.6 multistability in adaptive networks; owner-supplied PDF in repo at add81e6",
     rediscovery_basis="the review covering this result was in the repo at the first commit. "+YARD)
for i in ["AUD-RATELAW","AUD-KAPPA-TW","U-MS-8.3"]:
    setr(i,independent_rediscovery_validation="unclear",rediscovery_basis="Miller & MacKay match is an analogy only (bot-added, salvage f7246a3, 2026-10-23); degree-generated rates appear at HU:543 (add81e6). "+YARD)
for r in rows:
    v=r["independent_rediscovery_validation"]
    if v=="no": r["independent_rediscovery_validation"]="no (route from literature)" if r["id"]=="LEAN-KN-01" else "no (no literature match claimed)"
# F3/N8: evidence-level changes and CI flags
setr("AUD-CYCLE-KERNEL",evidence_level=A,evidence_detail="argument only overall (the claim is mainly that the round-2 matrix is not a Jacobian and the right object is the multiplier on K); dimension part Lean-proved (AIEFProofs n=3..6, in CI; AIEFProofsKn all n, branch-only); census 373/373 components")
RID["AUD-CYCLE-KERNEL"]["lean_in_ci"]="partly: AIEFProofs (n=3..6) in CI; AIEFProofsKn branch-only, not in CI"
RID["LEAN-R4"]["lean_in_ci"]="yes (AIEFProofs in lean.yml)"
RID["LEAN-CF-01"]["lean_in_ci"]="yes (AIEFProofs in lean.yml)"
RID["CF06"]["lean_in_ci"]="yes (AIEFProofs in lean.yml); applicability rests on CF05 (one seed)"
RID["LEAN-KN-01"]["lean_in_ci"]="no: branch-only (research/lean-kn), not in CI"
RID["RES-FREEZE-01"]["lean_in_ci"]="no: Lean core branch-only (research/freezing), not in CI"
# F4/N5: reclassifications and the withdrawn/live split
setr("U-THRESH",evidence_level=A,evidence_detail="hand algebra (E12); no script or proof computes 3/7 and 0.4543 exactly")
setr("U-MODEL",evidence_level=F,evidence_detail="freezing re-implementation agrees bitwise in float64 (diff 0.0) with the engine on 80k steps x 3 seeds; finite runs, not exact arithmetic")
setr("AUD-KAPPA-TW",evidence_level=A,evidence_detail="derived formula; census of 292 slow components in 200 replays (160 bit-exact) checks it numerically")
setr("AUD-RESP1-UNIFORM",evidence_level=F,evidence_detail="live, Supported correction (erratum E8) from a re-read of the audit's own table; not a withdrawal")
# N6: missing erratum
setr("AUD-REPRO-B2A95",errata="E10 (audit/nanfix-v2 cbf2ae7)")
# F6/N9: full owner label
for r in rows:
    if r["id"].startswith("SSRH-ORIG"): r["status_in_registry"]="Speculative / untested origin hypothesis"
# 0.4286 nuance (audit item 6): shuffle result holds under either threshold
setr("EMP-AIEF13-01",open_gaps="Outcome forced by construction (shuffled mean R 0.371 is below both 3/7=0.4286, where B*=0, and the 0.4543 settle-above-B_c threshold, so D_B=0); not preregistered")
setr("U-THRESH",open_gaps="AUD-TOPO-OMEGA states the rule as mu/(eta+mu)=3/7; the Research Sweep Page used 0.4286 for freezing (corrected to 0.4543 on 2026-10-29)")
# N10/N11
RID["RES-FREEZE-01"]["key_numbers"]+="; 246 of the 249 N>0 pairs come from 2 runs (random_omega_U[1,2]#0 and stress_near_identical, 123 each) + 3 single reset_B pairs"
# AUD-NOVELTY (inconsistency 15)
RID["AUD-NOVELTY"]["open_gaps"]="Partly stale: E12, the research sweep and the lean-kn README added literature later, and the Berner review PDF was in the repo from day one"
# ================= end REVISION 2 =================
out=os.path.join(HERE,"claims_map.csv")
with open(out,"w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
C=collections.Counter
reg=[r for r in rows if r["registry"]=="registered"]
V=lambda r: r["independent_rediscovery_validation"]
yes=[r["id"] for r in rows if V(r).startswith("yes (textbook")]
part=[r["id"] for r in rows if V(r).startswith("yes (partial")]
unc=[r["id"] for r in rows if V(r)=="unclear"]
rej=[r["id"] for r in rows if V(r).startswith("no (designed-in") or V(r).startswith("no (literature in repo")]
route=[r["id"] for r in rows if V(r).startswith("no (route")]
distinct_yes={"K_n unsigned-incidence kernel dimension C(n,2)-n (van Nuffelen 1976; Grossman, Kulkarni & Schochetman 1994)":["AUD-CYCLE-KERNEL","U-MS-8.1"],
              "Jordan-type n*r^n solution under resonance (repeated-root linear recurrences; Elaydi 2005, citation added by this map)":["U-MS-10"]}
distinct_part={"frequency shapes final topology (Chauhan et al. 2022 frequency-degree correlation)":["AUD-TOPO-OMEGA"]}
assert sorted(sum(distinct_yes.values(),[]))==sorted(yes) and sorted(sum(distinct_part.values(),[]))==sorted(part)
ev=C(r["evidence_level"] for r in rows)
withdrawn=[r["id"] for r in rows if r["evidence_level"]==R]
live_corr=[r["id"] for r in rows if r["evidence_level"]!=R and ("erratum" in r["status_in_registry"] or "correction" in r["evidence_detail"].lower())]
lean_primary=[r["id"] for r in rows if r["evidence_level"]==L]
lean_backed=[r["id"] for r in rows if r["lean_project_and_axioms"]]
lean_not_ci=[r["id"] for r in rows if r["lean_in_ci"].startswith("no")]
# ---------- inconsistencies (original 15 as rated by the audit, plus N1-N11) ----------
INC=[
 ("1","CURRENT_STATUS.md:84 says '75 rows' and line 3 'Last Verified 2026-10-23'; research/freezing and research/lean-kn have 76 (75 is correct on nanfix-v2 and merge-prep)","confirmed","open (repo follow-up)"),
 ("2","RES-FREEZE-01 (freezing) and LEAN-KN-01 (lean-kn) both sit at claims.csv:70 and both carry study_id AI_AGENT_AUDITS_2026_10 although neither came from an audit round; they will merge-conflict","confirmed","open (repo follow-up)"),
 ("3","(dropped) 'RES-FREEZE-01 says explicit N but Lean has only existential N' - every source already says explicit N is paper-level and Lean has existential N","wrong (no inconsistency)","dropped"),
 ("4","Stale artifact hashes: 5 of 9 Lean artifacts (ART-0743, 0744, 0745, 0746, 0748; artifacts.csv:744-749) do not match the files; 0747 and 0749-0751 match. AIEFProofsKn and AIEFFreezeCore are not registered as artifacts at all. ART-0743..0751 describe every Lean file as 'ker(C_{2,7})'","right but understated (widened)","open (repo follow-up)"),
 ("5","README.md:75 still says no literature review has been done; the Lean section (README.md:57) omits AIEFProofsKn and AIEFFreezeCore","confirmed","open (repo follow-up)"),
 ("6","0.4286 used as a persistence/freezing threshold where 0.4543 applies (3/7=0.4286 is where B*=0; 0.4543 is the settle-above-B_c threshold, ERRATA:189, REPORT.md:213): claims.csv:2 note, build_claims_reconciliation.py:49, AIEFS_audit_response.md:21, this map's EMP-AIEF13-01 row (fixed), and Research Sweep Page:227 (fixed 2026-10-29); claims.csv:46 states it symbolically as mu/(eta+mu). The shuffle result (mean R 0.371) holds under either threshold","confirmed with nuance","map + Research Sweep Page fixed; repo open"),
 ("7","ERRATA:30 (E1) still says 'on clustered omega it does worse'; ERRATA:150-151 (E8) calls that an overstatement","confirmed (minor)","open (repo follow-up)"),
 ("8","EMP-AIEF14-01 note quotes 0/29,040 edges (from the 440-run audit set) under a '40 paired seeds' scope","confirmed","open (repo follow-up)"),
 ("9","Manuscript abstract and Props 2.10/3.1/7.1 keep 'projected' (retired by AUD-GATE); Cor 8.2 at MS:1248 still says 'spectrally silent' (retired at README.md:73 and audit responses 2-3) with no erratum","confirmed","open (repo follow-up)"),
 ("10","CF05/CF10 status Supported although single-seed and never re-checked (the row itself discloses this)","partly right","open"),
 ("11","EMP-AIEF13-02 caveat is broader than the audit wording (the row's own note flags it)","confirmed","open"),
 ("12","lean.yml triggers on lean/** but builds only lean/AIEFProofs: a change to Kn or FreezeCore gives a green run that never built it","confirmed","open (fix pushed as 14c29fe, unmerged)"),
 ("13","Validator default --edited-since ce8cced is not in any pushed ref (validate_registry_against_tree.py:50 on merge-prep, nanfix-v2, freezing, lean-kn); fixed only on unmerged ci/validator 249ea3f","confirmed","open (repo follow-up)"),
 ("14","SSRH-ORIG-04 r=0.92 comes from chat text with no data (the row already says so)","partly right","no action needed beyond label"),
 ("15","AUD-NOVELTY scope still says first-pass search only; later literature work (E12, sweep, lean-kn README) and the day-one review PDF are not reflected","partly right","open (repo follow-up)"),
 ("N1","MAP_NOTES.md had no inconsistency list (items lived only on the Page)","new (audit)","fixed: list generated into MAP_NOTES.md and inconsistencies.csv"),
 ("N2","Four hand-added totals.json keys (lean_note, validation_hits.distinct_results_yes, distinct_results_yes_partial, headline) were not produced by build_map.py","new (audit)","fixed: all totals keys generated by build_map.py"),
 ("N3","The rediscovery yardstick and the U-MULTISTAB call ignored the Berner 2023 review that was in the repo at add81e6","new (audit)","fixed: per-paper yardstick; U-MULTISTAB = no"),
 ("N4","Chauhan 2022 was attached to AUD-CORR-0995 although it fits AUD-TOPO-OMEGA","new (audit)","fixed: moved to AUD-TOPO-OMEGA (partial)"),
 ("N5","The 26 'withdrawn or corrected' included the live correction AUD-RESP1-UNIFORM","new (audit)","fixed: 25 withdrawn + live corrections listed separately"),
 ("N6","AUD-REPRO-B2A95 has erratum E10 (audit/nanfix-v2 cbf2ae7; its claims.csv note cites it) but the map showed none","new (audit)","fixed"),
 ("N7","tools/sync/SHA256SUMS covers only the sync scripts and tools/sync/README.md, not the root README or any Lean file, so it does not back the Lean claims","new (audit)","noted (repo follow-up); per-project Lean SHA256SUMS do verify"),
 ("N8","The Page's Lean-proved definition left out the CI requirement; 2 of 3 Lean projects are not in CI","new (audit)","fixed: definition + lean_in_ci column"),
 ("N9","SSRH-ORIG rows showed 'Speculative' (CSV) or no label (Page) instead of the owner's full label 'Speculative / untested origin hypothesis'","new (audit)","fixed"),
 ("N10","246 of the 249 N>0 freezing pairs come from 2 runs (random_omega_U[1,2]#0 and stress_near_identical, 123 each) plus 3 single reset_B pairs","new (audit)","fixed: stated in row, totals and Page"),
 ("N11","The Page and README never said the 249 N>0 pairs come from 2 runs","new (audit)","fixed on the Page; README open (repo follow-up)"),
]
with open(os.path.join(HERE,"inconsistencies.csv"),"w",newline="") as f:
    w=csv.writer(f); w.writerow(["id","inconsistency","audit_rating","status_after_revision_2"]); w.writerows(INC)
tot=dict(generated="2026-10-29 (America/Toronto), revision 2 after Auditor Seat 002",sources={"research/freezing":"cc31533","research/lean-kn":"2fc1110"},
 rows_total=len(rows),registry_rows=len(reg),registry_rows_note="76 on research/freezing and on research/lean-kn, 75 on merge-prep, nanfix-v2, ci/validator and ci/artifact-pins; union 75+2=77 (RES-FREEZE-01 only on freezing, LEAN-KN-01 only on lean-kn)",
 unregistered_rows=len(rows)-len(reg),
 by_type_all=dict(C(r["type"] for r in rows)),by_type_registry=dict(C(r["type"] for r in reg)),
 by_evidence_all=dict(ev),by_evidence_registry=dict(C(r["evidence_level"] for r in reg)),
 lean_backed_rows=lean_backed,lean_proved_primary=lean_primary,lean_backed_not_in_ci=lean_not_ci,
 lean_note="%d rows have Lean as primary evidence (%s), all linear-algebra facts; %d rows have some Lean backing. Lean-proved here means: builds, source SHA256SUMS verifies, no sorry/admit/axiom, standard axioms only (propext, Classical.choice, Quot.sound). Only AIEFProofs is in CI; %s rest on branch-only projects. No Lean proof covers the coupled dynamics."%(len(lean_primary),", ".join(lean_primary),len(lean_backed),", ".join(lean_not_ci)),
 conditional_rows=sum(r["conditional"]=="yes" for r in rows),conditional_registry=sum(r["conditional"]=="yes" for r in reg),
 rows_citing_errata=sum(bool(r["errata"]) for r in rows),
 rows_wording_or_status_corrected=sum(r["wording_or_status_corrected"]!="no" for r in rows),
 withdrawn_rows=len(withdrawn),live_corrections=live_corr,
 validation_hits={"yardstick":YARD,"yes_textbook_level":yes,"yes_partial":part,"unclear":unc,"no_claimed_match_rejected":rej,"no_route_from_literature":route,
   "count_rows_yes":len(yes),"count_distinct_yes":len(distinct_yes),"count_partial":len(part),"count_distinct_partial":len(distinct_part),
   "count_unclear":len(unc),"count_no_rejected":len(rej),"distinct_results_yes":distinct_yes,"distinct_results_partial":distinct_part,
   "headline":"%d distinct textbook-level rediscoveries (%d rows) + %d partial (%d row); %d unclear; %d claimed matches rejected"%(len(distinct_yes),len(yes),len(distinct_part),len(part),len(unc),len(rej))},
 lean_projects={"AIEFProofs":"115 declarations, standard axioms, 7/7 PASS, in lean.yml (CI)","AIEFProofsKn":"52 declarations, standard axioms, 7/7 PASS locally, branch-only (research/lean-kn), NOT in CI","AIEFFreezeCore":"5 core declarations, standard axioms, 7/7 PASS locally, branch-only (research/freezing), NOT in CI"},
 parameter_coverage={"N_oscillators":"12 only (one value)","dt":"0.01 only (AUD-TIMESTEP: no convergence study)","tau":"0.5 and 0 (no_delay) only",
   "eta_gamma_mu_Bc_a_q_delta":"one fixed set (0.04, 0.015, 0.03, 0.12, 1, 1.5, 0.05)","T_w":"5 values rho in {0.5,0.75,1,1.5,2} (AIEF-1.4 T_w study only)",
   "omega":"repo vector (most results) + 20 uniform + 20 clustered draws (audit) + 15+15 sets x4 seeds (replication) + 2 random + 1 near-identical stress (freezing)",
   "seeds":"100 paired (AIEF-1.3), 40 paired (AIEF-1.4), 500 repro runs, 440 audit runs, 12 freezing runs",
   "freezing_numerics":"12 runs, 1,412 certified (run,T) pairs, 0 violations; 249 pairs with N>0 (max N 1,428), of which 246 come from 2 runs (random_omega_U[1,2]#0 and stress_near_identical, 123 each) and 3 from single reset_B pairs; all at one parameter set",
   "claimed_scope":"theorems are stated for general parameters; README wording 'topology set by omega' reads general; every numeric check is at a single point of the 7 rate constants and dt"},
 most_load_bearing_gaps=["O1 closed-loop locking with margin (RES-FREEZE-01, AUD-FROZEN-TOPO interpretation)","AUD-TIMESTEP: no dt convergence study (all numerics)","AUD-SCOPE-1.4/CF12: CF chain single-seed; infinite-time branch persistence open"],
 inconsistencies={"original_items":15,"dropped":1,"kept":14,"new_from_audit":11,"total_listed":len(INC),"fixed_or_partly_fixed_in_map_or_pages":sum(x[3].startswith("fixed") or "fixed" in x[3].split(";")[0] for x in INC)})
json.dump(tot,open(os.path.join(HERE,"totals.json"),"w"),indent=1)
# ---------- MAP_NOTES.md (generated) ----------
NOTES=["# AIEFS project map: method and caveats (revision 2, 2026-10-29, America/Toronto)","",
"Generated by build_map.py. Revision 2 applies Auditor Seat 002's prioritized fix list.","",
"## What was read (read-only)",
"- `git show` from research/freezing @ cc31533 and research/lean-kn @ 2fc1110: registry/claims.csv, artifacts.csv, supersessions.csv, studies.csv, ERRATA_2026-10-28.md, CURRENT_STATUS.md, README.md, research/freezing/REPORT.md and results.json, lean/AIEFProofsKn/README.md, the AIEF-1.4 manuscript and theorem notes, and the AI Agent Audits salvage.",
"- Box-only audit notes (not in the repo) and Auditor Seat 002's audit, including its dating of results against the chat histories h01-h10.",
"- Nothing was cloned, built, compiled, committed or pushed. No pinned file was touched.","",
"## Rows",
"- 77 registry rows: 76 on each research branch; the union adds RES-FREEZE-01 (freezing) and LEAN-KN-01 (lean-kn), both at claims.csv:70.",
"- 21 unregistered rows: substantive claims in the manuscript, theorem notes, REPORT and ERRATA with no ledger row. Manuscript propositions are grouped by section.","",
"## Evidence levels",
"- Each row gets the strongest evidence for its CURRENT wording; corrections are tracked in separate columns.",
"- Lean-proved = the project builds, its source SHA256SUMS verifies, it has no sorry/admit/axiom, and `#print axioms` shows only propext, Classical.choice and Quot.sound. Column lean_in_ci says whether CI builds it; only AIEFProofs is in CI.",
"- Retracted/corrected = the claim was withdrawn. Live corrections (e.g. AUD-RESP1-UNIFORM, a Supported erratum) keep their numeric level.",
"- Revision 2 changed 5 rows: AUD-CYCLE-KERNEL Lean->argument (dimension part Lean-proved); U-THRESH exact->argument; U-MODEL exact->floating-point; AUD-KAPPA-TW floating-point->argument; AUD-RESP1-UNIFORM retracted->floating-point.","",
"## Independent rediscovery / validation",
"- Yardstick: a result counts as rediscovered only if it was derived before THAT specific paper was cited. The Berner et al. 2023 review (arXiv:2304.05652) was in the repo at the first commit add81e6, so 'before any literature' is not claimed. Git cannot date anything inside the 866-file first commit; only the chat histories give an internal order. Everything else is unknowable and marked unclear.",
"- Every literature citation in the repo was added by a bot; the only owner-supplied literature is the Berner review PDF.",
"- Result: "+tot["validation_hits"]["headline"]+". Both hits are textbook facts: real, specific matches, but weak as validation. The chat histories also show recall (h03:43270, h03:26349), which the files cannot separate from derivation.",
"- The Elaydi 2005 citation for U-MS-10 was added by this map and is not in the repo.","",
"## Unknowns",
"- Whether CF05/CF10 still hold (never re-checked); how many v4 'recovery' events are really retention; whether v4.1 changes real held-event rows.","",
"## Inconsistencies (also in inconsistencies.csv)"]
for i,t,rt,st in INC: NOTES.append("- **%s** (%s; %s) %s"%(i,rt,st,t))
NOTES+=["","## Parameter coverage","- "+tot["parameter_coverage"]["freezing_numerics"],"- Every numeric check is at N=12, dt=0.01 and one set of the seven rate constants; only tau, T_w and omega vary.",""]
open(os.path.join(HERE,"MAP_NOTES.md"),"w").write("\n".join(NOTES))
print(json.dumps({k:tot[k] for k in ["rows_total","registry_rows","unregistered_rows","by_type_all","by_evidence_all","by_evidence_registry","conditional_rows","rows_citing_errata","rows_wording_or_status_corrected","withdrawn_rows","live_corrections","lean_proved_primary","lean_backed_rows","lean_backed_not_in_ci","inconsistencies"]},indent=0)); print(tot["validation_hits"]["headline"]); print("unclear",unc); print("rejected",rej)
