# Signal Contract v1 — render-provenance extension

**Status:** draft (promotion gate satisfied — see Provenance below)
**Type:** additive extension to v1; does NOT modify `schema.json`
**Authority:** VIBEnet
**Last updated:** 2026-05-16

## Purpose

Signal Contract v1 defines the **event** object. This extension defines the
companion **render-provenance** signals that a rendered surface (HTML page,
voice utterance, ambient display) emits so external probes can verify how
old the SOURCE DATA was at render time, INDEPENDENTLY of how old the cached
render is.

Without these signals, a fresh cache built on stale source data is
indistinguishable from a fresh-source-fresh-cache page. The signals make the
gap observable from a single read.

## Why this is here

The reference SerpRadio implementation went 12 days with stale price data
behind a fresh-looking materialized HTML cache before the gap surfaced. The
post-incident contract (SerpRadio's `contracts/data_fidelity_signals.yaml`)
declared the vocabulary; this document promotes it into the Signal Contract
spec so other renderers can adopt the same shape and downstream consumers
can interpret it uniformly.

## Promotion gate

A render-provenance signal is promoted into this extension only when
**≥ 2 independent consumers** depend on it. The initial promotion (this
document) satisfies the gate via three SerpRadio consumers shipping in the
same release:

1. Cloudflare Pages edge — `serpradio-frontend/functions/[[path]].ts`
2. Screaming Frog audit — `serpradio-frontend/tools/screaming_frog_unified_audit.py`
3. Render-provenance probe — `serpradio-frontend/app/lib/render-provenance-probe.ts`

The producer is `tgflightsfromnyc/src/shell_renderer/engine.py`. Reference
PRs are listed at the bottom of this file.

## The HTML attribute family

A renderer emitting HTML SHOULD attach the following attributes to the
`<html>` root element when source data is present:

| Attribute | Type | Semantic |
| --- | --- | --- |
| `data-source-freshness` | ISO 8601 UTC string | Timestamp of the most recent upstream observation reflected in the page. NOT the render time. NOT the cache age. |
| `data-source-freshness-sec` | non-negative integer | Seconds elapsed between `data-source-freshness` and render time. Clock-skew negative values clamp to `0`. |
| `data-source-freshness-scope` | snake_case identifier | Names the upstream system whose timestamp the freshness refers to (e.g. `price_observations`, `gsc_imports`, `riff_bank`). |

### Required-when / forbidden-when-absent

- **Required when** source data is present in the render payload.
- **Forbidden when** source data is absent. The attributes MUST NOT be
  emitted with empty, `null`, or `"unknown"` values — legacy probes must
  not see a misleading "fresh" marker.

## The response-header family (edge mirror)

A renderer or edge layer serving the HTML SHOULD mirror the freshness on the
response:

| Header | Source | Semantic |
| --- | --- | --- |
| `x-source-freshness-sec` | parsed from `data-source-freshness-sec` | Seconds since the source observation. Omitted when the HTML did not carry the attribute. |
| `x-source-freshness-scope` | parsed from `data-source-freshness-scope` | Mirror of the scope identifier. |
| `x-cache-freshness-sec` _(or implementation-specific equivalent)_ | computed at serve time | Seconds since the cached render was produced. This is the **cache** age, distinct from the source age. |

**The two ages MUST be reported as independent fields.** A consumer
receiving fresh cache + stale source is the canonical signal that the
collector is behind; the contract makes it observable. Edge layers MUST NOT
synthesize one from the other when the source signal is absent.

## Conformance — L1 invariants

A renderer is L1-conformant on render-provenance when:

1. **Present-when-data:** Attributes appear on `<html>` whenever the render
   payload carried source-data timestamp(s).
2. **Machine-readable:** Integer seconds parse as non-negative; ISO
   timestamp parses with `Date.parse` / equivalent.
3. **SLA-classified:** Consumers classify the value against the scope's
   `fresh` / `stale` / `critically_stale` thresholds. The page is NOT
   considered fresh just because the cache is fresh.
4. **Cache-and-source split:** Cache age and source age are surfaced as
   separate fields. The test fails if source age is hidden by a fresh cache
   age in any consumer surface.

Reference fixtures: `conformance/l1/render_provenance.jsonl` in this repo.
Renderers MAY add per-scope SLA defaults in their own configuration; the
spec only requires the visibility + classification semantics.

## What this extension does NOT assert

- **A maximum age bound.** Source data CAN legitimately be older than the
  cache (e.g. weekly-cadence routes between collection runs). The spec
  asserts visibility + classification, not a numerical ceiling.
- **A scope vocabulary.** Renderers declare their own scopes
  (`price_observations`, `gsc_imports`, `riff_bank`, etc.). The spec
  asserts only that the scope is a stable snake_case identifier.
- **Changes to the core event `schema.json`.** This extension is additive;
  it lives alongside the v1 event schema and does not modify it.

## Operating law

> Consuming layers do not invent truth.

Each layer reports the freshness of what it is serving. Downstream layers
must not silently upgrade a stale upstream into a fresh-looking response.
Missing freshness signals are reported as absent, NOT as zero.

## Provenance

| Item | Reference |
| --- | --- |
| Producer (reference implementation) | `tgflightsfromnyc/src/shell_renderer/engine.py` |
| Render PR | jamesfgibbons/tgflightsfromnyc#699 |
| Edge + probe PR | jamesfgibbons/serpradio-frontend#905 |
| Authoritative downstream contract | `serpradio-cms/contracts/data_fidelity_signals.yaml` (jamesfgibbons/serpradio-cms#48) |
| Source-authority routing | `serpradio-cms/contracts/source_authority.yaml` ("How old is the source data on this rendered page?") |
| Originating incident | SerpRadio `FARE SUPPRESSED` — 12-day stale-source-behind-fresh-cache gap, May 2026 |

## Compatibility

This extension is **additive**. Existing v1 producers, adapters, and
renderers continue to conform without modification. Renderers that emit
HTML and want to participate in render-provenance L1 SHOULD adopt the
attributes/headers above; those that don't are unaffected.
