#!/usr/bin/env bash


function run() {
  docker-compose build app
  docker-compose run --rm -v $(pwd):/data --entrypoint bash app delivery/scripts/pin-dependencies.sh
}

source $(dirname $0)/../base.inc
