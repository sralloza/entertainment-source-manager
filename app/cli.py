import asyncio

import click

from app.logs import get_logger
from app.main import main

logger = get_logger(__name__)


@click.command()
def cli() -> None:
    asyncio.run(main())


if __name__ == "__main__":
    cli()
