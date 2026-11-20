# 011 preregistration — modulo-safe delayed phasor increment and chord bound

Researcher040282; prepared2026-09-04 Atlantic/Reykjavik (session label). Prior
owner/repository November labels and runtime/compiler clocks remain separate.
This fixes the protocol BEFORE any011 acquired-engine execution or theorem
compilation. So far: public source/feedback/API inspection and mathematical design.

## Fresh scope / intake / no duplicate provenance work

Current main eb3933c196ee19e80e1621ae80d89ca72e6d9485:32 selected texts (claims
inventory deliberately not fetched; includes one matched-phase anchor test read
statically only). Current inbox4fbd00b6e5f975b49bd74885e8c381af9abaf9f7:8 selected
notes/evidence after adding new trust-anchor Part5 review/evidence ONLY. Its
contributed regression reproducer not fetched/executed, its design not approval
of009/010. Targeted R040282/R001/general TRIAGE unchanged. Do not duplicate guard,
rate-law, uploader/checksum or chronicler work. One public open PR16 unrelated;
16Git branch names, no relevant phase/phasor/history/delay/wrap/increment match.
Selected Lean scopes exclude phase/delay; header/keyword inspection no matching
implementation. Limited public navigation, not exhaustive/private-work assurance.

GitHub API403 quota failure preserved under development. Read-only Git refs and
shallow BLOBLESS tree navigation + raw selected-file fetch succeeded; public PR
HTML independently read. NUL-delimited tree parsing corrects initial Unicode path
quoting BEFORE any science; no new-file finding inferred from quoted rendering.
Raw Git objects remain in own excluded disposable cache, not outgoing metadata.

Actual frozen ART-0702 engine imported intact. No edits/replacements/monkeypatches,
source/registry/lock change, full production/baseline study, run_seed/simulate_*,
shuffle/intervention/CLI/writer/certificate, real S01, remote push/PR/contact/upload
or unattended012. Reuse unchanged010 history module/scalar oracle as explicit
owned components, not rerunning historical010 suite or modifying its evidence.

## One mathematical bridge, three intended named claims

Let P=2*pi. Define the IDEAL-REAL wrap W(t)=t-floor(t/P)*P; phasor E(t)=exp(i*t).
For arbitrary real initial vector x0 and arbitrary unwrapped increments
u:Nat->(index->Real), define x(n+1,i)=W(x(n,i)+u(n,i)). Constants omega,tau need
not obey a synchronization assumption. Use010's constant-initialized D+1 history
H(n), so oldest=x(max(0,n-D)). Define actual-shaped coherence input

 z(n,i,j)=E(x(n,i)-H(n)[0](j)-((omega_i+omega_j)/2)*tau).

Define delayed increment L(n,j)=0 when n<D, otherwise u(n-D,j), and
v(n,i,j)=u(n,i)-L(n,j). Prove in the prescribed Lean/Mathlib toolchain:

1 E(W(t))=E(t), with explicit floor-based wrap, not an assumed periodicity axiom.
2 z(n+1,i,j)=z(n,i,j)*E(v(n,i,j)), ALL n, including n=D-1 and first live n=D.
3 ||z(n+1,i,j)-z(n,i,j)|| <= |v(n,i,j)|.

Only three new named main declarations intended. Recompile unchanged010 history
as dependency, not three new labels. Main imports targeted Mathlib trigonometric
Bounds/floor/real and Ring/FieldSimp/NormNum/Linarith, not omnibus Mathlib/Tactic.
Footprints subset{propext,Classical.choice,Quot.sound}; complete named axiom-print
coverage, no main warnings/errors/sorry/admit/native_decide/extra axioms/unsafe.
Preserve development errors, never count as planned falsifiers or compiled claims.

