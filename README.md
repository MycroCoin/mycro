Mycro: A Platform for Open-Source Consumer Application

#Dev Requirements
+ Docker
+ Docker Compose
+ Metamask

#Running the Server
+ Mycro has a helper script in the root directory called mycro. 

Helper Script Commands:
```
# starts the server
./mycro.sh start

# stops the server
./mycro.sh stop

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
