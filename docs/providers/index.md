# SPIRT Providers

SPIRT uses a provider contract so platform-specific collection remains isolated from normalization, evidence, reporting, and orchestration.

## Supported platforms

| Platform | Provider page | Collection model |
|---|---|---|
| Facebook | [Facebook](facebook.md) | Public-web metadata |
| Instagram | [Instagram](instagram.md) | Public-web metadata |
| LinkedIn | [LinkedIn](linkedin.md) | Public-web metadata |
| X/Twitter | [X/Twitter](x.md) | Public-web metadata |
| TikTok | [TikTok](tiktok.md) | Public-web metadata |
| GitHub | [GitHub](github.md) | Public-web metadata |

Availability is not a guarantee that a platform will expose a particular field. A valid profile URL can still produce an `unavailable` result when public content is inaccessible at collection time.

## Provider contract

A provider declares whether it supports a URL and returns a structured `CollectionResult`. URL routing is syntax-only; network safety is enforced by the HTTP layer immediately before public content is fetched.

## Adding a provider

A new provider should:

1. Declare an exact supported host set.
2. Reuse the common URL parser and host matcher.
3. Collect only legitimately public data or authorized official API data.
4. Preserve evidence for normalized values.
5. Return structured status and error codes.
6. Add offline unit tests for URL routing and collection behavior.
