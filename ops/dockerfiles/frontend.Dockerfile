FROM node:8

WORKDIR mycro

RUN npm install -g truffle

# used for prod environment
RUN npm install -g serve

COPY frontend/package.json .
RUN npm install

COPY ./ops/wait_for_it.sh .

COPY frontend .
# TODO contracts should be taken out of the backend
COPY ./backend/contracts ./contracts
ENV TERM xterm

