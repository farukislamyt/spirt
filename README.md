# SPIRT

**Social Profile Intelligence Research Toolkit**

Research public profiles. Discover social intelligence.

SPIRT is an open-source OSINT toolkit for discovering, collecting, normalizing, correlating, and reporting information that is genuinely publicly available on social-profile pages.

## 1.0 architecture

`Provider → Collector → Parser → Normalizer → Evidence → Output`

The toolkit includes:

- Multi-platform provider registry: Facebook, Instagram, LinkedIn, X/Twitter, TikTok, and GitHub.
- Common `CollectionResult` and provider contract.
- Public-web metadata parsing with evidence provenance.
- URL discovery from text/HTML without contacting discovered URLs.
- Explainable cross-platform correlation using explicit shared signals.
- JSON, Markdown, and HTML research reports.
- Batch collection through the CLI and Python API.
- Optional FastAPI service (`spirt[api]`).
- Continuous integration across Python 3.11, 3.12, and 3.13.

## Documentation and web presence

- [Documentation hub](docs/index.md)
- [Getting started](docs/getting-started.md)
- [Provider documentation](docs/providers/index.md)
- [Username OSINT guide](docs/guides/username-osint.md)
- [Profile investigation guide](docs/guides/profile-investigation.md)
- [API reference](docs/api.md)
- [Report schema](docs/report-schema.md)
- [Security and public-data boundary](docs/security/public-data-boundary.md)

The repository also contains a static, SEO-ready public site under `docs/site/`, with canonical metadata, Open Graph tags, JSON-LD structured data, provider landing pages, `robots.txt`, and an XML sitemap. A GitHub Pages deployment workflow is included; the configured Pages URL is the intended public-site canonical.

SPIRT is intentionally positioned around descriptive search intent such as **open-source OSINT toolkit**, **social profile OSINT tool**, **public profile OSINT**, **social media intelligence toolkit**, **OSINT profile investigation**, **cross-platform username OSINT**, and **Python OSINT toolkit** rather than relying on the ambiguous standalone name “SPIRT”.

## CLI

```bash
spirt providers
spirt profile https://www.facebook.com/example --json
spirt discover input.txt
spirt report https://www.facebook.com/example https://github.com/example --markdown
```

Run the API with:

```bash
pip install 'spirt[api]'
uvicorn spirt.api:create_app --factory --host 127.0.0.1 --port 8000
```

## Safety boundary

SPIRT is intentionally limited to legitimately public information and authorized official APIs. It does **not** bypass authentication, private profiles, anti-bot/access controls, rate limits, or other platform protections, and it does not collect credentials or private data.

Platform availability depends on what the target site exposes publicly at collection time. A provider may therefore return `unavailable` even when the URL is valid.

## Roadmap

- [x] v0.4.0 Multi-platform providers
- [x] v0.5.0 Data normalization and evidence
- [x] v0.6.0 Public profile discovery
- [x] v0.7.0 Cross-platform correlation
- [x] v0.8.0 Reports
- [x] v0.9.0 API and automation foundations
- [x] v1.0.0 Stable production release

See `CHANGELOG.md` for release history and `SECURITY.md` for the security policy.
