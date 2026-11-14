# The GPT Lean Proof for a Millennium Prize: A Detailed Write-Up

**Subject:** OpenAI's claimed resolution of the Navier–Stokes existence and smoothness problem, with a full Lean 4 formalization
**Announced:** September 8, 2026 · **This report updated:** September 14, 2026
**One-line summary:** An unreleased OpenAI model (newer than GPT‑6 Astra), running as a swarm of ~10,000 agents, produced a ~165‑page analytical proof that the 3‑D Navier–Stokes equations — the fluid equations used in aircraft design, weather forecasting, and blood‑flow modeling — can develop a finite‑time singularity when driven by a smooth force; GPT‑6 Astra then translated the argument into a machine‑checked Lean proof in 17 hours. As of this update, **independent third parties have reproduced every layer of the *formal* verification (build, Comparator, second kernel), the independent DeepMind challenge repository has merged the proof as a valid solution, the problem's own author Charles Fefferman says the result appears to match his formulation, but no PDE expert group has yet digested the mathematics and the Clay Institute still lists the problem as open** [1](https://openai.com/index/navier-stokes-solution/) [4](https://github.com/openai/NavierStokesAndEuler) [17](https://github.com/CrystalArchitect/navier-stokes-lean-check).

---

## 1. What exactly was announced

