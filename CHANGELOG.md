# Changelog

All notable changes to SPIRT are documented here.

## [1.0.0] - 2026-09-10

### Added

- Multi-platform public-profile provider architecture.
- Facebook, Instagram, LinkedIn, X/Twitter, TikTok, and GitHub providers.
- Unified collection results, normalization, and evidence provenance.
- Public profile URL discovery without contacting discovered URLs.
- Explainable cross-platform correlation using explicit shared signals.
- JSON and Markdown research reports.
- Batch collection and optional FastAPI service.
- GitHub Actions CI across Python 3.11, 3.12, and 3.13.

### Fixed

- Corrected the correlation contract test to match the documented weighted scoring model.
- Removed an unused output-module import that failed Ruff checks.
- Kept API version metadata synchronized with the package version.
- Updated the HTTP client user agent for the 1.0 release.
