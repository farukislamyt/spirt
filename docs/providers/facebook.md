# Facebook OSINT Provider

The Facebook provider handles supported Facebook profile URLs and extracts public-web metadata exposed by the target page.

## Scope

Typical normalized fields include display name, profile URL, username when exposed, bio/description, public website links, public image metadata, and field-level evidence.

## Limitations

Facebook may expose different metadata depending on page type, region, consent state, or collection time. SPIRT does not bypass login walls, private profiles, anti-bot controls, or other access restrictions.
