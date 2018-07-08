import {Contracts} from '../Contracts.js';

const getProjectForAddress = (address) => {
  return Contracts.BaseDao.at(address);
};

const ascAddressToJson = (address) => {
  return new Promise(resolve => {
    resolve({id: address, name: "no name"});
  });
};

const projectContractToProjectJson = (contract) => {
  const projectJson = {};
  projectJson.id = contract.address;
  projectJson.githubUrl = "";

  return Promise.all([
    contract.name(),
    contract.get_proposals()
  ]).then( ([name, ascAddresses]) => {
    projectJson.name = name;
    return Promise.all(ascAddresses.map(ascAddressToJson))
  }).then((ascs) => {
    projectJson.ascs = ascs;
    return projectJson;
  });
}

export {
  getProjectForAddress,
  projectContractToProjectJson,
  ascAddressToJson
}

