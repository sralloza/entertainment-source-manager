# CHANGELOG

## [Unreleased]

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
