import {Contracts} from '../Contracts.js';

const getProjectForAddress = (address) => {
  return Contracts.BaseDao.at(address);
};

const ascAddressToJson = (address) => {
  return {id: address, name: "no name"};
};

const projectContractToProjectJson = (contract) => {
  return new Promise( (resolve) => {
    Promise.all([
      contract.name(),
      contract.get_proposals()
    ]).then( ([name, ascAddresses]) => {
      const id = contract.address;
      const githubUrl = "";
      const ascs = ascAddresses.map(ascAddressToJson);
      resolve({name, ascs, id, githubUrl});
    });
  });
}

export {
  getProjectForAddress,
  projectContractToProjectJson
}

