FROM mycro/solc-python:latest

WORKDIR mycro

# copy the requirements first so that changing a file doesn't mean we have to reinstall with pip
COPY backend/requirements.txt .
RUN pip3 install -r requirements.txt

# needed for django
RUN ln -s $(which python3) /usr/bin/python

COPY backend backend/
COPY manage.py .
COPY wait_for_it.sh .
ENV TERM xterm

