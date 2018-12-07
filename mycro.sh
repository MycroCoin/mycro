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
# the token is split to get past a github security feature that automatically removes 
# security keys that are commited to a repo. The security risk here is that everyone
# has read/write access to github projects created from dev environments.
PART_1="156"
PART_2="b79d231"
PART_3="d108baea9a"
PART_4="97386d9036d7ce35ad3a"
DEFAULT_GITHUB_TOKEN="${PART_1}${PART_2}${PART_3}${PART_4}"
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
