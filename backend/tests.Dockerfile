FROM mycro/solc-python:latest

WORKDIR mycro

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY contracts/ contracts
COPY tests/ tests

CMD ["python3", "-m", "unittest", "discover", "-v", "-s", "tests"]
