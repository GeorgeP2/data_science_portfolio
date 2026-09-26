# P7 tasks

Atomic tasks for [Real-Time Card Fraud Scoring](../brief.md). One file per task, each with
**Ask / Why / How / Plan / Acceptance criteria**.

| # | Task | Phase | Est. | Depends on |
|---|------|-------|------|------------|
| [T01](T01-scaffold-project.md) | Scaffold the project | 0 Setup | 1 h | none |
| [T02](T02-download-tabformer.md) | Download TabFormer | 0 Setup | 1 h | T01 |
| [T03](T03-download-baf.md) | Download BAF | 0 Setup | 1 h | T01 |
| [T04](T04-load-and-order-tabformer.md) | Load, clean and order TabFormer | 1 Offline model | 2 h | T02 |
| [T05](T05-time-aware-split.md) | Time-aware split | 1 Offline model | 1 h | T04 |
| [T06](T06-static-baseline.md) | Static-feature baseline | 1 Offline model | 2 h | T05, T09 |
| [T07](T07-stateful-features.md) | Stateful per-card features | 1 Offline model | 3 h | T04 |
| [T08](T08-stateful-model-and-ablation.md) | Stateful model and ablation | 1 Offline model | 1.5 h | T06, T07 |
| [T09](T09-evaluation-metrics.md) | Metrics and cost model | 2 Evaluation | 1.5 h | T01 |
| [T10](T10-cost-curves-and-threshold.md) | Cost curves, threshold, sensitivity | 2 Evaluation | 2 h | T08, T09 |
| [T11](T11-redpanda-and-replay-producer.md) | Redpanda and replay producer | 3 Streaming | 2 h | T04 |
| [T12](T12-streaming-scorer-in-memory.md) | Streaming scorer (in-memory state) | 3 Streaming | 3 h | T07, T10, T11 |
| [T13](T13-redis-state-backend.md) | Redis state backend | 3 Streaming | 2 h | T12 |
| [T14](T14-feature-parity-test.md) | Feature-parity test in CI | 3 Streaming | 1.5 h | T07, T12 |
| [T15](T15-monitor-and-make-up.md) | Monitor and `make up` | 3 Streaming | 2 h | T12 |
| [T16](T16-load-test.md) | Load test vs SLO | 3 Streaming | 1.5 h | T13, T15 |
| [T17](T17-baf-model.md) | BAF companion model | 4 Fairness | 1.5 h | T03, T09 |
| [T18](T18-fairness-group-metrics.md) | Group metrics and thresholds | 4 Fairness | 2 h | T17 |
| [T19](T19-design-decisions-writeup.md) | Design decisions write-up | 5 Write-up | 2 h | T10, T13, T16 |
| [T20](T20-readme.md) | Project README | 5 Write-up | 1.5 h | T08, T10, T15, T16, T18, T19 |
| [T21](T21-stretch-delayed-labels.md) | *Stretch:* delayed-label simulation | Stretch | 3 h | T12, T15 |
| [T22](T22-stretch-graph-feature.md) | *Stretch:* shared-merchant graph feature | Stretch | 3 h | T08, T14 |

**Total:** ~35 h must-have against a ~30 h time box. If it runs over, cut in this order: T13's
restart/recovery test (keep the Redis latency comparison), then the group-aware threshold variant in
T18 (keep the single-threshold group table), then the per-group ablation in T08 (keep static vs full).

## Mapping to "Done when"

| Brief criterion | Tasks |
|-----------------|-------|
| `make up && make replay` shows live scoring with a latency panel | T11, T12, T15 |
| Feature-parity test in CI | T07, T14 |
| Cost curve + chosen threshold in the README | T09, T10, T20 |
| Fairness companion section with the group metrics table | T17, T18, T20 |
