# SPIRT Research Report Schema

SPIRT reports use schema version `1.0`.

The public JSON Schema is available at [`schema/report-1.0.json`](../schema/report-1.0.json).

## Top-level fields

- `tool` — `SPIRT`.
- `schema_version` — report schema version.
- `generated_at` — UTC generation timestamp.
- `results` — collection results.
- `correlations` — explainable cross-platform similarity matches.
- `evidence_graph` — typed edges for qualifying explicit signals.
- `timeline` — deterministic report events derived from collection order.

The schema intentionally permits additional properties so the report format can evolve without making older consumers reject useful metadata.
