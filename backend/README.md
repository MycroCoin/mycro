# How to get this shit going in pycharm
Inspired by https://www.jetbrains.com/help/pycharm/using-docker-as-a-remote-interpreter.html
Below instructions are unnecessary if working purely in docker, which you should
1. install docker
1. cd mycro/backend
2. run `docker build -t mycro-tests:latest -f tests.Dockerfile .`
3. Add a project interpreter in pycharm and set it up like so: https://imgur.com/a/QdGeoFK
4. Create a run configuration for the tests by right clicking the tests directory and hitting "run all tests"
5. Edit the run configuration and make sure that it uses the docker interpreter: https://imgur.com/a/dsZXXId

Ok, now whenever you run tests, you'll build the latest image and run them in the docker container, I think.

# Docker Compose Watch tests

cd mycro/backend
docker build -t mycro-tests:latest -f tests.Dockerfile .
docker-compose run tests

# Installation instructions OSX
```bash
python3 -m virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
brew update
brew upgrade
brew tap ethereum/ethereum
brew install solidity
brew linkapps solidity
brew install pkg-config
```
# Installation instructions for Ubuntu 16
```bash
python3 -m virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
sudo add-apt-repository ppa:ethereum/ethereum
sudo apt-get update
sudo apt-get install solc
```

# Confirming your installation works
Try running a test
`python tests/test_mycro_contract.py`

# App Frontend
This is code debt for now the front end of our app lives in the backend directory.

Useful truffle commands:
```bash
truffle compile
truffle migrate
```

note that we don't use truffle test as truffle tests aren't stateless.
