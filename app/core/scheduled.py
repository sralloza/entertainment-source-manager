import asyncio
from datetime import date

from app.logs import get_logger
from app.models.episodes import ScheduledEpisode
from app.models.todoist import Task, TaskCreate, TaskUpdate
from app.repositories.todoist import TodoistRepository

logger = get_logger(__name__)


async def process_scheduled_episodes(episodes: list[ScheduledEpisode], assume_new: bool) -> None:
    # We only care about episodes that will be released in the future (excluding today)
    today = date.today()
    if assume_new:
        episodes = [x for x in episodes if x.released_date]
    else:
        episodes = [x for x in episodes if x.released_date and x.released_date > today]

    project_ids = set(x.source.inputs.todoist_project_id for x in episodes)

    todoist_repo = TodoistRepository()
    tasks = await get_tasks_from_project_ids(todoist_repo, project_ids)
    task_map = {x.content: x for x in tasks}

    for episode in episodes:
        task_content = f"{episode.source_name} {episode.chapter_id}"
        task = task_map.get(task_content)
        task_description = f"Released: {episode.released_date} on {episode.platform}"

        if not task:
            logger.info("Creating task for %r", task_content)
            task_create = TaskCreate(
                content=task_content,
                description=task_description,
                project_id=episode.source.inputs.todoist_project_id,
                section_id=episode.source.inputs.todoist_section_id,
                due_date=episode.released_date,
            )
            await todoist_repo.create_task(task_create)
            continue

        task_update = TaskUpdate()
        if task.description != task_description:
            task_update.description = task_description

        if not task.due_date or task.due_date != episode.released_date:
            task_update.due_date = episode.released_date

        if task.section_id != episode.source.inputs.todoist_section_id:
            task_update.section_id = episode.source.inputs.todoist_section_id

        if task_update:
            params = task_update.dict(exclude_unset=True)
            logger.info("Updating task for %r with params %r", task_content, params)
            await todoist_repo.update_task(task.id, task_update)


async def get_tasks_from_project_ids(todoist_repo: TodoistRepository, ids: set[str]) -> list[Task]:
    tasks_futures = [todoist_repo.list_tasks(project_id=project_id) for project_id in ids]
    tasks_nested = await asyncio.gather(*tasks_futures)
    return [item for sublist in tasks_nested for item in sublist]
