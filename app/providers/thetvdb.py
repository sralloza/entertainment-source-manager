from bs4 import BeautifulSoup, Tag
from dateutil.parser import parse as parse_date

from app.core.common import BaseRepository
from app.models.episodes import ScheduledEpisode
from app.models.inputs import TheTVDBInputs
from app.models.source import Source


class TheTVDBProvider(BaseRepository):
    def __init__(self) -> None:
        super().__init__("https://thetvdb.com/series")

    async def process_source(self, source: Source) -> list[ScheduledEpisode]:
        inputs: TheTVDBInputs = source.inputs  # type: ignore
        path = f"/{inputs.source_encoded_name}/allseasons/official"
        soup = await self._send_request_soup("GET", path)
        return self._parse_episodes(soup, inputs, source)

    def _parse_episodes(
        self, doc: BeautifulSoup, inputs: TheTVDBInputs, source: Source
    ) -> list[ScheduledEpisode]:
        return [
            self._build_episode(inputs, el, source)
            for el in doc.select("li.list-group-item")
            if "list-group-item-special" not in el["class"]
        ]

    def _build_episode(self, inputs: TheTVDBInputs, tag: Tag, source: Source) -> ScheduledEpisode:
        headings = tag.select(".list-group-item-heading")
        season, chapter_number = map(
            int, headings[0].text.split(" ")[0].replace("S", "").split("E")
        )

        chapter_id = f"{season}x{chapter_number:02d}"
        release_parts = tag.select(".list-inline > li")

        if len(release_parts) > 1:
            date = parse_date(release_parts[0].text).date()
            platform = release_parts[1].text
        else:
            date = None
            platform = release_parts[0].text

        return ScheduledEpisode(
            source_name=inputs.source_name,
            chapter_id=chapter_id,
            released_date=date,
            platform=platform,
            source=source,
        )
