# How to get this shit going in pycharm
Inspired by https://www.jetbrains.com/help/pycharm/using-docker-as-a-remote-interpreter.html
Below instructions are unnecessary if working purely in docker, which you should
1. install docker
1. `cd mycro`
2. run `docker build -t mycro-tests:latest -f backend/server.Dockerfile .`
3. Add a project interpreter in pycharm and set it up like so: https://imgur.com/a/QdGeoFK
4. Create a run configuration for the tests by right clicking the tests directory and hitting "run all tests"
5. Edit the run configuration and make sure that it uses the docker interpreter: https://imgur.com/a/dsZXXId

Ok, now whenever you run tests, you'll build the latest image and run them in the docker container, I think.

# Minikube
1. install minikube. This will be kinda painful becuase you have to get virtualbox or some other hypervisor
2. `minikube start`
3. `kubectl create secret generic eth-private-key --from-literal=value=<some eth private key>`
5. open `parity-dev.json` and add a value to `accounts` with the public address of the private key used in the previous step
3. `kubectl create secret generic github-token --from-literal=value=<your github access token>`
4. `eval $(minikube docker-env)`
5. `docker build -f server.Dockerfile -t mycro-backend .`
6. `docker build -f parity-dev.Dockerfile -t mycro-parity-dev .`
7. `docker build -f frontend.Dockerfile -t mycro-frontend `
4. `kubectl apply -f kubernetes-local.yaml`
5. run `minikube ip` and record the value
7. in your browser visit `<minikube ip>:30080`
6. open metamask and use a new endpoint of the form `http://<minikube ip>:30045`


# Django backend without docker
I'm not 100% sure how to get started. I followed http://docs.graphene-python.org/projects/django/en/latest/tutorial-plain/

I think the only commands you need to do are:

```python
$ ./manage.py migrate
$ ./manage.py loaddata projects
$ ./manage.py runserver
```

After the `runserver` command, you should be able to visit `localhost:8000/graphql` and follow instructions from above for listing and mutating


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
This is code debt due to the way truffle works. For now the front end of our app relies on the build and migrations directory in our in the backend directory.

Useful truffle commands:
```bash
truffle compile
truffle migrate
```

note that we don't use truffle test as truffle tests aren't stateless.

# Code coverage
To get code coverage results do the following:

```
$ cd mycro
$ coverage erase && coverage run --source='.' manage.py test backend.tests && coverage html && open backend/coverage/index.html
```
