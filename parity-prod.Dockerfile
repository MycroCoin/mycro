FROM parity/parity:v1.11.8

# NOTE: to be able to build this file you need to first sync locally with
# parity --chain ropsten --reserved-peers ropstenpeers.txt --light --base-path <path to mycro project>/parity-chain
# then you can build a container with this image
# build and push with (note that `v1` should be switched to a new version):
# gcloud auth print-access-token | docker login -u oauth2accesstoken --password-stdin https://gcr.io
# docker build -f parity-prod.Dockerfile -t gcr.io/mycrocoin/parity:v1 .
# docker push gcr.io/mycrocoin/parity:v1
COPY parity-chain .
COPY ropstenpeers.txt .

EXPOSE 8545
