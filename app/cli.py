import asyncio

import click

from app.logs import get_logger
from app.main import main
from app.show import print_source_names, print_sources

logger = get_logger(__name__)


@click.group(invoke_without_command=True, context_settings={"help_option_names": ["-h", "--help"]})
@click.pass_context
def cli(ctx: click.Context) -> None:
    if ctx.invoked_subcommand is None:
        asyncio.run(main())


@cli.command()
@click.argument("entire-source", type=str)
def update_single_source(entire_source: str) -> None:
    """Process all episodes from a source asuming they are new.

    This command only creates todoist tasks, it does not send telegram notifications
    for non scheduled episodes.
    """
    asyncio.run(main(entire_source))


@cli.group("print")
def print_cli() -> None:
    pass


@print_cli.command("sources")
def print_helper_sources() -> None:
    print_sources()


@print_cli.command("source-names")
def print_helper_source_names() -> None:
    print_source_names()


if __name__ == "__main__":
    cli()