The recurrence is a definition, not the desired phasor identity assumed as a
premise. Arbitrary forcing u can represent dt*(omega_i+coupling_i), where source
coupling uses NEW gated B and old delayed-current sine. This universality permits
feedback instantiation but does NOT formalize C/R/B, Python allocations, actual
floating remainder/trigonometry, whole coupled evolution, locking or convergence.
The formal real wrap is a mathematical model of remainder, not verified NumPy FFI.
Source configurations retain positive dt/tau and exact D*dt=tau, hence D>=1;
abstract D0 is mathematically covered only, not a source-valid configuration.

Paper-only specialization if post-gate nonnegative row sum<=c:
startup bound dt*(|omega_i|+c); live bound dt*(|omega_i-omega_j|+2*c), dt>=0.
This follows |sum B*sin|<=c, not a synchronization assumption. Not a new Lean gate
or capacity/composition theorem; generic signed-increment chord bound is formal.
Ordinary stored-angle differences can jump2*pi: do NOT replace the circular/phasor
bound by a Euclidean representative bound. Conversely exp(i*(stored_new-old)) is
legitimately equal to exp(i*u) modulo winding: test as a POSITIVE, not a mutant.
The mean-frequency offset cancels from the ratio, but matters in absolute input;
ratio-only checks cannot detect omitting that constant.

## Fixed independent synthetic design and numeric tolerances

All source expected traces precomputed using immutable tuple cases, pure math/
cmath scalar oracle reused unchanged from010, BEFORE acquired module import.
For each synthetic case initialize history as D+1 equal value copies of specified
x0 (constructor later makes independent arrays), C0=0, B as below. Seven cases,
EIGHT advances each, INPUT phasors z0..z7, ADJACENT input ratios n0..6 only:

- N3,D1,theta(2*pi-.015,1.27,4.13),omega(.5,1,1.5), active eta3;
- N3,D2,theta(.31,1.27,4.13),sameomega/active;
- N3,D3,same theta/omega/active;
- N4,D4,theta(.31,1.27,4.13,2.71),omega(.5,1,1.5,1.25),active;
- N3,D2,theta(.01,1.27,4.13),omega(-1,.75,1.5),active (negative wrap);
- N3,D2,theta(.31,1.27,4.13),omega(161,-143,27),active (multiple windings);
- N1,D3,theta(6.1),omega1,B0,eta=mu=gamma0 (free drift/startup/positive wrap).

Common dt=.125,tau=D*.125,Twindow=.5,a1,q1.5,delta.1,epsilon1e-12,mu.05,gamma.2;
N3 B edges(.08,.23,.32); N4 Bij=.04*(1+i+j) offdiag, diag0. C0 all complex0,
B_c=B_init_scale0. This is manual synthetic initialization, not a claim random
production initialize_state returns these exact values. No initializer calls.

Expect 56actual advances/common suite,496 full complex input coordinates,
434adjacent pair coordinates:157startup/277live, of which62first-live at n=D.
Actual source updates C with z_n BEFORE updating phase; observing z_(n+1) requires
the NEXT advance. Do not mislabel a post-call C innovation as next-time input.
Observed innovations=(C_after-alpha*C_before)/(1-alpha), with copied ACTUAL old C
as observed data only; independent expected z_n/phase/forcing never from target.
Alpha=exp(-.25), safely away from1; no unstable tiny denominator in this domain.
Never pre-call mutating compute_R. Also compare C/B/theta/history and physical/
driver R to scalar prediction. Reused expected shadow only from oracle outputs.

Fixed absolute5e-13,relative0 for finite real/imag components, unwrapped-winding
residuals, phasor/ratio residuals and one-sided chord/capacity bound slack. Exact
shape/boolean/count/history storage/RNG/input preservation checks; no known NaN-
masking whole-element predicate. No tolerance tuning after source results.
Require each wrong numeric witness>1e-7, not tolerance fuzz. Case-design scalar
numbers may be inspected before engine execution; if a chosen witness is vacuous,
record blocker/plan amendment before execution rather than crediting it.

## Same nine source methods normally and -O

