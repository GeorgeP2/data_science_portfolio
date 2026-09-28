# Project 11: Forecast-to-Procurement Pipeline

**One line:** probabilistic half-hourly demand forecasts for a simulated energy supplier's household
portfolio, fed into day-ahead purchasing decisions and settled against real GB imbalance prices, so
models are compared on the cost of the decisions they drive rather than on forecast error.

**Time box:** ~8 weeks part-time. Flagship of the ML × OR track. Reuses Project 4's data pipeline.

## Headline question

> Does training forecasts for the purchasing decision, rather than for forecast accuracy, lower
> total procurement cost at the same shortfall rate?

## Why it matters

Most forecasting portfolios stop at an error metric, but businesses pay for decisions. This shows
the full chain, and that the best forecast by error isn't always the best for cost.

Day-ahead purchasing is the energy version of inventory: a supplier buys volume before delivery,
then pays the imbalance price for any shortfall and sells any surplus back at a worse price. It's a
newsvendor problem, and the costs are **real market prices, not invented ratios**.

## Data

| Source | What | Access | Licence | Use |
|--------|------|--------|---------|-----|
| [Low Carbon London smart meters](https://data.london.gov.uk/dataset/smartmeter-energy-use-data-in-london-households/) | 5,567 households, half-hourly kWh, Nov 2011–Feb 2014 | London Datastore; shared with Project 4 | CC BY | Supplier portfolio demand (sampled households) |
| [Open-Meteo historical API](https://open-meteo.com/) | Temperature, solar radiation, wind | Free, no key; cached once; shared with Project 4 | CC BY 4.0 data; free tier non-commercial | Forecast features |
| [Elexon BMRS / Insights API](https://bmrs.elexon.co.uk/) | Half-hourly system (imbalance) prices and Market Index Data prices | API, no key | *Unverified*: check terms | Imbalance costs and a wholesale purchase-price proxy |
| *Fallback:* [NESO Historic Demand Data](https://www.neso.energy/data-portal/historic-demand-data) | Half-hourly national demand, 2001–present | CSV per year; shared with Project 4 | NESO Open Data Licence | Scaled national demand if Elexon history doesn't cover the LCL period |

## Scope

**Must have**
- **Portfolio:** a simulated supplier serving portfolios of LCL households at several sizes (e.g. 50, 500, 5,000). Small portfolios are noisy, like intermittent demand.
- **Decision:** a day-ahead purchase volume per half-hour, taken from the forecast distribution at the critical ratio implied by imbalance prices.
- **Baselines:** seasonal naive; LightGBM point forecast with a normal-error assumption.
- **Probabilistic models:** quantile LightGBM, a global deep model (DeepAR-style), and conformal calibration on top.
- **Settlement simulator:** replays the holdout period, buying from each forecast at the purchase-price proxy and settling surplus or shortfall at the real imbalance prices. Tracks purchase cost, imbalance cost and shortfall rate.
- **Decision-focused variant:** tune quantile targets or train on a cost-aligned loss directly.
- **Frontier:** sweep shortfall-rate targets to trace a cost vs shortfall frontier for every method.

**Out of scope:** hedging with forward contracts, generation and trading strategy, retail pricing (that's Project 6).

## Milestones

| Weeks | Milestone | Exit criterion |
|-------|-----------|----------------|
| 1–2 | Data pipeline + settlement simulator | Simulator reproduces hand-computed costs on toy cases; price data covers the LCL period (or fallback chosen) |
| 3–4 | Baselines + probabilistic models | CRPS and coverage reported per model and portfolio size |
| 5–6 | Decision-focused variant | Full frontier for every method |
| 7–8 | Analysis + release | Write-up, interactive frontier plot |

## Deliverables and headline chart

- An interactive **cost vs shortfall-rate frontier** plot for every method.
- A write-up and a reusable settlement-simulation module.

## Design decisions to write up

- Accuracy-optimal vs decision-optimal forecasts, and where they diverge.
- Using a fixed critical ratio vs one that varies with each period's price spread.
- The purchase-price proxy, and how sensitive the conclusions are to it.

## Risks and gotchas

- **Price history may not cover 2011–2014.** Check Elexon's archive first; if it doesn't, pair NESO national demand (scaled to portfolio size) with price data from matching dates.
- **Imbalance pricing changed in 2015** (dual to single price). Check which regime applies to the chosen period and model it correctly; the asymmetry drives the whole decision.
- **The purchase price is a proxy.** Market Index Data isn't what a supplier actually pays. Run a sensitivity analysis on it and show where conclusions hold.
- **Portfolio size dominates noise.** Report results by portfolio size.

## Done when

- [ ] Frontier plot where the decision-aware method dominates at matched shortfall rate, with the gap reported in cost terms and bootstrap confidence intervals
- [ ] Simulator tested against hand-computed toy cases
- [ ] README leads with the frontier plot

**Stack:** Polars, LightGBM, PyTorch, MAPIE or a hand-rolled conformal layer.
