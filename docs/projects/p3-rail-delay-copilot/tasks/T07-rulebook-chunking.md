# T07: Section-aware chunking of DAPR, PGDs and rulings

**Phase:** 2 Retrieval · **Estimate:** 3 h · **Depends on:** T03

## Ask

Parse the rulebook documents into chunks by section, keeping section numbers for citation and
recording cross-references between sections.

## Why

Answers must cite DAPR sections. Legal-style text refers to other sections constantly; naive
chunking loses both the citation and the context. This is also a design decision to write up.

## How

- Extract text from the source format; detect section headings by numbering pattern; one chunk per
  section, splitting long sections with the heading repeated.
- Metadata: document, section number, title, page, edition.
- Cross-references: pattern-match "see section X" style references and store them as edges for
  optional expansion at retrieval time.
- Extract the cause-code tables separately as structured rows (also used by T20).

## Plan

- [ ] Text extraction and heading detection
- [ ] Chunker with metadata
- [ ] Cross-reference extraction
- [ ] Cause-code table extraction
- [ ] Spot-check 20 chunks against the source

## Acceptance criteria

- [ ] Every chunk has a document and section number; 20 spot-checked chunks match the source
- [ ] Cross-reference edges are extracted and their count reported
- [ ] Cause-code table is saved as a structured file
- [ ] Chunker tests run on a small text fixture
