# SPIRT — Social Profile Intelligence Research Toolkit

SPIRT is an open-source Python OSINT toolkit for researching **genuinely public social-profile information**.

It discovers profile URLs, collects public metadata, normalizes profile fields, preserves evidence provenance, correlates explicit cross-platform signals, and produces research reports.

## Start here

- [Getting Started](getting-started.md) — install SPIRT and run your first collection.
- [Providers](providers/index.md) — supported social-profile platforms and their public-data scope.
- [Username OSINT](guides/username-osint.md) — deterministic username-to-profile discovery.
- [Profile Investigation](guides/profile-investigation.md) — an explainable research workflow.
- [API](api.md) — optional FastAPI service.
- [Report Schema](report-schema.md) — machine-readable report structure.
- [Security & Public-Data Boundary](security/public-data-boundary.md) — what SPIRT does and does not collect.

## What SPIRT is

SPIRT — **Social Profile Intelligence Research Toolkit** — is designed for public-profile OSINT, social media intelligence research, and cross-platform profile analysis where the underlying information is legitimately accessible without bypassing authentication or access controls.

### Core pipeline

`Provider → Collector → Parser → Normalizer → Evidence → Output`

### Key capabilities

- Multi-platform provider architecture.
- Public-web metadata collection.
- Deterministic normalization and provenance.
- Profile URL discovery from text or HTML without contacting discovered URLs.
- Explainable cross-platform correlation using explicit shared signals.
- JSON, Markdown, and HTML research reports.
- Batch collection with concurrency, caching, and graceful degradation.
- Optional FastAPI application.

## Search topics

SPIRT is useful when you are looking for an **open-source OSINT toolkit**, **social profile OSINT tool**, **public profile investigation toolkit**, **social media intelligence toolkit**, or a **Python OSINT toolkit** for research based on public information.

## Safety boundary

SPIRT does not bypass authentication, private profiles, anti-bot or access-control mechanisms, rate limits, or other platform protections. It does not collect credentials or private data. Provider behavior depends on what a target platform exposes publicly at collection time.
