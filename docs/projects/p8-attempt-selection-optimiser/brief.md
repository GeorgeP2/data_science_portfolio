# Project 8: Powerlifting Attempt Selection Optimiser

**One line:** a Bayesian decision engine for powerlifting meets. It estimates the probability of
making any attempt weight from millions of competition results, then optimises a lifter's
attempt plan (openers, jumps and when to play safe) to maximise expected total, the chance of
hitting a target total, or expected placing.

**Time box:** weeks 24–26+ (~30 h). Sits alongside Projects 6 and 7.

## Headline questions

> 1. How well can the probability of making an attempt be predicted from the jump size, the
>    attempt number, the previous attempt's outcome and the lifter's history, and are those
>    probabilities **calibrated** on future meets?
> 2. How much expected total (or chance of hitting a qualifying total) does an optimised attempt
>    plan add over the jumps lifters actually choose?
> 3. When does playing safe beat going for it? For example, the value of a conservative
>    third deadlift when chasing a placing rather than a PB (personal best).

## Why this data is different

Nobody else's portfolio has this. It's also the same problem as pricing in different clothes:
a bigger jump is like a higher price, and the chance of making the lift is like conversion. So
it shows **decision-making under uncertainty**, which is the core skill, on data that's
public domain, large and personally engaging. A live demo that real lifters can use is also
far more shareable than another churn model.

## Data

| Source | What | Access | Licence |
|--------|------|--------|---------|
| [OpenPowerlifting bulk CSV](https://openpowerlifting.gitlab.io/opl-csv/) ([column docs](https://openpowerlifting.gitlab.io/opl-csv/bulk-csv-docs.html)) | One row per lifter per meet per division: every attempt `Squat1Kg…Deadlift4Kg` (negative = missed), bests, `TotalKg`, `BodyweightKg`, `WeightClassKg`, `Age`, `Sex`, `Equipment`, `Tested`, `Federation`, `Date`, `Place`; `Name` disambiguated with `#N` | Bulk zip download, regenerated regularly (download size and cadence *unverified*) | **Public domain**; attribution encouraged, so credit OpenPowerlifting in the README and demo |

## Scope

**Must have**
- **Data preparation:**
  - Filter to meets that report **all attempts** (many only report best lifts).
  - Deduplicate lifters entered in multiple divisions at one meet.
  - Handle DQ/DD/NS/Guest `Place` codes, 4th attempts (excluded from totals), lb→kg rounding artefacts and approximate ages (`.5`).
  - Time-based train/test split by meet date.
- **Make-probability model:**
  - **Baseline:** logistic regression on the jump percentage, the attempt number and the previous attempt's outcome.
  - **Main model:** a hierarchical Bayesian model in PyMC.
    - Each lifter has a latent "meet-day max" drawn from their history (a progression model).
    - An attempt succeeds if its weight is below that day's max, adjusted for fatigue from earlier attempts.
    - Lifters are pooled within sex × equipment × weight class, which handles lifters with only one or two meets.
  - LightGBM as a flexible comparison.
  - **Evaluate:** log loss, Brier score, calibration plots on future meets, overall and for first-time lifters.
- **Attempt optimiser:**
  - Dynamic programming over the 9 attempts. The state is the best lift so far, the attempt index and the previous outcome.
  - Objectives: expected total; P(total ≥ target); and expected placing against a simulated field drawn from the real entries of comparable meets.
  - Enforce federation increments (2.5 kg) and the "no lower weight after a successful attempt" rule.
- **Retrospective analysis:** compare lifters' actual jump choices with the optimised plan under the fitted model. How much total is left on the table, and where? It's typically on openers and third attempts.
- **Demo:** a Streamlit or Hugging Face Space where the user enters recent bests, bodyweight, equipment and a goal, and gets a recommended attempt plan with make probabilities for each attempt. It uses only what the user types in, with no lookup of named lifters.

**Stretch**
- **Natural experiment:** a difference-in-differences or regression discontinuity analysis around a federation rule change, e.g. a weight-class restructure. The specific change needs verifying first. This links to Project 3.
- **Live updating:** after each attempt, update the plan with the outcome by Bayesian updating.

**Out of scope:** training recommendations, and anything that analyses individual athletes' drug-testing outcomes.

## Design decisions to write up

- **Latent strength vs direct classifier:** why a generative "meet-day max" model gives more sensible behaviour when extrapolating (e.g. big jumps) than a black-box classifier.
- **Evaluating a policy that was never deployed:** only the outcomes of the attempts lifters actually chose are observed. Explain what can and can't be claimed, which links to off-policy evaluation in Project 6.
- **Choice of objective:** expected total, hitting a target total and expected placing lead to different risk behaviour.
- **Pooling structure:** which groupings matter, and evidence for them.

## Risks and gotchas

- **Selection bias:** lifters choose attempts they believe they'll make, so jump size is confounded with how the lifter feels on the day. The latent-strength model reduces this but doesn't remove it; state the limitation.
- **Missing attempts:** attempt-level data is missing for many federations and older meets, so report coverage after filtering.
- **Identity:** name disambiguation is imperfect, so treat lifter histories as noisy.
- **Real people:** the data names real individuals and includes doping disqualifications. Publish aggregate results and models only. No lifter profiles, leaderboards of "worst attempt selectors", or anything that singles someone out.

## Done when

- [ ] Calibration plot of make probability on held-out future meets in the README
- [ ] "Total left on the table" chart, by attempt and by lift
- [ ] Optimiser respects federation rules, with property-based tests to prove it
- [ ] Live demo with OpenPowerlifting credited
