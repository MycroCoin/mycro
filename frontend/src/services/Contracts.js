import TruffleContract from 'truffle-contract';
// Import contracts
import BaseDaoData from '../build/contracts/BaseDao.json';

let Contracts;

if (window.web3) {
  //TODO have backup providers here
  const provider = window.web3.currentProvider;
  const web3 = window.web3;

  Contracts = {
    BaseDao: TruffleContract(BaseDaoData)
  };

  //add providers
  Object.keys(Contracts).forEach(contractName => {
    const contract = Contracts[contractName];
    contract.setProvider(provider);
    contract.defaults({ from: web3.eth.accounts[0] });
  });
}

export { Contracts };
