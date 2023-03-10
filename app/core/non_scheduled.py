import asyncio
from datetime import date
from itertools import groupby

from app.logs import get_logger
from app.models.episodes import NonScheduledEpisode, S3NonScheduledEpisode
from app.models.todoist import TaskCreate
from app.repositories.s3 import S3Repository
from app.repositories.telegram import TelegramRepository
from app.repositories.todoist import TodoistRepository

logger = get_logger(__name__)


async def process_non_scheduled_episodes(episodes: list[NonScheduledEpisode]) -> None:
    today = date.today()
    source_names = {x.source_name for x in episodes}

    s3_repo = S3Repository()
    todoist_repo = TodoistRepository()
    telegram_repo = TelegramRepository()

    s3_episodes = await get_all_episodes(s3_repo, source_names)
    s3_episodes_map = {f"{x.source_name} {x.chapter_id}": x for x in s3_episodes}

    new_episodes_source_names: set[str] = set()
    for episode in episodes:
        task_title = f"{episode.source_name} {episode.chapter_id}"
        s3_episode = s3_episodes_map.get(task_title)

        if not s3_episode:
            logger.info("Creating task and notification for %r", task_title)
            task_content = f"[{task_title}]({episode.chapter_url})"
            task_create = TaskCreate(
                content=task_content,
                description="",
                project_id=episode.source.inputs.todoist_project_id,
                section_id=episode.source.inputs.todoist_section_id,
                due_date=today,
            )
            new_episodes_source_names.add(episode.source_name)
            await todoist_repo.create_task(task_create)
            await telegram_repo.send_message(f"New episode: {task_content}")

    if not new_episodes_source_names:
        logger.info("No new non scheduled episodes")
        return

    await update_s3_info(s3_repo, new_episodes_source_names, episodes)


async def update_s3_info(
    s3_repo: S3Repository,
    new_episodes_source_names: set[str],
    episodes: list[NonScheduledEpisode],
) -> None:
    tasks = []
    for source_name, source_episodes_iter in groupby(episodes, key=lambda x: x.source_name):
        if source_name not in new_episodes_source_names:
            logger.debug("Skipping %r because it has no new episodes", source_name)
            continue

        logger.info("Updating %r episodes in s3", source_name)
        source_episodes = list(source_episodes_iter)
        episode_ids = [x.chapter_id for x in source_episodes]
        tasks.append(s3_repo.update_episodes(source_name, episode_ids))

    await asyncio.gather(*tasks)


async def get_all_episodes(
    s3_repo: S3Repository, source_names: set[str]
) -> list[S3NonScheduledEpisode]:
    tasks_futures = [s3_repo.get_episodes(source_name=source_name) for source_name in source_names]
    episodes_nested = await asyncio.gather(*tasks_futures)
    return [item for sublist in episodes_nested for item in sublist]
