FROM ubuntu:18.04

RUN apt-get update     \
&& apt-get install -yyq --no-install-recommends     \
automake     \
build-essential     \
libffi-dev     \
libgmp-dev     \
libsecp256k1-dev \
libssl-dev     \
libtool     \
pkg-config     \
python3-dev \
python3-pip \
software-properties-common     \
&& add-apt-repository ppa:ethereum/ethereum     \
&& apt-get update     \
&& apt-get install -yyq solc \
&& rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade pip setuptools