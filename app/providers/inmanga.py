from bs4 import Tag

from app.core.common import BaseRepository
from app.models.episodes import NonScheduledEpisode
from app.models.inputs import InMangaInputs
from app.models.source import Source

INMANGA_HTML_TEMPLATE = "https://inmanga.com/ver/manga/{}/{}/{}"


class InMangaProvider(BaseRepository):
    def __init__(self) -> None:
        super().__init__("https://inmanga.com/chapter/chapterIndexControls")

    async def process_source(self, source: Source) -> list[NonScheduledEpisode]:
        inputs: InMangaInputs = source.inputs  # type: ignore
        path = "?identification=" + str(inputs.first_chapter_id)
        soup = await self._send_request_soup("GET", path)
        elements = soup.select("#ChapList")[0].select("option")
        return [self._parse_tag(element, inputs, source) for element in elements]

    def _parse_tag(self, tag: Tag, inputs: InMangaInputs, source: Source) -> NonScheduledEpisode:
        chapter_id = self._process_chapter_id(tag.text.replace(",", ""))
        chapter_uuid = tag["value"]
        chapter_url = INMANGA_HTML_TEMPLATE.format(
            inputs.source_encoded_name, chapter_id, chapter_uuid
        )
        return NonScheduledEpisode(
            source_name=inputs.source_name,
            chapter_id=chapter_id,
            chapter_url=chapter_url,
            source=source,
        )

    def _process_chapter_id(self, chapter_id: str) -> str:
        chapter_id = chapter_id.lstrip("0")
        if not chapter_id:
            return "0"
        as_float = float(chapter_id)
        as_int = int(as_float)
        if as_float == as_int:
            return str(as_int)
        return chapter_id
