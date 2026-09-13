from __future__ import annotations

import html
import json
from datetime import UTC, datetime
from typing import Any

from spirt.collection import CollectionResult
from spirt.correlation import correlate
from spirt.intelligence import build_evidence_graph
from spirt.report_schema import REPORT_SCHEMA_VERSION, validate_report


def _timestamp() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def _timeline(results: list[CollectionResult]) -> list[dict[str, Any]]:
    return [
        {
            "index": index,
            "platform": result.data.platform if result.data is not None and hasattr(result.data, "platform") else None,
            "url": result.data.profile_url if result.data is not None and hasattr(result.data, "profile_url") else None,
            "status": result.status.value,
        }
        for index, result in enumerate(results)
    ]


def build_report(results: list[CollectionResult], *, generated_at: str | None = None) -> dict[str, object]:
    profiles = [r.data for r in results if r.data is not None and hasattr(r.data, "platform")]
    graph = build_evidence_graph(profiles)
    report = {
        "tool": "SPIRT",
        "schema_version": REPORT_SCHEMA_VERSION,
        "generated_at": generated_at or _timestamp(),
        "results": [r.to_dict() for r in results],
        "correlations": [m.to_dict() for m in correlate(profiles)],
        "evidence_graph": [edge.to_dict() for edge in graph],
        "timeline": _timeline(results),
    }
    validate_report(report)
    return report


def render_report_json(results: list[CollectionResult], *, generated_at: str | None = None) -> str:
    return json.dumps(build_report(results, generated_at=generated_at), indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def render_report_markdown(results: list[CollectionResult], *, generated_at: str | None = None) -> str:
    report = build_report(results, generated_at=generated_at)
    lines = [
        "# SPIRT Research Report",
        "",
        f"- Schema: `{report['schema_version']}`",
        f"- Generated: `{report['generated_at']}`",
        "",
        "## Profiles",
    ]
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
    lines += ["", "## Evidence Graph"]
    graph = report["evidence_graph"]
    if not graph:
        lines.append("No explicit evidence links met the default threshold.")
    else:
        for edge in graph:
            lines.append(f"- `{edge['left_platform']}` `{edge['signal']}` `{edge['right_platform']}` — weight `{edge['weight']:.2f}`")
    lines += ["", "## Timeline"]
    for event in report["timeline"]:
        lines.append(f"- `{event['index']}` — `{event['status']}` — {event['platform'] or 'unknown'} — {event['url'] or 'no URL'}")
    return "\n".join(lines) + "\n"


def render_report_html(results: list[CollectionResult], *, generated_at: str | None = None) -> str:
    """Render a self-contained, static HTML investigation report."""
    report = build_report(results, generated_at=generated_at)
    rows = []
    for result in results:
        profile = result.data
        name = profile.display_name or profile.username or profile.profile_url if profile is not None else "—"
        url = profile.profile_url if profile is not None else "—"
        platform = profile.platform if profile is not None else "—"
        rows.append(f"<tr><td>{html.escape(platform)}</td><td>{html.escape(name)}</td><td>{html.escape(url)}</td><td>{html.escape(result.status.value)}</td></tr>")
    graph_rows = "".join(
        f"<li><code>{html.escape(edge['left_platform'])}</code> — {html.escape(edge['signal'])} → <code>{html.escape(edge['right_platform'])}</code> ({edge['weight']:.2f})</li>"
        for edge in report["evidence_graph"]
    ) or "<li>No explicit evidence links.</li>"
    return """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>SPIRT Research Report</title><style>body{font-family:system-ui,sans-serif;max-width:1100px;margin:2rem auto;padding:0 1rem;line-height:1.5}table{width:100%;border-collapse:collapse}th,td{border:1px solid #ddd;padding:.55rem;text-align:left}code{font-family:ui-monospace,monospace}section{margin-top:2rem}</style></head>
<body><h1>SPIRT Research Report</h1>
<p><strong>Schema:</strong> %s<br><strong>Generated:</strong> %s</p>
<section><h2>Profiles</h2><table><thead><tr><th>Platform</th><th>Name</th><th>URL</th><th>Status</th></tr></thead><tbody>%s</tbody></table></section>
<section><h2>Evidence Graph</h2><ul>%s</ul></section>
<section><h2>Raw Report</h2><pre>%s</pre></section>
</body></html>
""" % (html.escape(str(report["schema_version"])), html.escape(str(report["generated_at"])), "".join(rows), graph_rows, html.escape(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True)))
