#!/usr/bin/env bash

ARG_DEFS=(
  "--repo=(.+)"
  "--tag=(.+)"
)

function init() {
  : ${DOCKERHUB_USERNAME?"DOCKERHUB_USERNAME env variable is required"}
  : ${DOCKERHUB_TOKEN?"DOCKERHUB_TOKEN env variable is required"}
}

function run() {
  echo "+Logging in to dockerhub API"
  response=$(curl -sX POST -H 'Content-Type: application/json' --data \
  '{"password":"'$DOCKERHUB_TOKEN'","username":"'$DOCKERHUB_USERNAME'"}' \
  https://hub.docker.com/v2/users/login --fail-with-body)
  token=$(echo $response | jq -r .token)

  echo "+Deleting image $REPO/$TAG"
  curl -sX DELETE -H "Authorization: Bearer $token" "https://hub.docker.com/v2/repositories/$REPO/tags/$TAG"
}

source $(dirname $0)/../base.inc
