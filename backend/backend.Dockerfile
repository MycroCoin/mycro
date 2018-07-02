FROM mycro/solc-python:latest

WORKDIR mycro

# copy the requirements first so that changing a file doesn't mean we have to reinstall with pip
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# needed for django
RUN ln -s $(which python3) /usr/bin/python

COPY backend backend/
COPY manage.py .
RUN ./manage.py migrate
ENV TERM xterm

# This is how tests are run in the django world
CMD ["./manage.py", "test"]
