# T20: Decision memo

**Phase:** 4 Pipeline and write-up · **Estimate:** 2.5 h · **Depends on:** T10, T17, T19

## Ask

Write a two-page decision memo, "Who should we treat, and what's it worth?", with cost per mailing
as a parameter, saved in `reports/`.

## Why

It's the project's main deliverable and must read like something a product lead could act on.

## How

- Templated (e.g. Jinja → Markdown/PDF) so numbers are filled from pipeline outputs and cost per
  mailing is a config parameter.
- Structure: recommendation first → expected extra outcomes and cost per extra outcome at the chosen
  budget → uncertainty → what would change the recommendation → a short note on experiment speed
  from Part B.
- Neutral, methodological framing: the interest is the design, not the politics.

## Plan

- [ ] Memo template
- [ ] Break-even calculation vs cost per mailing
- [ ] Draft, then cut to two pages
- [ ] Render from `make analysis`

## Acceptance criteria

- [ ] Memo is ≤ 2 pages and opens with a recommendation
- [ ] Changing cost per mailing in config changes the memo's numbers and, past break-even, its recommendation
- [ ] Every number traces to a pipeline output
- [ ] Saved in `reports/`
