#! /bin/bash
SERVER_STARTED_MESSAGE="
+------------------------+
| Mycro servers started. |
+------------------------+

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

Navigate your browser to localhost:3000 
and set your metamask endpoint to localhost:8545\n
"
# This is a hack that gives the user access to a mycro-test-account github account
# this won't scale but makes dev setup easy for now. We should find a better solution
# to this long term.
DEFAULT_GITHUB_TOKEN="3c69ed70dc96fa80a65494e139986b93499581f7"
[ -n "${GITHUB_TOKEN}" ] || export GITHUB_TOKEN=$DEFAULT_GITHUB_TOKEN

start() {
  docker-compose build
  docker-compose up -d && printf "$SERVER_STARTED_MESSAGE"
}

stop() {
  docker-compose stop
}

logs() {
  docker-compose logs -f "$1"
}

status() {
  docker-compose ps
}

clean() {
  stop
  docker-compose rm
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
  *)
      echo $"Usage: $0 {start|stop|restart|logs|status}"
      exit 1
esac
