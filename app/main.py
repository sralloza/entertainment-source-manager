import asyncio

from click import ClickException

from app.core.non_scheduled import process_non_scheduled_episodes
from app.core.scheduled import process_scheduled_episodes
from app.logs import get_logger
from app.models.episodes import NonScheduledEpisode, ScheduledEpisode
from app.models.source import Source
from app.providers import _LNS, _LS, process_source
from app.settings import get_sources, settings

logger = get_logger(__name__)


async def _get_episodes_from_source(source: Source, disable_filter: bool) -> _LS | _LNS:
    if not disable_filter and source.inputs.source_name in settings.disabled_sources:
        logger.info("Source %s is disabled", source.inputs.source_name)
        return []  # type: ignore[return-value]
    result = await process_source(source)
    logger.debug("Found %d episodes for %s", len(result), source.inputs.source_name)
    return result


async def get_episodes_from_source(source: Source, disable_filter: bool) -> _LS | _LNS:
    try:
        return await _get_episodes_from_source(source, disable_filter)
    except Exception:
        template = "Error while processing source %r"
        logger.exception(template, source.inputs.source_name, stack_info=True)
        return []  # type: ignore[return-value]


def filter_sources(sources: list[Source], entire_source: str) -> list[Source]:
    filtered_sources = [x for x in sources if x.inputs.source_name == entire_source]
    if not filtered_sources:
        source_names = ", ".join(repr(x.inputs.source_name) for x in sources)
        msg = f"Invalid source name: {entire_source}. Valid names are: {source_names}"
        raise ClickException(msg)
    return filtered_sources


async def _main(entire_source: str | None) -> None:
    sources = get_sources()
    if entire_source is not None:
        sources = filter_sources(sources, entire_source)

    assume_new = entire_source is not None
    tasks = [get_episodes_from_source(source, disable_filter=assume_new) for source in sources]
    episodes_nested = await asyncio.gather(*tasks)
    episodes = [item for sublist in episodes_nested for item in sublist]

    scheduled_eps = [x for x in episodes if isinstance(x, ScheduledEpisode)]
    non_scheduled_eps = [x for x in episodes if isinstance(x, NonScheduledEpisode)]

    logger.info("Found %d scheduled episodes", len(scheduled_eps))
    logger.info("Found %d non-scheduled episodes", len(non_scheduled_eps))

    await process_scheduled_episodes(scheduled_eps, assume_new=assume_new)
    await process_non_scheduled_episodes(non_scheduled_eps, assume_new=assume_new)


async def main(entire_source: str | None = None) -> None:
    try:
        await _main(entire_source)
    except Exception as e:
        if not isinstance(e, ClickException):
            logger.exception("Internal error", stack_info=True)
            raise ClickException("Internal error: " + str(e))
        raise
