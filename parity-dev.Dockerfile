FROM parity/parity:v1.11.7

COPY parity-dev.json .

ENTRYPOINT ["/parity/parity", "--chain", "parity-dev.json", "--unsafe-expose", "--jsonrpc-cors", "all"]
