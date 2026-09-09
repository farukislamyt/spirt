from __future__ import annotations

import typer
from rich.console import Console

from spirt import __version__

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
) -> None:
    """Research a public social profile."""
    console.print(f"[bold]SPIRT[/bold] profile target: {url}")
    console.print("Provider collection will be added in the next implementation phase.")


if __name__ == "__main__":
    app()
