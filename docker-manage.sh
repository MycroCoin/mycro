#! /bin/bash
# wrapper to make callng manage.py helper functions within 
# mycro-backend docker context easier.
# example usage: "./docker-manage.sh makemigrations"

docker run -v `pwd`:`pwd` -w `pwd` -i -t mycro_server ./manage.py "$@"