On **Tuesday, September 8, 2026**, OpenAI published three artifacts [1](https://openai.com/index/navier-stokes-solution/) [4](https://github.com/openai/NavierStokesAndEuler):

1. *Finite time blowup for Navier–Stokes* — a ~165‑page analytical paper (ten chapters + three appendices) [2-paper](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf);
2. *Finite time blowup for the Euler equation* — a ~57‑page companion paper on the inviscid (zero‑viscosity) equations, which the agents solved first as a "warm‑up" [3-paper](https://cdn.openai.com/pdf/315b36cd-ec98-4023-8342-93345194ece1/euler.pdf);
3. **`github.com/openai/NavierStokesAndEuler`** — the Lean 4 formalization of both results, Apache‑2.0 licensed [4](https://github.com/openai/NavierStokesAndEuler).

The claim is a **disproof**: smooth solutions of the 3‑D incompressible Navier–Stokes equations are *not* guaranteed to exist forever — finite‑time blowup can occur even while total kinetic energy stays bounded. OpenAI says this settles alternatives **(C)** and **(D)** of Charles Fefferman's official Clay Institute problem statement, and it **will not claim the $1 million prize** [1](https://openai.com/index/navier-stokes-solution/).

The discovery model is an unreleased internal system that OpenAI describes as "significantly more capable than GPT‑6 Astra," in training since August 28, 2026. **GPT‑6 Astra** — released September 3, 2026, and itself fresh off Lean‑verifying ten long‑standing problems on August 3 (repo `openai/ten-proofs`, final‑run cost ~$2,000, reviewed publicly by Tim Gowers) — was used specifically for the *formalization* stage [6](https://www.neowin.net/news/openai-says-its-unreleased-ai-model-has-solved-a-1-million-millennium-prize-problem/) [20](https://miraflow.ai/blog/navier-stokes-ai-proof-controversy-openai-astra-explained-2026).

OpenAI also told the *New York Times* it had made "substantial progress" on a second, unnamed Millennium Prize problem [21](https://www.explainx.ai/blog/fields-medalists-ai-math-declaration-openai-2026).

---

## 2. The mathematical background

### 2.1 The Millennium problem

The Navier–Stokes equations are Newton's second law for a fluid treated as a continuum:

$$\partial_t u + (u\cdot\nabla)u - \nu\Delta u + \nabla p = f,\qquad \nabla\cdot u = 0,$$

with velocity $u$, pressure $p$, viscosity $\nu>0$, and external force $f$. Jean Leray proved in **1934** that global *weak* (generalized) solutions exist; whether solutions starting from smooth data must stay smooth forever — or can develop a **singularity** (speeds growing without bound in finite time) — has been open ever since, roughly 90 years. The Clay Institute made it one of seven Millennium Prize Problems in 2000; only the Poincaré Conjecture (Perelman) has ever been awarded [1](https://openai.com/index/navier-stokes-solution/) [2](https://qz.com/openai-ai-navier-stokes-millennium-prize-math-090826).

Fefferman's official formulation ("to give reasonable leeway to solvers while retaining the heart of the problem") offers four alternatives [xeno](https://xenospectrum.com/en/openai-navier-stokes-singularity-clay-dispute/) [24](https://www.ctco.blog/posts/ten-thousand-agents-and-a-millennium-problem/):

| Alternative | Domain | Force | Statement |
|---|---|---|---|
| **(A)** | $\mathbb{R}^3$ | $f=0$ | Smooth, finite‑energy solutions exist for all time |
| **(B)** | $\mathbb{R}^3/\mathbb{Z}^3$ (torus) | $f=0$ | The same positive statement, periodically |
| **(C)** | $\mathbb{R}^3$ | smooth, decaying $f$ allowed | Exhibit smooth data/force with **no** global smooth, energy‑bounded solution |
| **(D)** | $\mathbb{R}^3/\mathbb{Z}^3$ | smooth periodic $f$ allowed | The same breakdown on the torus |

OpenAI claims **(C)** and **(D)** — alternatives that Fefferman deliberately left open as Clay‑eligible resolutions, but which most working fluid dynamicists regard as meaningfully easier than the celebrated *unforced* global‑regularity question (A)/(B), which remains untouched [20](https://miraflow.ai/blog/navier-stokes-ai-proof-controversy-openai-astra-explained-2026). A note on the fine print: (C)/(D) still impose strict bounds on every derivative of $f$ and its space‑time decay; OpenAI's force is **compactly supported in space and time**, so it satisfies those bounds automatically *if* the formal definitions match Fefferman's text — the central statement‑fidelity question for reviewers [xeno](https://xenospectrum.com/en/openai-navier-stokes-singularity-clay-dispute/).

### 2.2 The main theorem, in ordinary mathematics

Paper's Theorem 1.1 [2-paper](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf):

> For **every** viscosity $\nu>0$, there exist a force $f\in C_c^\infty(\mathbb{R}^3\times(0,\infty);\mathbb{R}^3)$, a compact set $K\subset\mathbb{R}^3$, and smooth $u,p$ on $\mathbb{R}^3\times[0,1)$ solving the Navier–Stokes equations with **zero initial velocity** $u(\cdot,0)=0$, with $u,p$ supported in $K$ for all $t<1$, such that
> $$\sup_{0\le t<1}\|u(t)\|_{L^2}<\infty,\qquad \limsup_{t\uparrow 1}\|u(t)\|_{L^\infty}=\infty.$$
> Hence no global smooth solution with uniformly bounded kinetic energy exists with that force and datum — alternative **(C)**. Compact support also yields the torus construction — alternative **(D)** (Corollary 10.6).

The crucial subtlety: you cannot just "put in an infinite force by hand." Given *any* flow you can define $f$ as the equation residual, so the entire game is making the individual terms blow up while their **sum stays smooth through the singular time**, with every derivative bounded [1](https://openai.com/index/navier-stokes-solution/).

### 2.3 The construction, in two stages (paper §§2–10)

The paper builds an inward‑spiraling, axially stretching vortex — "like spaghetti" [2-paper](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf), with the §3 outline helpfully summarized in the MathOverflow discussion thread [25](https://mathoverflow.net/questions/515056/proof-outline-and-discussion-openais-claimed-forced-blowup-construction-for-na):

**Stage 1 — the concentrating background.**
- A self‑similar, axisymmetric leading flow. With $\tau=1-t$ the time to blowup and a fixed $0<h<1/100$,
$$\ell_r\asymp \tau^{1/2},\qquad \ell_z\asymp \tau^{1/2-h},$$
so the core becomes an increasingly slender column (volume $\sim\tau^{3/2-h}$) concentrated at the origin. Speeds scale as $|u_\theta|,|u_z|\asymp \tau^{-1/2-h}$ (the radial speed is only $O(\tau^{-1/2})$), yet the core's kinetic energy $\sim \tau^{1/2-3h}\to 0$: enormous speeds in a vanishing volume.
- Physics of the spin‑up: radial inflow carries angular momentum inward ($ru_\theta$ conserved absent torque); axial outflow through incompressibility drains the incoming fluid; the azimuthal Reynolds number $\mathrm{Re}_\theta\asymp\tau^{-h}\to\infty$ while the radial Reynolds number stays $O(1)$, so viscosity never stops competing radially.
- The background $(u^{(0)},p^{(0)})$ is *not* a solution: its momentum residual $R(u^{(0)},p^{(0)})$ diverges as $t\uparrow1$. It is rewritten as the divergence of a **stress tensor $T$**, supported in a shrinking annulus, with radial moment matching conditions fixing its exterior.

**Stage 2 — cancel the residual with oscillatory waves, then iterate.**
- Two families of divergence‑free oscillatory ring‑shaped pulses (wavelength $\ell_{\text{wave}}\sim q^{1/2+h/2}$, amplitude $A\sim q^{-1/2-h/2}$) grow under the background shear and then decay under viscosity. Their squared amplitudes are chosen so that the time‑averaged quadratic momentum flux of the two families (their covariance vectors $v_1,v_2$) realizes the stress exactly: $T=c_1v_1+c_2v_2$ with $c_1,c_2>0$ — the paper's "**admissible stress cone**" condition. Writing the perturbations as curls $w=\nabla\times A$ makes them exactly divergence‑free.
- A fixed **four‑step correction cycle** then repeats: solve driven wave‑amplitude equations; adjust signed amplitude increments for the averaged stress; invert a fast auxiliary‑time derivative to correct zero‑mean parts; solve five radial‑moment equations preserving two conserved integrals. Each cycle improves a residual decay exponent by a fixed amount, $\sigma_{j+1}=\sigma_j+\tfrac{1}{10}$, driving $\sigma_j\to\infty$. Summing with shrinking cutoffs, *every* Cartesian space‑time derivative of the residual vanishes to every order at the singular time — this "flatness" statement (**Theorem 3.1**) is the technical heart.
- Localize with cutoffs, take a final curl, and set $f:=R(u,p)$. Flatness makes $f$ extend smoothly through $t=1$; an energy estimate over the shrinking core (using $h<1/6$) gives uniformly bounded energy; a **uniqueness lemma (10.5)** rules out any competing bounded‑energy global solution with the same force and zero datum. Rescaling in $\nu$ and periodizing gives the torus corollary (10.6) [25](https://mathoverflow.net/questions/515056/proof-outline-and-discussion-openais-claimed-forced-blowup-construction-for-na).

The intellectual lineage is explicitly cited: Tao's 2016 blowup for an *averaged* Navier–Stokes model; Buckmaster–Vicol's convex‑integration weak nonuniqueness; Albritton–Brué–Colombo's nonuniqueness with a force singular at the initial time; Daneri–Székelyhidi's oscillatory stress realization for Euler; and above all **Diego Córdoba and Luis Martínez‑Zoroa's** successive‑amplification vortex‑layer constructions (forced Euler; hypodissipative Navier–Stokes; incompressible porous media) [2-paper](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf). (El País reported that OpenAI's *first* version of its announcement omitted the Córdoba–Martínez‑Zoroa references and they were added several hours later in an update [22](https://elpais.com/ciencia/2026-09-09/el-anuncio-de-openai-de-que-ha-resuelto-uno-de-los-mayores-enigmas-matematicos-de-la-historia-desata-acusaciones-de-plagio.html).)

### 2.4 The Euler companion result

As a stepping stone, ~100 agents over ~50 hours proved **unforced** 3‑D Euler blowup: smooth, compactly supported, divergence‑free initial data (nonzero, divergence‑free) with a finite maximal lifespan $0<T^*\le1$ in the all‑order Sobolev class, energy bounded on every earlier interval, $\limsup_{t\uparrow T^*}\|u(t)\|_{C^1}=\infty$, and a divergent Beale–Kato–Majda vorticity integral $\int_0^{T^*}\|\omega(t)\|_\infty\,dt=\infty$ [4](https://github.com/openai/NavierStokesAndEuler). That BKM divergence is significant: it certifies blowup through the classical criterion rather than a mere loss of regularity. The concurrent human result (Alpöge–Buckmaster) covered the **forced** Euler equation — a different theorem; OpenAI claims the stronger *unforced* version [1](https://openai.com/index/navier-stokes-solution/). (A third camp — Ganeshram, Duruisseaux and Anandkumar — circulated a *candidate* unforced Euler singularity with a 112‑page conditional stability companion; their unconditional blowup proof remained unfinished and drew requests for stronger residual‑derivative bounds [8](https://kingy.ai/blog/navier-stokes-ai-proof-claims-dispute/).)

---

## 3. The Lean proof — the heart of the release

This is the part that makes the announcement more than a press claim. A Lean formalization turns a natural‑language proof into code where every logical step is checked by a small, trusted kernel: there is no hand‑waving gap the checker will accept [4](https://github.com/openai/NavierStokesAndEuler).

### 3.1 What the repository contains

I cloned and inspected `openai/NavierStokesAndEuler` directly (last official commit `f9e8bc5`, September 10, 2026; no CI workflow and no open/closed issues on the official repo; ~1.9k stars, ~195 forks by Sept 14) [4](https://github.com/openai/NavierStokesAndEuler):

| Item | Value |
|---|---|
| Toolchain | **Lean 4.34.0‑rc2**, Mathlib pinned to the same tag, built with Lake/elan |
| Extra dependency | `leanprover/comparator` (independent‑statement cross‑checker), same tag |
| Total Lean code | **2,659 `.lean` files, ~641,000 lines** |
| Navier–Stokes library | 816 files, ~429,000 lines (incl. an `R3/` subtree) |
| Euler library | 1,839 files, ~212,000 lines |
| Largest single files | `Euler/EulerProof.lean` (20,755 lines), `NavierStokes/CorrectionStep.lean` (9,849), `CorrectionInitialization*.lean` (~5,500 each) |
| Build size | ~11,100–11,251 Lake jobs; Mathlib itself comes from the prebuilt olean cache; the project's own libraries compile locally (~15 min cold on 20 cores per an independent fork's measurements) |
| Compiler strictness | libraries built with `autoImplicit = false`, `warningAsError = true` |
| Authors (per metadata) | "OpenAI"; `automation.methods: agent`, models **GPT‑6 Astra**, framework **Codex** |
| License | Apache‑2.0 |

The file names read like a machine‑generated PDE textbook mirroring the paper's chapters: `ActivationCone`, `ActualBaseResidual`, `OscillatoryRealization`, `CorrectionStep`, `HeatExterior`, `ResidualImprovement`, `CompactForcing`, … [4](https://github.com/openai/NavierStokesAndEuler).

### 3.2 The actual machine‑checked theorems

The two Navier–Stokes certificates, from `NavierStokes/ComparatorSolution.lean` [4](https://github.com/openai/NavierStokesAndEuler):

```lean
/-- (C) Breakdown of Navier–Stokes solutions on ℝ³. -/
theorem navier_stokes_breakdown_R3 (nu : ℝ) (hnu : nu > 0) :
    ∃ (u₀ : ℝ³ → ℝ³) (f : ℝ³ → ℝ → ℝ³),
    InitialVelocityConditionDecay u₀ ∧ ForceConditionDecay f ∧
    ¬ (∃ v p, NavierStokesExistenceAndSmoothnessRn nu u₀ f v p)

/-- (D) Breakdown of Navier–Stokes solutions on ℝ³/ℤ³. -/
theorem navier_stokes_breakdown_periodic (nu : ℝ) (hnu : nu > 0) :
    ∃ (u₀ : ℝ³ → ℝ³) (f : ℝ³ → ℝ → ℝ³),
    InitialVelocityConditionPeriodic u₀ ∧ ForceConditionPeriodic f ∧
    ¬ (∃ v p, NavierStokesExistenceAndSmoothnessPeriodic nu u₀ f v p)
```

In plain language: *for every positive viscosity, there are admissible initial data and an admissible force for which no velocity–pressure pair satisfying the full existence‑and‑smoothness contract (PDE, divergence‑free, regularity, energy bounds) exists* — on $\mathbb{R}^3$ and on the torus. The Euler certificates (`Euler/Solution.lean`) state the unforced blowup and the explicit BKM‑certified singularity theorem [4](https://github.com/openai/NavierStokesAndEuler).

### 3.3 No `sorry`, only the three standard axioms

The two classic ways to fake a formal proof are (a) leaving holes with `sorry`/`admit`, and (b) assuming extra axioms [4](https://github.com/openai/NavierStokesAndEuler):

- A full search finds **zero `sorry`/`admit` in the proof libraries**. The *only* occurrences are **four intentional placeholders** (two in each challenge file) inside `ComparatorChallenges/` — the *question* templates, which by design state the problem without proving it; that library is not built with `warningAsError`, so the four warnings are expected. `formalization.yaml` declares `sorry_count: 0` for every main result, and an independent build confirmed those four warnings were "the entire non‑progress output" besides the axiom info lines [17](https://github.com/CrystalArchitect/navier-stokes-lean-check).
- Every main theorem ends with `#print axioms`, and the Comparator config whitelists exactly:
```json
"permitted_axioms": ["propext", "Quot.sound", "Classical.choice"]
```
These are precisely the three standard axioms underlying all of Mathlib (propositional extensionality, quotient soundness, functional choice) — no custom physical axioms [4](https://github.com/openai/NavierStokesAndEuler).

### 3.4 The clever part: Comparator, an independent statement, and a second kernel

A Lean kernel certifies that a proof derives *the statement that was typed*. It cannot tell you whether the typed statement actually *is* the Millennium Problem. "Formally proving the wrong theorem" is a real failure mode: in January 2026, David Budden's much‑discussed Navier–Stokes Lean effort collapsed partly because the Lean‑Dojo formalization it targeted admitted a trivial proof [12](https://manifold.markets/Simon74fe/outcome-of-david-buddens-navierstok).

OpenAI's answer is the **Comparator** architecture, a framework from the official Lean project (`leanprover/comparator`) [16](https://github.com/leanprover/comparator):

1. **An independent problem statement.** `ComparatorChallenges/NavierStokes.lean` is a standalone formalization of Fefferman's problem adapted (with attribution, Apache‑licensed) from **Google DeepMind's *Formal Conjectures*** project — an encoding written and published *before any proof existed*, pinned at upstream commit `8bf45ed`. It imports only Mathlib, inlines all utilities, and contains the (C)/(D) claims with `sorry` placeholders. **Neither the proof libraries nor the submission imports this file** — the agents developed the proof against their own definitions and could not quietly "fit" the target [4](https://github.com/openai/NavierStokesAndEuler) [17](https://github.com/CrystalArchitect/navier-stokes-lean-check).
2. **A bridge, not a rewrite.** Thin adapters (`ComparatorBridge`, `ComparatorR3Bridge`, …) connect the internal construction to the reference theorem names; a wrong definition cannot be bridged.
3. **A second, independent kernel.** The config sets `"enable_nanoda": true`. Comparator exports the proof terms with `lean4export` and replays them through **nanoda**, an independent Lean kernel written in Rust (v0.4.13), with the whole replay sandboxed via **landrun** (a Landlock LSM wrapper, Linux‑only) [4](https://github.com/openai/NavierStokesAndEuler) [18](https://whataifound.org/). As one Hacker News commentator put it, a false verdict would require "two bugs in two independently written Lean kernels," and the release was additionally cross‑checked via the community's Lean Kernel Arena [26](https://news.ycombinator.com/item?id=49668706).
4. **A fresh‑clone trust condition.** Comparator's guarantee depends on the solution never having been compiled outside the sandbox; the documented procedure uses a pristine clone (the proof code and the Comparator check are meant to run in separate clones) [19](https://github.com/Code4me2/NavierStokesAndEuler).

Reproduction commands:
```sh
lake exe cache get
lake build                                                      # Lean + Mathlib check
lake exe comparator ComparatorChallenges/NavierStokes.json      # independent statement + nanoda
lake exe comparator ComparatorChallenges/Euler.json
```

### 3.5 Formalization ↔ paper alignment

`formalization.yaml` ships a machine‑readable traceability table [4](https://github.com/openai/NavierStokesAndEuler):

| Paper statement | Lean declaration | Status |
|---|---|---|
| Theorem 1.1 (Navier–Stokes, $\mathbb{R}^3$) | `NavierStokes.Comparator.navier_stokes_breakdown_R3` | proved, 0 sorry, 3 standard axioms |
| Corollary 10.6 (torus) | `NavierStokes.Comparator.navier_stokes_breakdown_periodic` | proved, same |
| Theorem 1.1 (Euler) | `Euler.euler_breakdown_R3` | proved, same |
| Theorem 1.1 (Euler, explicit form) | `Euler.exists_compact_smooth_euler_singularity` | proved, same |

The metadata candidly labels **`review.status: self-assessed`** — no outside party is claimed by OpenAI as having reproduced the checks at release [4](https://github.com/openai/NavierStokesAndEuler).

### 3.6 What the Lean certificate does and does not establish

- **It guarantees:** deductive correctness from the encoded definitions and the three standard axioms — here reinforced by an independent target statement, adapter bridges, and a second kernel.
- **It does not guarantee:** that the encoded decay/regularity definitions match Fefferman's intent clause by clause (experts must diff `ComparatorDefinitions` against the Clay PDF); that the 165 prose pages and 641k code lines agree everywhere; or social/Clay acceptance. Terence Tao's working label is a **"formally verified proposed solution awaiting expert digestion and community validation"** [8](https://terrytao.wordpress.com/2026/09/07/finite-time-blowup-with-smooth-forcing-term-for-the-incompressible-porous-medium-boussinesq-and-incompressible-euler-equations/).
- **Prize mechanics:** Clay does not accept direct submissions; it requires publication in a qualifying refereed outlet, two years' elapsed time, and broad community acceptance. Its president **Martin Bridson** called announcement day "an exciting day … seeing important advances," while the institute's website continues to list the problem as unsolved [22](https://elpais.com/ciencia/2026-09-09/el-anuncio-de-openai-de-que-ha-resuelto-uno-de-los-mayores-enigmas-matematicos-de-la-historia-desata-acusaciones-de-plagio.html) [23](https://mlq.ai/news/openais-navierstokes-claim-is-public-machine-checked-and-still-awaiting-independent-judgment/).

---

## 4. Independent verification of the Lean artifact (Sept 9–14) — what is now settled

This is the part that moved fastest after release. Three independent efforts reproduced the *formal* chain within days. They are individual/community efforts rather than institutional certifications, but their checks are mechanical, reproducible, and published with logs [17](https://github.com/CrystalArchitect/navier-stokes-lean-check) [27](https://github.com/francescoantoniodeluca/navier-stokes-formal-audit/releases/tag/v1.0):

1. **Kernel validity and statement fidelity — `CrystalArchitect/navier-stokes-lean-check` (Sept 11).** A clean build: "Build completed successfully (**11,251 jobs**)," exit 0, no `sorryAx`; `#print axioms` returned only `[propext, Classical.choice, Quot.sound]` for both target theorems; exactly the four expected `sorry` warnings in the challenge stubs. It also published the **complete byte‑level diff** of OpenAI's `ComparatorDefinitions.lean` against DeepMind's pre‑proof upstream file (`8bf45ed`), concluding the proved statement is "Google DeepMind's pre‑existing encoding of Clay alternative (C), unmodified." This auditor did *not* run nanoda (no Linux/Landlock environment) [17](https://github.com/CrystalArchitect/navier-stokes-lean-check).
2. **Full chain including nanoda — `francescoantoniodeluca/navier-stokes-formal-audit`, release v1.0 (Sept 11–12).** Pinned to OpenAI's Sept 8 commit `8937a8f`, it reports: repository‑wide build **PASS**, Comparator **PASS**, **nanoda accepted**, Lean default kernel **accepted**, and an *additional* independent layer — a hand‑written 228‑line `ClaySpec.lean` derived directly from Fefferman's PDF (importing only Mathlib), plus `Gap.lean`/`Adapter.lean` formally composing the chain OpenAI construction → Comparator theorem → independently written Clay statement, ending in Lean‑checked terms `openAI_to_ClayOptionC`/`ClayOptionD`. A red‑team audit of adversarial failure modes also passed [27](https://github.com/francescoantoniodeluca/navier-stokes-formal-audit/releases/tag/v1.0).
3. **DeepMind Formal Conjectures accepted the proof as a solution to its challenge.** PR [#5361](https://github.com/google-deepmind/formal-conjectures/pull/5361), linking OpenAI's repository as the formal proof of its Millennium Navier–Stokes statement, was reviewed by maintainers (Paul‑Lez: "I don't expect any problem will be found"; Mathlib maintainer mo271: "we have sufficient consensus") and **merged on September 11** [28](https://github.com/google-deepmind/formal-conjectures/pull/5361). A Lean‑Zulip thread ("Independent verification of OpenAI NavierStokesAndEuler") records the build reproductions; further classroom‑scale reproductions (e.g., a Sept 14 French educational‑repo notebook reporting `kernels={nanoda:accepts, lean_kernel:accepts}` for both Euler and Navier–Stokes) have since appeared [29](https://github.com/jsboige/CoursIA/pull/16084).

**Calibration.** What these reproduce is the formal side of the ledger: the code compiles, the theorem matches the independent DeepMind encoding (and an independent re‑encoding of Fefferman), no holes or exotic axioms exist, and a second kernel concurs. What they do *not* do is referee the 165‑page analytical argument: if the paper's estimates were wrong but the Lean development proved the encoded statement anyway, the mismatch would live in the paper‑to‑code correspondence, which the formal bridge does not fully police. No PDE specialist team has yet published a line‑by‑line mathematical reading; Fefferman estimates "months" [22](https://elpais.com/ciencia/2026-09-09/el-anuncio-de-openai-de-que-ha-resuelto-uno-de-los-mayores-enigmas-matematicos-de-la-historia-desata-acusaciones-de-plagio.html) [25](https://mathoverflow.net/questions/515056/proof-outline-and-discussion-openais-claimed-forced-blowup-construction-for-na).

### The problem author's own preliminary verdict

**Charles Fefferman**, who wrote the Clay statement, told **El País** (Sept 9–10) that the result *appears to match the problem as he formulated it*, but that he would need "a rewrite in conventional mathematical prose and a close reading by several experts" before being convinced — a process he estimated in months [22](https://elpais.com/ciencia/2026-09-09/el-anuncio-de-openai-de-que-ha-resuelto-uno-de-los-mayores-enigmas-matematicos-de-la-historia-desata-acusaciones-de-plagio.html) [23](https://mlq.ai/news/openais-navierstokes-claim-is-public-machine-checked-and-still-awaiting-independent-judgment/. Fields medalist Timothy Gowers, before reading it, called the moment "undeniably a big moment" [2](https://qz.com/openai-ai-navier-stokes-millennium-prize-math-090826); Tao praised the rival Alpöge–Buckmaster forced‑Euler/Boussinesq/IPM papers as "a remarkable achievement" / "a breakthrough across three simplified models," said he saw no decisive *in‑principle* obstacle to extending the techniques to Navier–Stokes (nor to eventually removing forcing), but stressed enormous technical difficulties remain — and Stan Palasek has identified a specific obstacle to removing the forcing from the present approach [8](https://terrytao.wordpress.com/2026/09/07/finite-time-blowup-with-smooth-forcing-term-for-the-incompressible-porous-medium-boussinesq-and-incompressible-euler-equations/) [24](https://www.ctco.blog/posts/ten-thousand-agents-and-a-millennium-problem/).

---

## 5. How GPT produced it: the agent swarm

OpenAI's account [1](https://openai.com/index/navier-stokes-solution/) [6](https://www.neowin.net/news/openai-says-its-unreleased-ai-model-has-solved-a-1-million-millennium-prize-problem/):

- **Aug 28:** training begins on the new internal model. **Sept 1, Tuesday:** after rumors of breakthroughs (later tied to Alpöge and Buckmaster), agents are launched on *all* open Millennium Problems and related questions; separate groups get variants (A)/(B) (prove regularity) and (C)/(D) (find breakdown).
- **Tools/organization:** cached‑internet read, code execution, intra‑group messaging, varying group sizes, frontier‑evaluation isolation and monitoring.
- **Euler first:** ~100 agents, ~50 hours → unforced Euler blowup. The effort then concentrates on Navier–Stokes, with agents prompted on the Euler resolution.
- **Cross‑pollination:** Codex consolidates the best intermediate insights across competing groups and feeds them back; agents are upgraded to newer model checkpoints mid‑training.
- **Sept 5, Saturday (~88h in):** the winning group, on the order of **10,000 concurrent agents**, reaches the Navier–Stokes resolution. **Sept 6:** GPT‑6 Astra completes Lean formalization/verification in a further **17 hours**.
- **Scale and cost:** all problems combined — 4.9M agent messages, ~300B output tokens; Navier–Stokes alone — 2.7M messages, ~130B output tokens (a sustained ~410,000 output tokens/second for nearly four days). Mark Chen put compute cost "in the millions"; at Astra's retail $50/M output tokens the NS tokens alone would list at ~$6.5M, with third‑party total‑run estimates spanning roughly **$2M–$40M** [2](https://qz.com/openai-ai-navier-stokes-millennium-prize-math-090826) [24](https://www.ctco.blog/posts/ten-thousand-agents-and-a-millennium-problem/).
- **Human role:** Sébastien Bubeck said the human team lacked research‑level fluid‑dynamics expertise and contributed orchestration rather than mathematical content; Dan Roberts described the humans as "bees cross‑pollinating" between groups [11](https://andrew.ooo/answers/openai-navier-stokes-proof-10000-agents-september-2026-explained/) [time](https://time.news/openai-ai-model-solves-navier-stokes-millennium-prize-math-090826/). (Contrast the August ten‑proofs release, where a group including Noga Alon, Gowers, Will Sawin, Arul Shankar and Jacob Tsimerman subsequently published a human‑verified rewrite of one model‑generated counterexample [30](https://www.popularai.org/p/openai-navier-stokes-solution-provenance).)

---

## 6. The disputes: priority, provenance, and a Fields‑Medal declaration

### 6.1 The Alpöge–Buckmaster priority fight

- **Their program.** Levent Alpöge (Harvard, then Anthropic) and Tristan Buckmaster (NYU), building explicitly on Córdoba–Martínez‑Zoroa's cascading vortex‑layer method, reached smooth‑forcing blowup for the 2‑D Boussinesq and 3‑D forced Euler equations around **Aug 15**, had the Euler result Lean‑verified by **Aug 22**, and posted three manuscripts (IPM, Boussinesq, forced Euler — with Lean files; their README says Claude wrote the Lean under Alpöge's direction, Codex/Astra assisting) on **Sept 7**; a hypodissipative Navier–Stokes Lean check was still running [31](https://gadgetsnow.indiatimes.com/tech-news/navier-stokes-holds-as-openai-and-anthropic-staff-clash/articleshow/133935320.cgi) [8](https://kingy.ai/blog/navier-stokes-ai-proof-claims-dispute/).
- **Timeline of contact.** OpenAI's sprint began Sept 1 after the rumor; Buckmaster emailed OpenAI on **Sept 3** after hearing word of his work had reached the company; Alpöge later described a **Sept 2** contact. OpenAI says it completed its proof and Lean verification on **Sept 6**, then contacted the pair to offer a joint announcement, only then learning their result was forced Euler rather than Navier–Stokes [1](https://openai.com/index/navier-stokes-solution/) [20](https://miraflow.ai/blog/navier-stokes-ai-proof-controversy-openai-astra-explained-2026) [32](https://www.datacamp.com/blog/openai-navier-stokes-math-problem).
- **Allegations.** Buckmaster's [public statement](https://cims.nyu.edu/~tristanb/statement.pdf) says he was pressed on publication/authorship in Sept 6 calls, including a suggestion to exclude Alpöge because of his Anthropic employment, and that he got no direct answer when asking whether his two months of private Codex sessions had entered training. Bubeck apologized for one remark ("why would you ruin your career") [7](https://explainx.ai/blog/openai-navier-stokes-solution-agent-swarm-2026).
- **OpenAI's position.** Neither researchers nor agents saw the pair's work before publication; it recognizes their priority on forced Euler; a **Sept 10 update** reported an internal investigation concluding Buckmaster's Codex prompts could not have influenced the model (large‑scale RL atop a pre‑trained base, with the base predating the relevant sessions), while conceding it "cannot rule out" indirect effects of de‑identified usage data; the Euler theorems differ (unforced vs forced) and "the proofs differ significantly" [1](https://openai.com/index/navier-stokes-solution/). Notably, Buckmaster's own statement does not dispute that OpenAI produced a valid construction — his objections are process, disclosure and credit [20](https://miraflow.ai/blog/navier-stokes-ai-proof-controversy-openai-astra-explained-2026); and both sides openly credit the same published lineage, making independent convergence plausible [30](https://www.popularai.org/p/openai-navier-stokes-solution-provenance).

### 6.2 "A Severe Misalignment of AI in Mathematics" (Sept 11)

The episode triggered the strongest community‑wide institutional response in years: a declaration at **mathandai.org signed by 25 Fields Medalists — including Terence Tao** — arguing that "the push by AI companies to solve mathematical problems as a benchmark is detrimental to the science of mathematics … the goals of the AI companies and the goals of the mathematical community are severely misaligned." Its objection is not correctness (it does not dispute the Lean verification) but the *form* of mathematical progress: results announced as marketing before human‑legible writeups, before new methods are isolated, before prior work is attributed, and before the community can convert a true/false verdict into shared understanding; plus the chilling effect on open sharing if labs can deploy 10,000 agents the moment a human direction leaks. Tao had previewed the concern on Mathstodon on **Sept 5**, warning against converting "a historically productive and motivating problem such as Navier–Stokes regularity into a mere viral social media post advertising some benchmark progress" [33](https://www.explainx.ai/blog/fields-medalists-ai-math-declaration-openai-2026) [34](https://ethz.ch/en/news-and-events/eth-news/news/2026/09/no-ai-will-replace-mathematicians-but-i-am-concerned-about-education.html) [32](https://www.datacamp.com/blog/openai-navier-stokes-math-problem). Signatory Alessio Figalli (ETH) added a specific readability critique: "Definitions suddenly appear without it being obvious why they matter … or what the genuinely new idea is" — precisely the gap a Lean certificate cannot fill [34](https://ethz.ch/en/news-and-events/eth-news/news/2026/09/no-ai-will-replace-mathematicians-but-i-am-concerned-about-education.html).

---

## 7. Scorecard: where things stand on September 14, 2026

| Question | Answer |
|---|---|
| Is a proof public and inspectable? | **Yes** — ~165‑page paper + ~641k‑line Lean 4/Mathlib project, released Sept 8, last updated Sept 10 [4](https://github.com/openai/NavierStokesAndEuler) |
| Does Lean accept it with no `sorry` and only standard axioms? | **Yes, and now independently reproduced** — clean builds (~11,251 jobs, exit 0), four expected challenge‑stub warnings only, axiom lists `[propext, Classical.choice, Quot.sound]` [17](https://github.com/CrystalArchitect/navier-stokes-lean-check) |
| Does the formal theorem match the *independent* statement of the Clay problem? | **Independently confirmed at the formal level** — byte‑level diff against the pre‑existing DeepMind Formal Conjectures encoding; a second independently written `ClaySpec.lean` with a formal bridge; Comparator/nanoda pass; DeepMind **merged** the proof as its challenge solution on Sept 11 [27](https://github.com/francescoantoniodeluca/navier-stokes-formal-audit/releases/tag/v1.0) [28](https://github.com/google-deepmind/formal-conjectures/pull/5361) |
| Has a PDE‑expert group validated the *analytical* paper (estimates, paper–code correspondence)? | **Not yet** — Fefferman: appears to match the formulation, but wants a conventional prose rewrite and several expert readers; timeline months [22](https://elpais.com/ciencia/2026-09-09/el-anuncio-de-openai-de-que-ha-resuelto-uno-de-los-mayores-enigmas-matematicos-de-la-historia-desata-acusaciones-de-plagio.html) |
| Has Clay certified anything? | **No** — problem still listed open; rules require qualifying journal publication + two years + general acceptance; OpenAI declines to file [23](https://mlq.ai/news/openais-navierstokes-claim-is-public-machine-checked-and-still-awaiting-independent-judgment/) |
| Does it touch the *unforced* regularity question (A/B)? | **No** — (C)/(D), forced breakdown; Palasek has described a concrete obstacle to deleting the force in this construction [24](https://www.ctco.blog/posts/ten-thousand-agents-and-a-millennium-problem/) |
| Is the credit/provenance dispute settled? | **No** — OpenAI's Sept 10 investigation denial stands against Buckmaster's allegations; indirect de‑identified data effects conceded as un‑rule‑out‑able [1](https://openai.com/index/navier-stokes-solution/) [7](https://explainx.ai/blog/openai-navier-stokes-solution-agent-swarm-2026) |
| Broader community posture? | 25 Fields Medalists (incl. Tao) signed the Sept 11 "Severe Misalignment" declaration on benchmark‑style math announcements [33](https://www.explainx.ai/blog/fields-medalists-ai-math-declaration-openai-2026) |

### What to watch next

1. The first PDE‑specialist public readings (Tao, Buckmaster, Vicol, the Córdoba/Martínez‑Zoroa school) and an arXiv/journal submission of a human‑digestible rewrite.
2. Any correction to paper or Lean code; independent runs of the Linux‑only Comparator/nanoda sandbox beyond those already posted.
3. Resolution of provenance questions (OpenAI offered prompt transparency; Codex data‑lineage audits).
4. Whether the techniques extend toward unforced (A)/(B) — universally regarded as the prize that actually matters to working fluid dynamicists.
5. OpenAI's reported "substantial progress" on a second Millennium Problem.

---

## 8. Why this Lean proof matters regardless of the verdict

Historically, formal verification trailed famous proofs by years or decades and was human‑led (Flyspeck for the Kepler conjecture; the Liquid Tensor Experiment). Here a weekend's agent run produced, alongside the claimed discovery itself, a **sorry‑free, axiom‑audited, independently‑re‑targetable, second‑kernel‑checked** formalization whose target statement was deliberately authored by a *different* team's pre‑existing project — and the entire verification stack was reproduced by strangers within four days, using a fresh‑clone sandbox, a Rust re‑implementation of the kernel, byte‑level statement diffs, and a second independently hand‑written Clay specification [17](https://github.com/CrystalArchitect/navier-stokes-lean-check) [27](https://github.com/francescoantoniodeluca/navier-stokes-formal-audit/releases/tag/v1.0). The template — *independent reference statement frozen before the proof, adapter bridges, alternative kernel, public build instructions, machine‑readable statement map* — is now the de facto standard the community expects AI mathematics to meet; within days it was already being copied as a template for unrelated formal challenges [35](https://github.com/allenpd728/PleaNP/issues/64). What the template conspicuously does not provide is understanding: the 641k lines do not explain which idea was decisive, teach a student, or settle priority. Both halves of that divide — certificates and comprehension — are what the Navier–Stokes episode has just forced mathematics to adjudicate.

---

## Sources

**Primary**
1. OpenAI, *On the Navier–Stokes Millennium Prize Problem* (Sept 8, updated Sept 10, 2026): https://openai.com/index/navier-stokes-solution/
4. OpenAI Lean repository `NavierStokesAndEuler` (cloned and inspected Sept 11 & 14, 2026): https://github.com/openai/NavierStokesAndEuler
5. Papers: NS — https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf ; Euler — https://cdn.openai.com/pdf/315b36cd-ec98-4023-8342-93345194ece1/euler.pdf
16. Lean Comparator: https://github.com/leanprover/comparator
28. DeepMind Formal Conjectures PR #5361 linking/accepting the proof (merged Sept 11): https://github.com/google-deepmind/formal-conjectures/pull/5361
25. MathOverflow community proof‑outline thread: https://mathoverflow.net/questions/515056/

**Independent formal audits**
17. CrystalArchitect, *navier‑stokes‑lean‑check* (statement diff + 11,251‑job build): https://github.com/CrystalArchitect/navier-stokes-lean-check
27. F. A. Deluca et al., *navier‑stokes‑formal‑audit* v1.0 (Comparator + nanoda + independent ClaySpec bridges): https://github.com/francescoantoniodeluca/navier-stokes-formal-audit/releases/tag/v1.0
19. Community fork with fresh‑clone validation plan and build measurements: https://github.com/Code4me2/NavierStokesAndEuler
29. Independent classroom reproduction (Sept 14): https://github.com/jsboige/CoursIA/pull/16084
18. nanoda/Comparator tooling context (independent Rust Lean kernel): https://whataifound.org/
26. Hacker News discussion (claymath.org posting) on dual‑kernel verification: https://news.ycombinator.com/item?id=49668706

**Expert and institutional reaction**
22. El País, announcement, Fefferman and Bridson quotes, citation omission/correction (Sept 9): https://elpais.com/ciencia/2026-09-09/el-anuncio-de-openai-de-que-ha-resuelto-uno-de-los-mayores-enigmas-matematicos-de-la-historia-desata-acusaciones-de-plagio.html
23. MLQ.ai summary incl. Fefferman's El País assessment and Clay rules: https://mlq.ai/news/openais-navierstokes-claim-is-public-machine-checked-and-still-awaiting-independent-judgment/
8. Terence Tao, blog post/comments (Buckmaster–Alpöge forced blowup; "awaiting expert digestion"): https://terrytao.wordpress.com/2026/09/07/finite-time-blowup-with-smooth-forcing-term-for-the-incompressible-porous-medium-boussinesq-and-incompressible-euler-equations/
33. *A Severe Misalignment of AI in Mathematics* coverage (mathandai.org, 25 Fields medalists, Sept 11): https://www.explainx.ai/blog/fields-medalists-ai-math-declaration-openai-2026
34. ETH Zürich, Alessio Figalli interview (Sept 14): https://ethz.ch/en/news-and-events/eth-news/news/2026/09/no-ai-will-replace-mathematicians-but-i-am-concerned-about-education.html

**Dispute and process**
7. ExplainX, credit/data dispute explainer: https://explainx.ai/blog/openai-navier-stokes-solution-agent-swarm-2026
8b. Kingy.ai, evidence/dispute ledger (Euler candidates, Claude‑written Lean): https://kingy.ai/blog/navier-stokes-ai-proof-claims-dispute
30. Popular AI, provenance and August ten‑proofs follow‑up context: https://www.popularai.org/p/openai-navier-stokes-solution-provenance
31. Gadgets Now, timeline table of the three Alpöge–Buckmaster results: https://gadgetsnow.indiatimes.com/tech-news/navier-stokes-holds-as-openai-and-anthropic-staff-clash/articleshow/133935320.cgi
32. DataCamp explainer (Tao Mathstodon Sept 5; Sept 3 contact; cost): https://www.datacamp.com/blog/openai-navier-stokes-math-problem
2. Quartz: https://qz.com/openai-ai-navier-stokes-millennium-prize-math-090826
6. Neowin: https://www.neowin.net/news/openai-says-its-unreleased-ai-model-has-solved-a-1-million-millennium-prize-problem/
9. XenoSpectrum formulation comparison: https://xenospectrum.com/en/openai-navier-stokes-singularity-clay-dispute/
20. Miraflow verification/controversy guide (ten‑proofs comparison, verification commands): https://miraflow.ai/blog/navier-stokes-ai-proof-controversy-openai-astra-explained-2026
24. Layman's read with Fefferman four‑alternative text, Palasek obstacle, token economics: https://www.ctco.blog/posts/ten-thousand-agents-and-a-millennium-problem/
12. Manifold record of the earlier (Jan 2026) Budden/Lean‑Dojo misformalization: https://manifold.markets/Simon74fe/outcome-of-david-buddens-navierstok
