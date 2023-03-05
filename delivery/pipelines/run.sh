#!/usr/bin/env bash

function run() {
  docker-compose run --rm app $*
}

source "$(dirname "$0")/../base.inc"
