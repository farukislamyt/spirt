# Username OSINT with SPIRT

Username-based OSINT starts with a hypothesis, not an identity claim. SPIRT can turn a username into deterministic provider URL candidates and let the collection engine evaluate those URLs.

## Workflow

1. Normalize the username by removing a leading `@` when present.
2. Generate candidates only from provider URL templates explicitly supplied by the application.
3. Collect supported public pages.
4. Preserve evidence for every normalized value.
5. Compare profiles using explicit signals such as username, website, shared links, and display name.
6. Review the evidence before making any attribution.

## Important distinction

A matching username is a **signal**, not proof that two profiles belong to the same person. Reused handles, impersonation, organizational accounts, and coincidental matches are common.

## Safety

Use SPIRT only for legitimately public information and authorized research. Do not use it to bypass authentication, private profiles, access controls, anti-bot systems, or rate limits.
