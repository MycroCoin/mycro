import TruffleContract from 'truffle-contract';
import TruffleDeployer from 'truffle-deployer';
// Import contracts
import MycroCoinData from './build/contracts/MycroCoin.json';
import BaseDaoData from './build/contracts/BaseDao.json';
import MergeAscData from './build/contracts/MergeASC.json';
import MergeModuleData from './build/contracts/MergeModule.json';

//TODO have backup providers here
const provider = window.web3.currentProvider;
const web3 = window.web3;

const createTruffleContract = (data) => {
  const contract = TruffleContract(data);
  contract.setProvider(provider);
  contract.defaults({from: web3.eth.defaultAccount});
  return contract;
};

const deployHelper = (contract, ...args) => {
    //TODO use a promise here to avoid race condition
    return deployer.deploy(contract, ...args);
};

var deployer = null;
web3.version.getNetwork(function(err, id) {
      const network_id = id;

      deployer = new TruffleDeployer({
        contracts: [BaseDaoData],
        network: "test",
        network_id: network_id,
        provider: provider
      });
      
      deployer.start();
});
const Contracts = {
  MycroCoin: TruffleContract(MycroCoinData),
  BaseDao: TruffleContract(BaseDaoData),
  MergeAsc: TruffleContract(MergeAscData),
  MergeModule: TruffleContract(MergeModuleData),
};

//add providers
Object.keys(Contracts).forEach((contract) => {
  Contracts[contract] = createTruffleContract(Contracts[contract]);
});

const deployedMycro = () => {
  //TODO don't hardcode and actually grab it with graphql dynamically
  return Contracts.MycroCoin.at("0x4c6ffC6EA586fCab485C08724d3a911C390D199c");
}
// TODO uncomment this once shit is fixed
// Contracts.MycroCoin.deployed = deployedMycro;


export {
  Contracts,
  deployHelper,
  createTruffleContract,
};

