# Public Profile Investigation Workflow

SPIRT is built for an evidence-first OSINT workflow.

## 1. Define the research target

Start with a public profile URL or a username. Keep the initial hypothesis explicit and avoid assuming that a handle identifies a particular person.

## 2. Resolve candidates

Use deterministic target resolution to generate provider candidates. Resolution itself performs no network access.

## 3. Collect public pages

The collection engine can process multiple URLs concurrently while deduplicating inputs, caching recent results, tracking provider health, and isolating individual failures.

## 4. Inspect normalization and evidence

SPIRT gives normalized profile fields and field-level provenance. Prefer values with clear source URLs and extraction methods.

## 5. Correlate conservatively

Cross-platform correlation uses explicit shared signals and a threshold. The resulting match is an explainable similarity score, **not an identity assertion**.

## 6. Produce a report

Export JSON, Markdown, or HTML for review. Reports contain collection results, correlations, evidence-graph edges, and a deterministic timeline.

## Research discipline

Record what was observed, where it was observed, and when it was collected. Separate evidence from interpretation. Re-check time-sensitive public information before relying on it.
