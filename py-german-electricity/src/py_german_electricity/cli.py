"""Console script for py_german_electricity."""

import typer
from rich.console import Console

from py_german_electricity import utils

app = typer.Typer()
console = Console()


@app.command()
def main() -> None:
    """Console script for py_german_electricity."""
    console.print("Replace this message by putting your code into "
               "py_german_electricity.cli.main")
    console.print("See Typer documentation at https://typer.tiangolo.com/")
    utils.do_something_useful()


if __name__ == "__main__":
    app()
