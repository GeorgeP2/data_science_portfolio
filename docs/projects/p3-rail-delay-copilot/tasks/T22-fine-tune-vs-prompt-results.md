# T22: Fine-tune vs prompt results and recommendation

**Phase:** 5 Fine-tune vs prompt · **Estimate:** 2 h · **Depends on:** T19, T20, T21

## Ask

Produce the comparison table and a written recommendation, including the crossover point where each
option wins.

## Why

"Done when" requires the table and a recommendation. The crossover is the actual answer to headline
question 2.

## How

- Table: option, macro-F1, cost per 1k requests, p50/p95 latency, one-off cost (training, labelling).
- Crossover: total cost vs monthly request volume per option, with an accuracy floor. Plot it.
- Recommendation in plain words, including "the baseline is enough" if that's what the data says.
- Swap the winner into `classify_incident` (T12).

## Plan

- [ ] Assemble the table from T19–T21 outputs
- [ ] Crossover chart
- [ ] Recommendation write-up in `results/`
- [ ] Update `classify_incident`

## Acceptance criteria

- [ ] Table regenerates from saved results with one command
- [ ] Crossover chart is saved in `reports/figures/`
- [ ] Recommendation names a winner per volume range and states the accuracy trade-off
