FROM mycro/solc-python:latest

#setup uwsgi used in prod environments
RUN apt-get update
RUN pip3 install --upgrade pip
RUN pip3 uninstall uwsgi
RUN apt-get -y install build-essential python-dev
RUN pip3 install uwsgi
ENV UWSGI_WSGI_FILE=backend/wsgi.py UWSGI_HTTP=:8000 UWSGI_MASTER=1 UWSGI_WORKERS=2 UWSGI_THREADS=8 UWSGI_UID=1000 UWSGI_GID=2000 UWSGI_LAZY_APPS=1 UWSGI_WSGI_ENV_BEHAVIOR=holy

WORKDIR mycro

# copy the requirements first so that changing a file doesn't mean we have to reinstall with pip
COPY backend/requirements.txt .
RUN pip3 install -r requirements.txt

# needed for django
RUN ln -sf $(which python3) /usr/bin/python

COPY backend backend/
COPY manage.py .
COPY ./ops/wait_for_it.sh .
ENV TERM xterm

