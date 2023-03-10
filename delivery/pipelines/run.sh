#!/usr/bin/env bash

function run() {
  docker-compose run --rm app "$@"
}

run "$@"
