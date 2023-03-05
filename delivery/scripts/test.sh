#!/usr/bin/env bash

COVERAGE_TARGET="100"

function run() {
  cd /data

  echo "+Installing dev requirements"
  pip install -r requirements-dev.txt

  echo "+Running linters"
  lint

  echo "+Running tests"
  test
}

function lint() {
  echo "+Running ruff linter"
  ruff check app
  ruff check test

  echo "+Running black linter"
  black --check app
  black --check test

  echo "+Running mypy linter"
  mypy --strict --check-untyped-defs app
  mypy --check-untyped-defs test
}

function test() {
  echo "Cleaning test cache"
  find test -name '__pycache__' | tee cache.log | xargs -n1 rm -rf
  cat cache.log | xargs -n1 echo "++Removed"
  rm cache.log

  echo "+Running tests"
  pytest --cov-branch --cov-report html --cov-report term --cov=app -vv | tee coverage.log

  cov_score=$(awk '$1 == "TOTAL" {print $NF+0}' coverage.log)
  if (( $cov_score < $COVERAGE_TARGET )); then
    fatal "Coverage score is too low: $cov_score (target: $COVERAGE_TARGET)"
  fi
}

source $(dirname $0)/../base.inc
