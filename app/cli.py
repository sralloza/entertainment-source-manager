import asyncio

import click

from app.logs import get_logger
from app.main import main
from app.show import print_source_names, print_sources

logger = get_logger(__name__)
dry_run = click.option(
    "-n",
    "--dry-run",
    is_flag=True,
    help="Do not send any telegram messages or create any todoist tasks",
)


@click.group(invoke_without_command=True, context_settings={"help_option_names": ["-h", "--help"]})
@dry_run
@click.pass_context
def cli(ctx: click.Context, dry_run: bool) -> None:
    ctx.ensure_object(dict)
    ctx.obj["dry_run"] = dry_run
    if ctx.invoked_subcommand is None:
        asyncio.run(main(dry_run=dry_run))


@cli.command()
@click.argument("entire-source", type=str)
@click.pass_context
def update_single_source(ctx: click.Context, entire_source: str) -> None:
    """Process all episodes from a source asuming they are new.

    This command only creates todoist tasks, it does not send telegram notifications
    for non scheduled episodes.
    """
    dry_run = ctx.obj["dry_run"]
    asyncio.run(main(entire_source=entire_source, dry_run=dry_run))


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
