from app.models.episodes import NonScheduledEpisode, ScheduledEpisode
from app.models.source import Source
from app.providers.inmanga import InMangaProvider
from app.providers.spyxfamily import SpyXFamilyProvider
from app.providers.thetvdb import TheTVDBProvider

_LS = list[ScheduledEpisode]
_LNS = list[NonScheduledEpisode]

inmanga_provider = InMangaProvider()
thetvdb_provider = TheTVDBProvider()
spyxfamily_provider = SpyXFamilyProvider()


async def process_source(source: Source) -> _LS | _LNS:
    if source.provider == "InManga":
        return await inmanga_provider.process_source(source)
    elif source.provider == "TheTVDB":
        return await thetvdb_provider.process_source(source)
    elif source.provider == "SpyXFamily":
        return await spyxfamily_provider.process_source(source)
    else:
        raise ValueError(f"Invalid provider: {source.provider}")
