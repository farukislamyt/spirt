# Public-Data Security Boundary

SPIRT is intentionally designed around legitimately public information.

## In scope

- Public profile pages and metadata.
- Public URLs supplied by the researcher.
- Publicly exposed profile fields and links.
- Authorized official APIs when a provider explicitly supports them.

## Out of scope

- Authentication or login bypass.
- Private or restricted profiles.
- Credential collection.
- Circumventing anti-bot or access-control systems.
- Circumventing rate limits.
- Accessing private application data.

## Network safety

SPIRT's public HTTP layer requires HTTPS, rejects URL credentials, resolves hostnames, and rejects non-global destination IPs. Redirect targets are revalidated and response bodies are bounded. These controls reduce SSRF risk but do not constitute a mathematical guarantee against every DNS-rebinding or TOCTOU scenario.

## Interpretation

Collection results describe what was publicly observable at collection time. They should not be interpreted as proof of identity, ownership, intent, or offline attributes.
