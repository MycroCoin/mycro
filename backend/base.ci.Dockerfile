FROM ubuntu:16.04

RUN apt-get update     \
&& apt-get install -yyq --no-install-recommends     \
automake     \
build-essential     \
pkg-config     \
libtool     \
libffi-dev     \
libssl-dev     \
libgmp-dev     \
software-properties-common     \
&& add-apt-repository ppa:ethereum/ethereum     \
&& apt-get update     \
&& apt-get install -yyq --no-install-recommends solc     \
&& add-apt-repository ppa:deadsnakes/ppa \
&& apt update     \
&& apt install -yyq --no-install-recommends     \
python3.6     \
python3.6-dev     \
wget     \
&& wget https://bootstrap.pypa.io/get-pip.py     \
&& python3.6 get-pip.py     \
&& ln -s /usr/bin/python3.6 /usr/local/bin/python3     \
&& ln -s /usr/local/bin/python3 /usr/bin/python     \
&& rm -rf /var/lib/apt/lists/*