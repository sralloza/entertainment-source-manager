import asyncio

from click import ClickException

from app.core.non_scheduled import process_non_scheduled_episodes
from app.core.scheduled import process_scheduled_episodes
from app.logs import get_logger
from app.models.episodes import NonScheduledEpisode, ScheduledEpisode
from app.models.source import Source
from app.providers import process_source
from app.settings import get_sources

logger = get_logger(__name__)


async def get_episodes_from_source(
    source: Source,
) -> list[ScheduledEpisode] | list[NonScheduledEpisode]:
    result = await process_source(source)
    logger.debug("Found %d episodes for %s", len(result), source.inputs.source_name)
    return result


async def _main() -> None:
    sources = get_sources()
    tasks = [get_episodes_from_source(source) for source in sources]
    episodes_nested = await asyncio.gather(*tasks)
    episodes = [item for sublist in episodes_nested for item in sublist]

    scheduled_eps = [x for x in episodes if isinstance(x, ScheduledEpisode)]
    non_scheduled_eps = [x for x in episodes if isinstance(x, NonScheduledEpisode)]

    logger.info("Found %d scheduled episodes", len(scheduled_eps))
    logger.info("Found %d non-scheduled episodes", len(non_scheduled_eps))

    await process_scheduled_episodes(scheduled_eps)
    await process_non_scheduled_episodes(non_scheduled_eps)


async def main() -> None:
    try:
        await _main()
    except Exception as e:
        logger.exception("Internal error", stack_info=True)
        raise ClickException("Internal error: " + str(e))
