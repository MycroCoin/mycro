# Installation instructions OSX
```bash
python3 -m virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
brew update
brew upgrade
brew tap ethereum/ethereum
brew install solidity
brew linkapps solidity
brew install pkg-config


```
# Installation instructions for Ubuntu 16
```bash
python3 -m virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
sudo add-apt-repository ppa:ethereum/ethereum
sudo apt-get update
sudo apt-get install solc
```

# Confirming your installation works
Try running a test
`python tests/test_mycro_contract.py`
