# T17: Interactive Streamlit app

**Phase:** 6 App and write-up · **Estimate:** 2 h · **Depends on:** T10, T11

## Ask

Build a Streamlit app where the user moves the constraints (price cap, margin floor, max step) and sees
the optimal schedule and margin change.

## Why

This is a "done when" item. It makes the trade-offs between constraints tangible without reading code.

## How

- Sliders for each constraint, plus a picker for the day/cost path and the segment.
- Plots: price schedule vs cost, demand before/after, margin. Highlight the binding constraints.
- Show an infeasible status clearly rather than erroring.
- Cache optimiser results. Host on a free tier if cheap (Streamlit Community Cloud); ship a small
  precomputed input so the app needs no raw data.

## Plan

- [ ] Layout and controls
- [ ] Wire to the optimiser with caching
- [ ] Infeasible-state UI
- [ ] Deploy (optional) and add the link to the README

## Acceptance criteria

- [ ] `streamlit run` works from the project folder with only committed files
- [ ] Every constraint slider changes the schedule or margin when it binds
- [ ] Conflicting settings show "infeasible" and don't crash
- [ ] Each interaction updates in under 2 s
