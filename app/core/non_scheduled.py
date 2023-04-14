import asyncio
from datetime import date
from itertools import groupby
from logging import getLogger

from app.models.episodes import NonScheduledEpisode, S3NonScheduledEpisode
from app.models.todoist import TaskCreate
from app.repositories.s3 import S3Repository
from app.repositories.telegram import TelegramRepository
from app.repositories.todoist import TodoistRepository

logger = getLogger(__name__)


async def process_non_scheduled_episodes(
    episodes: list[NonScheduledEpisode], assume_new: bool, dry_run: bool
) -> None:
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

        if not s3_episode or assume_new:
            task_content = f"[{task_title}]({episode.chapter_url})"
            task_create = TaskCreate(
                content=task_content,
                description="",
                project_id=episode.source.inputs.todoist_project_id,
                section_id=episode.source.inputs.todoist_section_id,
                due_date=today,
            )
            logger.info(
                "Creating task and notification for %r (forced=%r)",
                task_title,
                assume_new,
                extra={
                    "task_create": task_create.dict(),
                    "op": "create_task",
                    "type": "non_scheduled",
                },
            )
            new_episodes_source_names.add(episode.source_name)
            if not dry_run:
                await todoist_repo.create_task(task_create)
                if not assume_new:
                    await telegram_repo.send_message(f"New episode: {task_content}")

    if not new_episodes_source_names:
        logger.info("No new non scheduled episodes")
        return

    await update_s3_info(s3_repo, new_episodes_source_names, episodes, dry_run)


async def update_s3_info(
    s3_repo: S3Repository,
    new_episodes_source_names: set[str],
    episodes: list[NonScheduledEpisode],
    dry_run: bool,
) -> None:
    tasks = []
    for source_name, source_episodes_iter in groupby(episodes, key=lambda x: x.source_name):
        if source_name not in new_episodes_source_names:
            logger.debug(
                "Skipping %r AWS S3 file update because it has no new episodes", source_name
            )
            continue

        logger.info("Updating %r episodes in AWS S3", source_name)
        source_episodes = list(source_episodes_iter)
        episode_ids = [x.chapter_id for x in source_episodes]
        if not dry_run:
            tasks.append(s3_repo.update_episodes(source_name, episode_ids))

    if dry_run:
        return
    await asyncio.gather(*tasks)


async def get_all_episodes(
    s3_repo: S3Repository, source_names: set[str]
) -> list[S3NonScheduledEpisode]:
    tasks_futures = [s3_repo.get_episodes(source_name=source_name) for source_name in source_names]
    episodes_nested = await asyncio.gather(*tasks_futures)
    return [item for sublist in episodes_nested for item in sublist]
