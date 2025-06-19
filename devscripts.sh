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
  API_HOST="127.0.0.1"
  API_MAPPED_PORT="8000"
  API_DOMAIN="FAKEDOMAIN.com"
  load_env
  
  if [ ! -f $NGINX_TEMPLATE_FN ]; then
    echo "template file '$NGINX_TEMPLATE_FN' not found"
    exit 1
  fi

  if [ ! -x "$(command -v envsubst)" ]; then
    echo "'envsubst' not installed"
    exit 1
  fi

  envsubst \
    '${API_DOMAIN} ${API_HOST} ${API_MAPPED_PORT}' \
    < $NGINX_TEMPLATE_FN \
    > "./$API_DOMAIN.conf"

  echo "## conf-file output: ${API_DOMAIN}.conf"
  echo "====="
  echo "## cp to nginx sites-available and sym link to sites-enabled:"
  echo "sudo cp ./$API_DOMAIN.conf /etc/nginx/sites-available/"
  echo "sudo ln -s /etc/nginx/sites-available/$API_DOMAIN.conf /etc/nginx/sites-enabled/$API_DOMAIN.conf"
  echo "sudo nginx -t"
  echo "sudo systemctl reload nginx"
  echo "## then run './devscripts.sh init_cerbot' to add certs"
}

init_certbot() {
  # add certs for a domain via certbot --webroot mode

  load_env
  
  if [ ! -x "$(command -v certbot)" ]; then
    echo "'certbot' not installed" >&2
    exit 1
  fi

  if [ "$(id -u)" -ne 0 ]; then
    echo "Error: This script must be run as root or with sudo for certbot." >&2
    exit 1
  fi
  
  if [ -z "$API_DOMAIN" ]; then
    echo "Error: API_DOMAIN environment variable is not set. Please set it in your .env file." >&2
    exit 1
  fi

  echo "Attempting to add cert for domain: $API_DOMAIN via command"
  echo "certbot certonly --webroot -w /var/www/html -d $API_DOMAIN"
  
  certbot certonly --webroot -w /var/www/html -d $API_DOMAIN

  echo "script complete."
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
  init_certbot            get certs via certbot for API_DOMAIN
  
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
redeploy|make_nginx|init_certbot)
  func=$1
  shift
  "$func" "$@"
  exit 0
  ;;
*)
  echo "Error: command '$1' not found." >&2
  exit 1
esac


