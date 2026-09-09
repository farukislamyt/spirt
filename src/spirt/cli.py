from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from spirt import __version__
from spirt.collection import CollectionStatus
from spirt.discovery import discover_profiles
from spirt.output import render_result_json
from spirt.providers.registry import get_provider, list_providers
from spirt.reporting import render_report_json, render_report_markdown
from spirt.automation import collect_many

app = typer.Typer(name="spirt", help="Social Profile Intelligence Research Toolkit for public-profile OSINT.", no_args_is_help=True)
console = Console()


@app.command()
def version() -> None:
    """Show the installed SPIRT version."""
    console.print(f"SPIRT {__version__}")


@app.command("providers")
def providers() -> None:
    """List installed platform providers and their safe collection scope."""
    table = Table(title="SPIRT Providers")
    table.add_column("Platform", style="bold")
    table.add_column("Hosts")
    table.add_column("Scope")
    for provider in list_providers():
        caps = getattr(provider, "capabilities", None)
        table.add_row(provider.name, ", ".join(sorted(getattr(caps, "hosts", []))), getattr(caps, "notes", ""))
    console.print(table)


@app.command()
def discover(file: Path = typer.Argument(..., exists=True, readable=True, help="Text/HTML file to scan for supported profile URLs.")) -> None:
    """Discover supported public-profile URLs without contacting them."""
    profiles = discover_profiles(file.read_text(encoding="utf-8", errors="replace"))
    typer.echo(__import__("json").dumps(profiles, indent=2))


@app.command()
def profile(
    url: str = typer.Argument(..., help="Public social-profile URL to research."),
    json_output: bool = typer.Option(False, "--json", help="Output collection result as JSON."),
    evidence: bool = typer.Option(False, "--evidence", help="Show field provenance in human-readable output."),
) -> None:
    """Research publicly available information from a supported profile URL."""
    try:
        provider = get_provider(url)
        result = provider.collect(url)
    except ValueError as exc:
        raise typer.BadParameter(str(exc), param_hint="url") from exc
    except Exception as exc:
        console.print(f"[red]Collection failed:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    if json_output:
        typer.echo(render_result_json(result))
        if result.status is not CollectionStatus.SUCCESS:
            raise typer.Exit(code=1)
        return
    if result.data is None:
        console.print(f"[red]Collection {result.status.value}:[/red] {result.error or 'no data returned'}")
        raise typer.Exit(code=1)

    profile_data = result.data
    table = Table(title="SPIRT Profile")
    table.add_column("Field", style="bold")
    table.add_column("Value")
    for label, value in (("Platform", profile_data.platform), ("Profile URL", profile_data.profile_url),
                         ("Username", profile_data.username or "—"), ("Display name", profile_data.display_name or "—"),
                         ("Profile ID", profile_data.profile_id or "—"), ("Bio", profile_data.bio or "—"),
                         ("Website", profile_data.website or "—"), ("Collection", result.status.value)):
        table.add_row(label, value)
    console.print(table)
    if evidence and profile_data.evidence:
        evidence_table = Table(title="Evidence")
        for column in ("Field", "Value", "Method", "Confidence", "Source"):
            evidence_table.add_column(column, style="bold" if column == "Field" else None)
        for item in profile_data.evidence:
            evidence_table.add_row(item.field, item.value, item.method, f"{item.confidence:.2f}", item.source_url)
        console.print(evidence_table)


@app.command()
def report(
    urls: list[str] = typer.Argument(..., help="One or more supported public-profile URLs."),
    output: Path | None = typer.Option(None, "--output", "-o", help="Write the report to a file."),
    markdown: bool = typer.Option(False, "--markdown", help="Render Markdown instead of JSON."),
) -> None:
    """Collect multiple profiles and generate a correlation-aware report."""
    results = collect_many(urls)
    rendered = render_report_markdown(results) if markdown else render_report_json(results)
    if output:
        output.write_text(rendered, encoding="utf-8")
        console.print(f"Report written to {output}")
    else:
        typer.echo(rendered)
    if any(r.status in {CollectionStatus.FAILED, CollectionStatus.UNAVAILABLE} for r in results):
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
