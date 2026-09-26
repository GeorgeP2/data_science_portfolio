# T02: Download and stitch Octopus Agile price history

**Phase:** 0 Setup · **Estimate:** 3 h · **Depends on:** T01

## Ask

Script the download of half-hourly Agile unit rates for every region from Feb 2018 to today, stitch
the product codes into one continuous series per region, and test it for gaps.

## Why

Agile prices are the cost and price-reference series for the simulator and optimiser. The brief
flags stitching across product codes and regional suffixes as a known gotcha; a silent gap or
overlap would bias every margin figure.

## How

- Public Octopus API, no key. List Agile products (AGILE-18-02-21 … AGILE-24-10-01; confirm the
  full list from the products endpoint), then page through standard unit rates per product × region.
- No explicit licence, so fetch by script and never commit raw responses. Cache to `data/raw/octopus/`.
- Stitch: concatenate by `valid_from`, resolve overlaps with a documented rule (e.g. the newer
  product wins), convert to UTC half-hour index.
- Gap check: every half-hour present per region; clock-change days handled (46/50 periods local time).
- Write a tidy parquet to `data/processed/agile.parquet`.

## Plan

- [ ] Confirm product codes and region letters from the API
- [ ] Paginated, rate-limit-friendly downloader with caching
- [ ] Stitching with overlap rule
- [ ] Gap and duplicate checks as tests
- [ ] `data/README.md` entry: source, "no explicit licence, do not redistribute"

## Acceptance criteria

- [ ] One command produces `agile.parquet` for all regions from a clean checkout
- [ ] Zero duplicate half-hours; any remaining gaps are listed with dates and reason
- [ ] Clock-change days have the right number of periods
- [ ] No raw Octopus data is tracked by git
