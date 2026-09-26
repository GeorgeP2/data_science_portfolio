# P1 tasks

Atomic tasks for the [Fulfilment Optimisation Service](../brief.md). One file per task, each with
**Ask / Why / How / Plan / Acceptance criteria**.

| # | Task | Phase | Est. | Depends on |
|---|------|-------|------|------------|
| [T01](T01-scaffold-project.md) | Scaffold the project | 0 Setup | 1 h | none |
| [T02](T02-download-kit-benchmark.md) | Download KIT benchmark suite | 0 Setup | 1 h | T01 |
| [T03](T03-download-academic-instances.md) | Download Henn & Wäscher + Foodmart | 0 Setup | 1 h | T01 |
| [T04](T04-domain-model-and-distances.md) | Domain model and distances | 1 Core model | 2 h | T01 |
| [T05](T05-parse-henn-waescher.md) | Parse Henn & Wäscher | 1 Core model | 1 h | T03, T04 |
| [T06](T06-parse-foodmart.md) | Parse Foodmart | 1 Core model | 1.5 h | T03, T04 |
| [T07](T07-routing-s-shape.md) | S-shape routing | 2 Routing | 1 h | T04 |
| [T08](T08-routing-largest-gap.md) | Largest-gap routing | 2 Routing | 1 h | T07 |
| [T09](T09-routing-optimal.md) | Optimal routing (Ratliff & Rosenthal) | 2 Routing | 3 h | T07 |
| [T10](T10-solver-interface-and-fcfs.md) | Solver interface + FCFS baseline | 3 Solvers | 1.5 h | T04, T07 |
| [T11](T11-seed-and-savings.md) | Seed and savings heuristics | 3 Solvers | 2 h | T10 |
| [T12](T12-cp-sat-batching.md) | CP-SAT batching | 3 Solvers | 3 h | T10, T11 |
| [T13](T13-alns-local-search.md) | ALNS local search | 3 Solvers | 4 h | T10, T11 |
| [T14](T14-benchmark-harness.md) | Benchmark harness | 4 Benchmarking | 2 h | T05, T09, T10 |
| [T15](T15-reproduce-published-results.md) | Reproduce published results | 4 Benchmarking | 2 h | T03, T11–T14 |
| [T16](T16-pareto-chart.md) | Pareto chart | 4 Benchmarking | 1 h | T14 |
| [T17](T17-profile-kit-suite.md) | Profile KIT suite | 5 Generator | 2 h | T02 |
| [T18](T18-generator-layout.md) | Generator: layout | 5 Generator | 1 h | T04, T17 |
| [T19](T19-generator-skus-and-orders.md) | Generator: SKU affinity + arrivals | 5 Generator | 2 h | T18 |
| [T20](T20-generator-validity.md) | Generator validity check | 5 Generator | 2 h | T05, T06, T19 |
| [T21](T21-held-out-evaluation.md) | Held-out set + final numbers | 5 Generator | 1 h | T14, T19 |
| [T22](T22-api-contract.md) | `POST /batch` contract | 6 Service | 1.5 h | T10 |
| [T23](T23-latency-budget-fallback.md) | Latency budget + fallback | 6 Service | 2 h | T12, T13, T22 |
| [T24](T24-dockerfile.md) | Dockerfile + local run | 6 Service | 1 h | T22 |
| [T25](T25-cloud-run-deploy.md) | Cloud Run deploy | 6 Service | 1.5 h | T24 |
| [T26](T26-load-test.md) | Load test + p95 | 6 Service | 1.5 h | T23, T25 |
| [T27](T27-design-decisions-writeup.md) | Design decisions write-up | 7 Write-up | 2 h | T12, T20, T23 |
| [T28](T28-readme.md) | Project README | 7 Write-up | 1.5 h | T15, T16, T21, T26, T27 |
| [T29](T29-stretch-simpy-shift.md) | *Stretch:* SimPy shift simulation | Stretch | 4 h | T13, T19 |

**Total:** ~47 h must-have against a ~40 h time box. If it runs over, cut in this order: T06
(Foodmart parser: keep Henn & Wäscher as the sole external benchmark), then T09 (optimal routing),
then reduce T13 to two destroy/repair operators.

## Mapping to "Done when"

| Brief criterion | Tasks |
|-----------------|-------|
| `docker run` + one `curl` reproduces a batching result | T22, T24 |
| Benchmark table reproduces published results within a stated tolerance | T14, T15 |
| Live Cloud Run endpoint with a documented p95 | T23, T25, T26 |
| README leads with the Pareto chart | T16, T28 |
