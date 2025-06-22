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

start() {
  # start the app and db
  # default: start with docker compose
  # add --native to start db in docker and app natively

  load_env

  if [ "$1" == "--native" ]; then
    run_postgres

    echo "sleeping 5 seconds for DB to start up..."
    sleep 5
    
    if [[ "$(which python)" == "$PWD/.venv/bin/python" ]]; then
      echo "Project virtualenv '.venv' appears to be active."
    else
      echo "Project virtualenv '.venv' does not appear to be active."
      echo "Attempting to source it."
      source .venv/bin/activate 
    fi
    if [ -z "$DATABASE_URL" ]; then
      echo "switching DB_HOST to 127.0.0.1"
      DB_HOST="127.0.0.1"
      export DB_HOST
    else 
      echo "switching DATABASE_URL from docker network name to localhost"
      DATABASE_URL=$(echo "$DATABASE_URL" | sed 's/@db:/@127.0.0.1:/g')
      export DATABASE_URL
    fi
    echo "starting api natively..."
    python app/main.py
  else
    echo "starting docker compose in detach mode..."
    docker compose up --build -d
  fi
}

redeploy() {
  # docker commands: deploy / re-deploy api container

  echo "legacy script since the app now requires db to be active as well, exiting..."
  exit 1
  
  API_IMAGE_NAME="type-friend:latest"
  API_CONTAINER_NAME="type-friend-container"
  API_MAPPED_PORT=8000
  load_env
  
  docker build -t "$API_IMAGE_NAME" .
  docker stop "$API_CONTAINER_NAME" && docker rm "$API_CONTAINER_NAME" || true
  docker run -d --name "$API_CONTAINER_NAME" -p "$API_MAPPED_PORT":8000 "$API_IMAGE_NAME"
  echo "Deploy complete. Container '$API_CONTAINER_NAME' running on port: $API_MAPPED_PORT"
}

run_postgres() {
  # run only the db container
  DB_CONTAINER_NAME="tf-db"
  load_env

  docker compose up db -d  
  echo "postgres container '$DB_CONTAINER_NAME' now running"

}

conn_sql() {
  # connect to db 
  
  DB_CONTAINER_NAME="tf-db"
  DB_NAME="postgres"
  load_env

  docker exec -it $DB_CONTAINER_NAME psql -U postgres -d $DB_NAME
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

  # TODO - add check for certs in /etc/letsencrypt (but need sudo)

  help="
## conf-file output: ${API_DOMAIN}.conf
=====
## now run 'sudo ./devscripts.sh init_certbot' to add certs. and finally...
=====
## cp to nginx sites-available and sym link to sites-enabled:
sudo cp ./$API_DOMAIN.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/$API_DOMAIN.conf /etc/nginx/sites-enabled/$API_DOMAIN.conf
sudo nginx -t
sudo systemctl reload nginx
"
  echo "$help"
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
  start                   start the app via docker-compose
    --native              start the db in docker, app runs natively
  run_postgres            run a postgres container (to connect natively running app)
  conn_sql                open psql shell connected to db container
  make_nginx              fill env vars to nginx_example.conf.template
  init_certbot            get certs via certbot for API_DOMAIN
  redeploy                (deprecated) build and run api container
  
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
start|redeploy|run_postgres|conn_sql|make_nginx|init_certbot)
  func=$1
  shift
  "$func" "$@"
  exit 0
  ;;
*)
  echo "Error: command '$1' not found." >&2
  exit 1
esac


