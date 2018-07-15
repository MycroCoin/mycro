FROM node:8

WORKDIR mycro

RUN npm install -g truffle

COPY frontend/package.json .
RUN npm install

COPY wait_for_it.sh .

COPY frontend .
# TODO contracts should be taken out of the backend
COPY ./backend/contracts ./contracts
RUN ln -s /mycro/build /mycro/src/build
ENV TERM xterm

