# Project 9: LLM Optimisation Formulation (Agent + Benchmark)

**One line:** an agent that turns a plain-language business problem into an optimisation model,
solves it, verifies the result and repairs it, plus the contamination-free benchmark of 300+
original problems it's evaluated on.

**Time box:** ~14 weeks part-time: ~8 for the agent (Part A), then ~6 for the benchmark (Part B),
which largely falls out of Part A. Flagship of the ML × OR track; the first one to build.

## Headline questions

> 1. **Agent:** does an agent that formulates, solves and verifies optimisation models get far
>    more problems right than one-shot formulation, and at what cost and latency?
> 2. **Benchmark:** does current LLMs' ability to formulate optimisation models drop sharply on
>    realistic, contamination-free problems compared with existing public benchmarks?

## Why it matters

Turning a plain-language business problem into a correct model is the bottleneck for applied OR. A
verified loop is the difference between a demo and something a planner could trust. Benchmarks get
cited and reused for years, so owning the reference eval in this niche makes the work something
others build on.

## Data

| Source | What | Access | Licence | Use |
|--------|------|--------|---------|-----|
| **Own problem set** | Part A: 150+ LP and MIP word problems with ground-truth optimal values. Part B: grown to 300+ original problems in logistics, manufacturing, energy and finance, never posted publicly before release | In repo; Hugging Face on release, with a private held-out split kept back | To decide before release | Evaluation and the benchmark |

## Scope

**Part A: Agent**
- **Problems:** textbook-to-industrial LP and MIP word problems (production planning, facility location, scheduling, routing variants).
- **Loop:** formulate → generate solver code → solve → verify → repair.
- **Formulation step:** emits a structured model (sets, parameters, variables, constraints, objective) before any code.
- **Code step:** targets one modelling layer (Pyomo or OR-Tools CP-SAT) with a HiGHS backend.
- **Verification:** the agent writes independent checks from the problem text (feasibility of the returned plan, units, obvious bounds) and runs them.
- **Repair:** failed checks and solver errors feed back for up to N rounds.
- **Ablations:** no verification, no structured step, varying N, different base models.
- **Demo:** paste a problem, watch the loop.

**Part B: Benchmark**
- **Difficulty tiers:** textbook, multi-constraint business, and industrial-scale with data tables.
- **Per problem:** a verified reference model, optimal value, and a solution checker. Each is checked by solving the reference model.
- **Grading:** optimal objective match plus feasibility of the returned solution, not text similarity.
- **Evaluation:** a spread of frontier and open models, one-shot and with the Part A agent loop.
- **Contamination guard:** a private held-out split to detect future contamination.

**Out of scope:** fine-tuning a frontier model; non-linear or stochastic programmes in the first
version; a leaderboard service (start with a static results table).

## Milestones

| Weeks | Milestone | Exit criterion |
|-------|-----------|----------------|
| 1–2 | Eval set + harness | 150+ problems with ground-truth optimal values |
| 3–4 | One-shot and loop agents | Both run end to end on the full set |
| 5–6 | Verification + ablations | Accuracy and cost per problem for every variant |
| 7–8 | Failure analysis + agent release | Taxonomy of failure modes, demo, write-up |
| 9–11 | Benchmark problems + reference models | 300 problems, each solved and double-checked |
| 12 | Grading harness | Automated scoring reproduces manual grades on a sample |
| 13–14 | Model evals + paper | Results table, error analysis, arXiv submission |

## Deliverables and headline chart

- **Verified-solution rate** on the test set, one-shot vs loop, with cost and latency alongside.
- The **dataset on Hugging Face** with a grading package, a results table and an arXiv paper.
- A demo and a write-up with a failure taxonomy.

## Design decisions to write up

- Why a structured formulation step comes before any code.
- How independent the verifier really is from the formulator.
- Grading by objective and feasibility rather than text similarity.
- Keeping a private split, and how it detects contamination.

## Risks and gotchas

- **Contamination:** public eval problems may have leaked into model training data. That's why Part B writes a fresh held-out set.
- **Verifier shares the formulator's blind spots.** Test it on deliberately broken models and report its catch rate.
- **Reference model errors.** Have every benchmark problem independently re-modelled or cross-checked before release.
- **Writing 300 problems is slow.** Build templates per problem family and vary the parameters and narratives.

## Done when

- [ ] Accuracy measured as matching the ground-truth optimal objective, with the loop beating one-shot by a clear margin
- [ ] Cost and latency reported for every variant; verifier catch rate on broken models reported
- [ ] Live demo
- [ ] Dataset released with a working grader, results for 6+ models, arXiv paper submitted

**Stack:** Claude API, Pyomo or OR-Tools, HiGHS, Hugging Face Datasets.
