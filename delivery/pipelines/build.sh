#!/usr/bin/env bash


function run() {
  echo "+Ensuring .env file exists"
  ensureEnvFileExists

  echo "+Building app"
  docker-compose build app

  echo "+Ensuring dependencies are pinned"
  ensureLatestDependencies

  echo "+Running test script"
  docker-compose run --rm -v $(pwd):/data --entrypoint bash app delivery/scripts/test.sh
}

function ensureLatestDependencies() {
  $(dirname $0)/pin-dependencies.sh
  deps_changed=$(git diff --name-only | grep -E 'requirements(.*)?.txt') || true
  if [[ "$deps_changed" ]]; then
    fatal "Dependencies are not pinned. Please run delivery/scripts/pin-dependencies.sh"
  fi
}

function ensureEnvFileExists() {
  envPath=$(dirname $0)/../../.env
  if [[ ! -f $envPath ]]; then
    echo "+Creating an empty .env file"
    touch $envPath
    echo "AWS_ACCESS_KEY_ID=aws-access-key-id" >> $envPath
    echo "AWS_BUCKET_NAME=aws-bucket-name" >> $envPath
    echo "AWS_REGION_NAME=aws-region-name" >> $envPath
    echo "AWS_SECRET_ACCESS_KEY=aws-secret-access-key" >> $envPath
    echo "TELEGRAM_TOKEN=telegram-token-test" >> $envPath
    echo "TELEGRAM_CHAT_ID=telegram-chat-id" >> $envPath
    echo "TODOIST_API_KEY=todoist-api-key-test" >> $envPath
  fi
}
source $(dirname $0)/../base.inc
