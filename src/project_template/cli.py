"""The `pt` command line. Typed errors end here as a plain message and a non-zero exit."""

from typing import Annotated

import typer

from project_template import __version__
from project_template.config import load_settings
from project_template.core.greeting import greet
from project_template.errors import ProjectTemplateError
from project_template.logging_setup import configure_logging, new_request_id

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    pretty_exceptions_enable=False,
    help="Placeholder CLI for BearingQuest projects.",
)


def fail(error: ProjectTemplateError) -> typer.Exit:
    typer.echo(f"error: {error}", err=True)
    return typer.Exit(code=1)


@app.command()
def version() -> None:
    """Print the package version."""
    typer.echo(__version__)


@app.command()
def hello(name: Annotated[str, typer.Option("--name", help="Who to greet.")]) -> None:
    """Greet NAME."""
    new_request_id()
    try:
        settings = load_settings()
        logger = configure_logging(settings.log_level)
        logger.info("hello", extra={"command": "hello"})
        typer.echo(greet(name, settings.max_name_length))
    except ProjectTemplateError as error:
        raise fail(error) from None
