from __future__ import annotations

import json
from datetime import datetime, timezone

from spirt.collection import CollectionResult
from spirt.correlation import correlate


def build_report(results: list[CollectionResult]) -> dict[str, object]:
    profiles = [r.data for r in results if r.data is not None and hasattr(r.data, "platform")]
    return {
        "tool": "SPIRT",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "results": [r.to_dict() for r in results],
        "correlations": [m.to_dict() for m in correlate(profiles)],
    }


def render_report_json(results: list[CollectionResult]) -> str:
    return json.dumps(build_report(results), indent=2, ensure_ascii=False)


def render_report_markdown(results: list[CollectionResult]) -> str:
    report = build_report(results)
    lines = ["# SPIRT Research Report", "", f"Generated: `{report['generated_at']}`", "", "## Profiles"]
    for result in results:
        profile = result.data
        if profile is None:
            lines.append(f"- **{result.status.value}** — {result.error or 'no data'}")
            continue
        lines.extend([
            f"- **{profile.platform}** — {profile.display_name or profile.username or profile.profile_url}",
            f"  - URL: {profile.profile_url}",
            f"  - Username: {profile.username or '—'}",
            f"  - Website: {profile.website or '—'}",
            f"  - Status: {result.status.value}",
        ])
    lines += ["", "## Correlations"]
    correlations = report["correlations"]
    if not correlations:
        lines.append("No correlations met the default threshold.")
    else:
        for match in correlations:
            lines.append(f"- `{match['left_platform']}` ↔ `{match['right_platform']}` — {match['score']:.2f} ({', '.join(match['reasons'])})")
    return "\n".join(lines) + "\n"
