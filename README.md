# Mycro: A Platform for Open-Source Consumer Application

## Dev Requirements
+ Docker
+ Docker Compose

+ app.mycrocoin.aq and api.mycrocoin.aq should point to localhost. This means adding the following lines to your hosts file (/etc/hosts on most linux distributions, /private/etc/hosts on mac)
```
127.0.0.1 api.mycrocoin.aq
127.0.0.1 app.mycrocoin.aq
```

## Running the Server
+ Mycro has a helper script in the root directory called mycro. 

Helper Script Commands:
```
# starts the server
./mycro.sh start

# runs tests
./mycro.sh test

# runs tests
./mycro.sh test


# restarts the server
./mycro.sh restart

# starts a log feed of the specified service
./mycro.sh logs frontend
./mycro.sh logs server
./mycro.sh logs worker
./mycro.sh logs <service>

# removes all stored docker images (deletes dev data)
./mycro.sh clean

# access to django's manage.py within the backend docker image.
./mycro.sh manage makemigrations
./mycro.sh manage test
./mycro.sh manage <any manage.py command>
```
