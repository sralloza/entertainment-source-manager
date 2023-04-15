import re
from logging import getLogger

from bs4 import BeautifulSoup, Tag
from click import ClickException
from dateutil.parser import parse as parse_date

from app.core.common import BaseRepository
from app.models.episodes import ScheduledEpisode
from app.models.inputs import TheTVDBInputs
from app.models.source import Source

logger = getLogger(__name__)


class TheTVDBProvider(BaseRepository):
    def __init__(self) -> None:
        super().__init__("https://thetvdb.com/series")

    async def process_source(self, source: Source) -> list[ScheduledEpisode]:
        inputs: TheTVDBInputs = source.inputs  # type: ignore
        soup0 = await self._send_request_soup("GET", f"/{inputs.source_encoded_name}")
        self._log_finished_series(soup0, inputs.source_name)

        path = f"/{inputs.source_encoded_name}/allseasons/official"
        soup1 = await self._send_request_soup("GET", path)
        return self._parse_episodes(soup1, inputs, source)

    def _log_finished_series(self, soup: BeautifulSoup, source_name: str) -> None:
        series_basic_info = self._get_series_basic_info_map(soup)
        if series_basic_info.get("Status") == "Ended":
            logger.warning("Series %r has ended", source_name)

    @staticmethod
    def _get_series_basic_info_map(soup: BeautifulSoup) -> dict[str, str]:
        container = soup.find("div", id="series_basic_info")
        if not container:
            raise ClickException("Could not find series basic info")
        output: dict[str, str] = {}
        for group in container.find_all("li"):  # type: ignore
            title = group.find("strong").text
            content = "".join([x.text.strip() for x in group.find_all("span")])
            content = re.sub(r"[\s\n]+", " ", content)
            output[title] = content
        return output

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
