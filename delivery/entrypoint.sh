#!/usr/bin/env bash

REQUIRED_VARS=(AWS_ACCESS_KEY_ID AWS_BUCKET_NAME AWS_REGION_NAME AWS_SECRET_ACCESS_KEY SOURCES TELEGRAM_CHAT_ID TELEGRAM_TOKEN TODOIST_API_KEY)

function init() {
  for requiredVar in "${REQUIRED_VARS[@]}"; do
    if [[ -z "${!requiredVar}" ]]; then
      echo "Missing required environment variable: $requiredVar"
      exit 1
    fi
  done
}

function run() {
  python /code/app/cli.py "$@"
}

init
run "$@"
