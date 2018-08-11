FROM parity/parity:v1.11.8

# NOTE: to be able to build this file you need to first sync locally with
# parity --light --chain ropsten --base-path ~/.local/share/io.parity.ethereum/docker --unsafe-expose
# then, run
# cp ~/.local/share/io.parity.ethereum/docker .
# then you can build a container with this image
# build and push with (note that `v1` should be switched to a new version):
# gcloud auth print-access-token | docker login -u oauth2accesstoken --password-stdin https://gcr.io
# docker build -f parity-prod.Dockerfile -t gcr.io/mycrocoin/parity:v1 .
# docker push gcr.io/mycrocoin/parity:v1
COPY docker .

EXPOSE 8545
