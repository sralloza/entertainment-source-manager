import re

from bs4 import Tag

from app.core.common import BaseRepository
from app.models.episodes import NonScheduledEpisode
from app.models.source import Source


class SpyXFamilyProvider(BaseRepository):
    def __init__(self) -> None:
        super().__init__("https://w12.spyxmanga.com")

    async def process_source(self, source: Source) -> list[NonScheduledEpisode]:
        doc = await self._send_request_soup("GET", "/")
        episodes = self.build_episodes(doc, source)
        return self.filter_episodes(episodes)

    def build_episodes(self, doc: Tag, source: Source) -> list[NonScheduledEpisode]:
        chapters_source = doc.select("#ceo_latest_comics_widget-3")[0].select("li a")
        return [self.build_episode(episode, source) for episode in chapters_source]

    def build_episode(self, episode: Tag, source: Source) -> NonScheduledEpisode:
        chapter_id = re.sub("[a-zA-Z, ]", "", episode.text)
        urls = episode["href"]
        url = urls if isinstance(urls, str) else urls[0]
        return NonScheduledEpisode(
            source_name="Spy X Family",
            chapter_id=chapter_id,
            chapter_url=url,
            source=source,
        )

    def filter_episodes(self, episodes: list[NonScheduledEpisode]) -> list[NonScheduledEpisode]:
        output = {}
        for episode in episodes:
            if episode.chapter_id not in output:
                output[episode.chapter_id] = episode
            else:
                # For duplicate chapters, keep the one with the shortest URL
                old_url = output[episode.chapter_id].chapter_url
                new_url = episode.chapter_url
                if len(new_url) < len(old_url):
                    output[episode.chapter_id] = episode
        return sorted(output.values(), key=lambda x: float(x.chapter_id))
