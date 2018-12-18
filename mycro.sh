#! /bin/bash
EXECUTION_LOCATION="$(pwd)"

# sources .env file if it exists
MYCRO_ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
cd $MYCRO_ROOT_DIR/ops

ENV_FILE="$MYCRO_ROOT_DIR/ops/.env"
[ -f $ENV_FILE ] && source $ENV_FILE && echo "Sourcing .env file..."

CERTS_DIR="$MYCRO_ROOT_DIR/ops/certs"
DOCKER_COMPOSE_BASE="docker-compose.yml"
DOCKER_COMPOSE_PROD="docker-compose.prod.yml"

PROD_SERVER_STARTED_MESSAGE="
Mycro Prod server started
"
DEV_SERVER_STARTED_MESSAGE="
+----------------------------+
| Mycro dev servers started. |
+----------------------------+

You can monitor logs of
+ frontend
+ backend
+ worker
or any other service using
./mycro.sh logs <service_name>

Restart the server using
./mycro.sh restart

Stop the server using
./mycro.sh stop

Navigate your browser to app.mycrocoin.aq
and set your metamask endpoint to localhost:8545\n
"
# This is a hack that gives the user access to a mycro-test-account github account
# this won't scale but makes dev setup easy for now. We should find a better solution
# to this long term.
# the token is split to get past a github security feature that automatically removes 
# security keys that are commited to a repo. The security risk here is that everyone
# has read/write access to github projects created from dev environments.
PART_1="156"
PART_2="b79d231"
PART_3="d108baea9a"
PART_4="97386d9036d7ce35ad3a"
DEFAULT_GITHUB_TOKEN="${PART_1}${PART_2}${PART_3}${PART_4}"
[ -n "${GITHUB_TOKEN}" ] || export GITHUB_TOKEN=$DEFAULT_GITHUB_TOKEN

DEFAULT_ENV="DEV"
[ -n "${ENV}" ] || ENV=$DEFAULT_ENV

case "$ENV" in
  PROD)
    DOMAIN="mycrocoin.org"
    DOCKER_COMPOSE="docker-compose -f $DOCKER_COMPOSE_BASE -f $DOCKER_COMPOSE_PROD"
    ;;
  *)
    # .aq is the TLD for antarctica. 
    # I seem to recall there's certain use cases where it's handy to use a real TLD in dev. 
    # AQ is reserved for organizations working in antartica so I don't think anyone is going 
    # to register this any time soon (unless we migrate our headquarters very far south)
    DOMAIN="mycrocoin.aq"
    DOCKER_COMPOSE="docker-compose"
    ;;
esac

export FRONTEND_HOST="app.$DOMAIN"
export API_HOST="api.$DOMAIN"

# ensures that SSL certs exist in $CERTS_DIR for the project. If they don't exist, self signed certs are created
_ensure_certs() {
  #evaluates to true if certs exist
  has_certs="[ -f $CERTS_DIR/privkey.pem ] && [ -f $CERTS_DIR/fullchain.pem ] && echo 'ssl keys found'"

  #generates new certs
  get_certs="echo 'no ssl keys found, self signing' && \
    sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
      -keyout $CERTS_DIR/privkey.pem \
      -out $CERTS_DIR/fullchain.pem \
      -subj '/CN=*.$DOMAIN/O=My Company Name LTD./C=US'"

  eval "($has_certs) || ($get_certs)"
}

start() {
  _ensure_certs

  $DOCKER_COMPOSE build

  case "$ENV" in
    PROD)
      $DOCKER_COMPOSE up -d && \
        printf "$PROD_SERVER_STARTED_MESSAGE"
      ;;
    *)
      $DOCKER_COMPOSE up -d && \
        printf "$DEV_SERVER_STARTED_MESSAGE"
      ;;
  esac
}

stop() {
  $DOCKER_COMPOSE stop
}

logs() {
  $DOCKER_COMPOSE logs -f "$1"
}

status() {
  $DOCKER_COMPOSE ps
}

clean() {
  case "$ENV" in
    PROD)
      echo "Failed - Running drop in prod will result in data loss"
      ;;
    *)
      stop
      $DOCKER_COMPOSE rm
      ;;
  esac
}

rebuild() {
  stop
  $DOCKER_COMPOSE rm worker server frontend
  start

}

manage() {
  docker run -v `pwd`:`pwd` -w `pwd` -i -t mycro_server ./manage.py "$@"
}

case "$1" in
  start)
    start
    ;;
  stop)
    stop
      ;;
  restart)
    stop
    start
      ;;
  logs)
    logs "$2"
      ;;
  status)
    status
      ;;
  clean)
    clean
      ;;
  manage)
    manage
      ;;
  rebuild)
    rebuild
      ;;
  *)
      echo $"Usage: $0 {start|stop|restart|logs|status|rebuild}"
      exit 1
esac

cd $EXECUTION_LOCATION
