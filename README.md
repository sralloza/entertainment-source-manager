# Entertainment Source Manager

> A simple way to manage your entertainment sources

## Deployment

Docker images are published to [Docker Hub](https://hub.docker.com/r/sralloza/entertainment-source-manager).

### Where is data stored

- Scheduled episodes are "stored" in Todoist. Only episodes that are not released yet are tracked.
- Non scheduled episodes are stored in AWS S3. Each source has its own file (list of episode IDs) in the bucket.

### Other considerations

- When a new scheduled episode is released, a Todoist task is created for the day of the episode's release.
- When a new non scheduled episode is released, a Todoist task is created for the same day and a Telegram message is sent.

## Configuration

Configuration is done via environment variables

### Required variables

- **_AWS_ACCESS_KEY_ID_**: AWS access key ID.
- **_AWS_BUCKET_NAME_**: AWS bucket name to store the non scheduled episodes.
- **_AWS_REGION_NAME_**: AWS region name where the bucket is.
- **_AWS_SECRET_ACCESS_KEY_**: AWS secret access key.
- **_SOURCES_**: base64 encoded JSON string with the sources to get the episodes from.
- **_TODOIST_API_KEY_**: Todoist token.

### Optional variables

- **_TELEGRAM_CHAT_ID_**: Telegram chat ID to send the notifications to.
- **_TELEGRAM_TOKEN_**: Telegram bot token to send the notifications from.
- **_DISABLED_SOURCES_**: List of source names to disable. Example: `One Piece,The Blacklist`

Note: if only one of the two Telegram variables is set, the application will fail to start.

## Providers

### InManga

- Type: `non-scheduled`
- Inputs:
  - **source_name** (string): name of the source. Example: `One Piece`
  - **source_encoded_name** (string): encoded name of the source (used to build the URL). Example: `one-piece`
  - **todoist_project_id** (string): todoist project ID to add the new chapters to.
  - **todoist_section_id** (string, optional): todoist section ID to add the new chapters to.
  - **first_chapter_id** (UUID): UUID of the first chapter.

### SpyXFamily

- Type: `non-scheduled`
- Inputs:
  - **todoist_project_id** (string): todoist project ID to add the new chapters to.
  - **todoist_section_id** (string, optional): todoist section ID to add the new chapters to.

### TheTVDB

- Type: `scheduled`
- Inputs:
  - **source_name** (string): name of the source. Example: `One Piece`
  - **source_encoded_name** (string): encoded name of the source (used to build the URL). Example: `one-piece`
  - **todoist_project_id** (string): todoist project ID to add the new chapters to.
  - **todoist_section_id** (string, optional): todoist section ID to add the new chapters to.

## Configuration example

```text
SOURCES=WwogIHsKICAgICJwcm92aWRlciI6ICJUaGVUVkRCIiwKICAgICJpbnB1dHMiOiB7CiAgICAgICJzb3VyY2VfbmFtZSI6ICJ0aGV0dmRiLnNvdXJjZV9uYW1lIiwKICAgICAgInNvdXJjZV9lbmNvZGVkX25hbWUiOiAidGhldHZkYi5zb3VyY2VfZW5jb2RlZF9uYW1lIiwKICAgICAgInRvZG9pc3RfcHJvamVjdF9pZCI6ICJ0aGV0dmRiLnRvZG9pc3RfcHJvamVjdF9pZCIsCiAgICAgICJ0b2RvaXN0X3NlY3Rpb25faWQiOiAidGhldHZkYi50b2RvaXN0X3NlY3Rpb25faWQiCiAgICB9CiAgfSwKICB7CiAgICAicHJvdmlkZXIiOiAiSW5NYW5nYSIsCiAgICAiaW5wdXRzIjogewogICAgICAic291cmNlX25hbWUiOiAiaW5tYW5nYS5zb3VyY2VfbmFtZSIsCiAgICAgICJzb3VyY2VfZW5jb2RlZF9uYW1lIjogImlubWFuZ2Euc291cmNlX2VuY29kZWRfbmFtZSIsCiAgICAgICJ0b2RvaXN0X3Byb2plY3RfaWQiOiAiaW5tYW5nYS50b2RvaXN0X3Byb2plY3RfaWQiLAogICAgICAidG9kb2lzdF9zZWN0aW9uX2lkIjogImlubWFuZ2EudG9kb2lzdF9zZWN0aW9uX2lkIiwKICAgICAgImZpcnN0X2NoYXB0ZXJfaWQiOiAiNjE4ZTVjY2QtMGU0NC00ZjZjLWIyMTQtMzE1MDU5MThhZjY3IgogICAgfQogIH0sCiAgewogICAgInByb3ZpZGVyIjogIlNweVhGYW1pbHkiLAogICAgImlucHV0cyI6IHsKICAgICAgInRvZG9pc3RfcHJvamVjdF9pZCI6ICJzcHl4ZmFtaWx5LnRvZG9pc3RfcHJvamVjdFx9pZCIsCiAgICAgICJ0b2RvaXN0X3NlY3Rpb25faWQiOiAic3B5eGZhbWlseS50b2RvaXN0X3NlY3Rpb25faWQiCiAgICB9CiAgfQpd
```

Decoded, the previous JSON string looks like this:

```json
[
  {
    "provider": "TheTVDB",
    "inputs": {
      "source_name": "thetvdb.source_name",
      "source_encoded_name": "thetvdb.source_encoded_name",
      "todoist_project_id": "thetvdb.todoist_project_id",
      "todoist_section_id": "thetvdb.todoist_section_id"
    }
  },
  {
    "provider": "InManga",
    "inputs": {
      "source_name": "inmanga.source_name",
      "source_encoded_name": "inmanga.source_encoded_name",
      "todoist_project_id": "inmanga.todoist_project_id",
      "todoist_section_id": "inmanga.todoist_section_id",
      "first_chapter_id": "618e5ccd-0e44-4f6c-b214-31505918af67"
    }
  },
  {
    "provider": "SpyXFamily",
    "inputs": {
      "todoist_project_id": "spyxfamily.todoist_project_id",
      "todoist_section_id": "spyxfamily.todoist_section_id"
    }
  }
]
```
