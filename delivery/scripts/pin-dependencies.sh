#!/usr/bin/env bash

function run() {
  cd /data

  echo "+Installing poetry"
  pip install poetry==1.4.0

  echo "+Installing dev requirements"
  poetry export -o requirements.txt

  echo "+Exporting dev requirements"
  poetry export --only dev -o requirements-dev.txt
  echo -e "\n\n# Mypy types\n" >> requirements-dev.txt
  poetry export --only types >> requirements-dev.txt
}

source $(dirname $0)/../base.inc
