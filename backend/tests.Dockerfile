FROM mycro/solc-python:latest

WORKDIR mycro

# copy the requirements first so that changing a file doesn't mean we have to reinstall with pip
COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY . backend
ENV TERM xterm

CMD ["python3", "-m", "unittest", "discover", "-v", "-s", "backend/tests"]
