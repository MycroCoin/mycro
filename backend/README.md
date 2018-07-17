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

# Docker Compose Watch tests
```
cd mycro
docker build -t mycro-tests:latest -f backend/tests.Dockerfile .
docker-compose -f backend/docker-compose.yml run tests
```

# Docker compose run django server
```
$ cd mycro
$ docker-compose -f backend/docker-compose.yml build
$ docker-compose -f backend/docker-compose.yml down && docker-compose -f backend/docker-compose.yml up
```

Then visit `localhost:8001/graphql`. It should work. Run


```
query {
  allProjects {
    name,
    id
  }
}
```

You should see

```
{
  "data": {
    "allProjects": []
  }
}
```

Create a project with:

```
mutation create {
  createProject(repoName: "lol", daoAddress: "wtf") {
    newProject {
      repoName
      id
      daoAddress
    }
  }
}
```

You should see:

```
{
  "data": {
    "createProject": {
      "newProject": {
        "repoName": "lol",
        "id": "1",
        "daoAddress": "wtf"
      }
    }
  }
}
```

Now, query all projects like before:

```
query {
  allProjects {
    repoName
  }
}
```

and you should see

```
{
  "data": {
    "allProjects": [
      {
        "repoName": "lol"
      }
    ]
  }
}
```

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
