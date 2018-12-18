FROM node:8

WORKDIR mycro

# serve is used to in prod for serving built web app
RUN npm install -g truffle serve

COPY frontend/package.json .
RUN npm install

COPY ./ops/wait_for_it.sh .

COPY frontend .
# TODO contracts should be taken out of the backend
COPY ./backend/contracts ./contracts
ENV TERM xterm

