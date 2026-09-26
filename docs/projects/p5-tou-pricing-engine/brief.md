# Project 5: Time-of-Use Pricing Engine

**One line:** a dynamic-pricing engine for a UK energy supplier. It sets half-hourly tariff prices
to shift household demand away from expensive peaks, under business constraints. It learns demand
response with Thompson-sampling bandits and evaluates policies off-policy before "launch".

**Time box:** weeks 24–26+ (~30 h). Pick this **or** Project 6.

## Headline questions

> 1. Given wholesale cost paths and households' price response, what tariff schedule maximises
>    margin subject to a margin floor, a price cap and rate-of-change limits, and how close does a
>    bandit that has to *learn* the price response get to the known optimum (regret)?
> 2. Can off-policy evaluation predict a new pricing policy's performance from logs of the old one,
>    before it's deployed?

## Why this data is different

Pricing projects usually use a toy simulator with made-up numbers. This one is **anchored on real UK data**:
- **Real price paths:** 8 years of Octopus Agile half-hourly prices, used as the cost and price-reference series.
- **Real demand response:** the Low Carbon London 2013 **dynamic ToU trial**. About 1,100 households saw High / Normal / Low price signals (67.20p / 11.76p / 3.99p), so it calibrates how demand actually responds to price.
- **Validated OPE:** off-policy estimators are first validated on the **Open Bandit Dataset**, which logs two real policies. The estimate for one policy can be checked against the other policy's actual on-policy results.

It shares data with Project 4, so the portfolio tells one energy story.

## Data

| Source | What | Access | Licence |
|--------|------|--------|---------|
| [Octopus Energy Agile tariff API](https://developer.octopus.energy/) | Half-hourly unit rates by region (A–P), Feb 2018–present | Public endpoints, no key; history split across product codes (stitch AGILE-18-02-21 … AGILE-24-10-01) | **No explicit licence found**: fetch via script, don't redistribute raw data |
| Low Carbon London (see Project 4) | ToU trial households, price schedule, half-hourly consumption | London Datastore | CC BY |
| [Open Bandit Dataset](https://research.zozo.com/data_release/open_bandit_dataset.zip) (ZOZOTOWN) | ~26M logged recommendations, 2 logging policies (random, Bernoulli TS) with true propensities | Direct download (413 MB) | CC BY 4.0 (per paper); research use |
| **Own simulator** | Household demand as a function of price, time and weather, with elasticities fitted to the LCL trial | In repo | MIT |
| *Optional:* UK Fuel Finder | Station-level fuel prices, updated within 30 min of changes (statutory since Feb 2026) | GOV.UK One Login + OAuth API; **no official archive**, so snapshots must be collected | OGL v3 + fair-use policy |

## Scope

**Must have**
- **Elasticity estimation** from the LCL trial: response by time of day and household group, with uncertainty. Use a hierarchical Bayesian model if Project 4's PyMC work is done; otherwise a regression.
- **Simulator** with known "true" elasticities drawn from that posterior, weather-driven baseline demand and Agile-derived wholesale costs.
- **Optimiser:** a constrained schedule (margin floor, Ofgem-style price cap, max step change between half-hours), solved as an LP/MIP or with CP-SAT (linking to Project 1).
- **Bandit:** Thompson sampling over price levels per segment, learning online in the simulator, with cumulative regret against the oracle optimum.
- **OPE:**
  - IPS, SNIPS and doubly-robust estimators.
  - Validate them on Open Bandit (estimate vs actual performance of the other policy), then apply them to the simulator's logs.

**Stretch**
- Fuel Finder competitor-response extension: model how nearby stations react to a price change (spatial neighbours + timestamped updates). Start collecting snapshots early if you want this.
- Fairness constraint: cap bill increases for low-usage households.

**Out of scope:** full reinforcement learning (RL), and real wholesale trading.

## Design decisions to write up

- Explore vs exploit when "exploration" means charging customers different prices (ethics and regulation).
- Why OPE matters before deployment, and where it breaks: support mismatch, high variance.
- Simulator validity: which conclusions transfer to reality and which don't.

## Risks and gotchas

- **LCL trial design:** confirm how households were assigned to ToU vs standard before claiming causal elasticities. If assignment wasn't randomised, say so and treat the elasticities as associational.
- **Octopus history** spans several product codes and regional suffixes. Stitch carefully and test for gaps.
- **Open Bandit's reward is clicks, not revenue.** It validates the estimators, not the pricing.

## Done when

- [ ] Regret curve (bandit vs oracle vs static tariff) in the README
- [ ] OPE validation table on Open Bandit (estimated vs actual)
- [ ] Optimiser respects every constraint, with property-based tests to prove it
- [ ] Interactive Streamlit: move the constraints and see the schedule and margin change
