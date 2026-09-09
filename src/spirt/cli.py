from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from spirt import __version__
from spirt.collection import CollectionStatus
from spirt.output import render_json
from spirt.providers.registry import get_provider

app = typer.Typer(
    name="spirt",
    help="Social Profile Intelligence Research Toolkit for public-profile OSINT.",
    no_args_is_help=True,
)
console = Console()


@app.command()
def version() -> None:
    """Show the installed SPIRT version."""
    console.print(f"SPIRT {__version__}")


@app.command()
def profile(
    url: str = typer.Argument(..., help="Public social-profile URL to research."),
    json_output: bool = typer.Option(False, "--json", help="Output normalized data as JSON."),
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
        typer.echo(render_json(result.data) if result.data is not None else result.to_dict().__repr__())
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
    table.add_row("Platform", profile_data.platform)
    table.add_row("Profile URL", profile_data.profile_url)
    table.add_row("Username", profile_data.username or "—")
    table.add_row("Display name", profile_data.display_name or "—")
    table.add_row("Profile ID", profile_data.profile_id or "—")
    table.add_row("Bio", profile_data.bio or "—")
    table.add_row("Website", profile_data.website or "—")
    table.add_row("Collection", result.status.value)
    console.print(table)

    if evidence and profile_data.evidence:
        evidence_table = Table(title="Evidence")
        evidence_table.add_column("Field", style="bold")
        evidence_table.add_column("Value")
        evidence_table.add_column("Method")
        evidence_table.add_column("Confidence")
        evidence_table.add_column("Source")
        for item in profile_data.evidence:
            evidence_table.add_row(
                item.field,
                item.value,
                item.method,
                f"{item.confidence:.2f}",
                item.source_url,
            )
        console.print(evidence_table)


if __name__ == "__main__":
    app()
