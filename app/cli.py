import asyncio

import click

from app.logs import get_logger
from app.main import main

logger = get_logger(__name__)


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx: click.Context) -> None:
    if ctx.invoked_subcommand is None:
        asyncio.run(main())


@cli.command()
@click.argument("entire-source", type=str)
def update_single_source(entire_source: str):
    """Process all episodes from a source asuming they are new."""
    asyncio.run(main(entire_source))


if __name__ == "__main__":
    cli()
