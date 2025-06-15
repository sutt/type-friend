#!/bin/bash

set -e
set -a

load_env() {
  # load env file; override default args in this script
  if [ -f .env ]; then
    . ./.env
  else
      echo "WARNING: could not find .env file. Running with all default args"
  fi
}

redeploy() {
  # docker commands: deploy / re-deploy api container
  
  API_IMAGE_NAME="type-friend:latest"
  API_CONTAINER_NAME="type-friend-container"
  API_MAPPED_PORT=8000
  load_env
  
  docker build -t "$API_IMAGE_NAME" .
  docker stop "$API_CONTAINER_NAME" && docker rm "$API_CONTAINER_NAME" || true
  docker run -d --name "$API_CONTAINER_NAME" -p "$API_MAPPED_PORT":8000 "$API_IMAGE_NAME"
  echo "Deploy complete. Container '$API_CONTAINER_NAME' running on port: $API_MAPPED_PORT"
}

make_nginx() {
  # fill in env vars to the nginx template

  NGINX_TEMPLATE_FN="nginx_example.template.conf"
  NGINX_OUTPUT_FN="nginx_example.conf"
  API_HOST="127.0.0.1"
  API_MAPPED_PORT="8000"
  load_env
  
  if [ ! -f $NGINX_TEMPLATE_FN ]; then
    echo "template file '$NGINX_TEMPLATE_FN' not found"
    exit 1
  fi

  if [ ! -x "$(command -v envsubst)" ]; then
    echo "'envsubst' not installed"
    exit 1
  fi

  envsubst < $NGINX_TEMPLATE_FN > ./$NGINX_OUTPUT_FN

  echo "conf output: $NGINX_OUTPUT_FN"

}

devscripts_help() {
  # script cli help

  help="
USAGE
  $ ./devscripts.sh [COMMAND]

COMMANDS
  help                    show help
  redeploy                build and run api container
  make_nginx              fill env vars to nginx_example.conf.template

"
  echo "$help"
}

# main: run sub-command ===========
# echo "@: $@"

if [ -z "$1" ]; then
  devscripts_help
  exit 0
fi
case $1 in help)
  devscripts_help
  exit 0
  ;;
esac
case $1 in
redeploy|make_nginx)
  func=$1
  shift
  "$func" "$@"
  exit 0
  ;;
*)
  echo "command '$1' not found."
  exit 1
esac


