#! /bin/bash
docker build -f server.Dockerfile -t mycro-backend .
docker build -f frontend.Dockerfile -t mycro-frontend .
docker build -f parity-dev.Dockerfile -t mycro-parity-dev .