1 all7x8 complete source/scalar traces and input innovations,56actual calls;
2 startup L=0, including frozen N1 input rotating until delay becomes live;
3 first live read n=D, not n=D+1;
4 later live age n-D, not current delayed-node increment;
5 positive/negative/multiple integer windings; raw-difference equality counterexample
  AND representative-phasor equality as legitimate positive;
6 chord bound signed v and paper row-capacity specialization; nonzero chord with
  bound<2 must occur, not merely a vacuous universal2 bound;
7 absolute mean-frequency-offset input, plus legitimate ratio cancellation;
8 NEW gated B forcing nonvacuity against old/unprojected B; independent history
  storage, immutable cases and RNG preservation;
9 C reads z_n before phase/append; exact observation counts, no extra compute_R.

Only method1 makes actual calls; others inspect those fixed immutable observations.
Expect nine methods PASS/0errors/0skips normally/-O. No repair/red-before claim.

## Ten wrong models, each mode; fixed independent witness positions

All are checker falsifiers, never injected into or substituted for engine functions.
Base active-D2 at n/i/j unless stated:
1 omit startup guard: n0,0,1 subtract u0j;
2 one-step-early delayed read: n1,0,1 subtract u0j;
3 current delayed-node increment: n3,0,1 subtract u3j instead of u1j;
4 one-extra delay: n2,0,1 subtract0 instead of u0j;
5 reverse increment difference: n3,0,1;
6 old B current increment: n0,0,1;
7 unprojected B current increment: n0,0,1;
8 omit mean-frequency offset: absolute z0,0,1 (ratio alone would not detect);
9 next-step C input timing: z0 claimed z1,0,1;
10 raw stored-angle difference equals unwrapped increment: multiwrap-D2,n0,node0.

Expected fields: factor for1..7, absolute_input for8..9, real_increment for10.
All numeric component witnesses>1e-7. Import/setup/timeouts must BLOCK rather than
be mistaken for semantic detection. Normal/-O non-timing records match.

## Eight formal controls, compiler resource and closeout

Two nonzero positives (startup D1 and live delayed increment); three false math
witnesses (no-wrap W(2*pi)=2*pi; subtract delayed increment during startup; use
current instead of aged delayed increment); compiling sorry/added-axiom payloads
rejected by policy and compiling omitted-print rejected by coverage. Raw compiler
outcomes and intended mathematical/policy reasons required. False math import/
unknown-identifier/runtime/timeout failures never count as rejection.

Lean/lake/old cache absent,20GB free observed. Select prescribed current project
Lean4.33.1 and Mathlib revision from acquired lake-manifest. Recorded official
Lean570405234B asset info inherited from010, fresh API quota unavailable; verify
actual download against recorded length/published digest. Install ONLY into own
excluded .cache/researcher040282-cycle011; complete runtime needed for Lake/cache
helper, targeted Mathlib cache (no omnibus library). Decoder target own cache,
pip --no-cache-dir; Mathlib/cache helper code is a setup dependency, not science.
No global toolchain setting. Bound setup at12GB owned cache and15minutes; if blocked,
label uncompiled honestly, no labels from sketches. Remove OWN compiler/archive/
decoder/Git navigation/Mathlib caches only AFTER actual full extracted rerun.

After original science, complete inline standalone note with all owned critical
code and essential outputs; extract into clean directory; freshly fetch engine+
registry+toolchain+lake-manifest (4public dependencies) and repeat full runner with
same verified compiler/Mathlib setup. Compare science,4worker non-timing records,
formal records and detailed deterministic outputs, not timing logs. Only afterward
append3scoped LEAN_COMPILED rows+1finite source-contract row, expected122rows/
100formal labels if observed. Preserve all prior118/97 and completed010 state/
ledger/report/archive/science. Unpack/index citations, minimal metadata/privacy/
packet closure before delivery; owner upload only, no independent approval inferred.
