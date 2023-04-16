# CHANGELOG

## [1.2.0] - 2023-04-16

### Added

- feat: add log to warn when a `TheTVDB` source is marked as `Ended`

### Changed

- chore: improve json logs using python-json-logger library

### Fixed

- fix: update `spyxfamily` provider to use the new website
- fix: escape special telegram characters for markdown v2
- fix: ignore 404 S3 errors when reading unscheduled source lists

## [1.1.0] - 2023-03-11

### Added

- feat: send telegram notification when a new non scheduled episode is found
- feat: skip some sources using the environment variable `DISABLED_SOURCES` (`DISABLED_SOURCES=source1,source2`)
- feat: add command `update-single-source` to update a single source assuming all the episodes are new
- feat: add command `print` to print the sources definitions and source names
- feat: add `--dry-run` flag to simulate the update process

### Fixed

- fix: do not stop execution when a provider fails to fetch its episodes

## [1.0.0] - 2023-03-05

### Added

- feat: add support for `inmanga` and `spyxfamily` non scheduled providers
- feat: add support for `thetvdb` scheduled provider
