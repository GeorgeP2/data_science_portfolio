# T16: Demo app

**Phase:** 5 Demo · **Estimate:** 2.5 h · **Depends on:** T10, T13, T14

## Ask

Build a Streamlit app where the user enters recent bests, bodyweight, equipment and a goal, and gets a
recommended attempt plan with make probabilities for each attempt.

## Why

A demo real lifters can use is the most shareable output, and it's a "Done when" criterion.

## How

- Inputs come only from the form; no lookup of named lifters.
- Output: recommended openers and a decision table for 2nd/3rd attempts after a make or miss, with
  P(make) and the objective value for each.
- Loads the compact model artefact from T10; OpenPowerlifting credit in the footer.

## Plan

- [ ] Input form and validation
- [ ] Plan table with per-attempt probabilities
- [ ] Objective selector (expected total / target total / placing)
- [ ] Credit and a short "how it works and limitations" section

## Acceptance criteria

- [ ] Runs locally with one command
- [ ] Returns a plan in under 2 s
- [ ] No name field and no lifter lookup
- [ ] OpenPowerlifting is credited on the page
