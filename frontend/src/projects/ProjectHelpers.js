import {Contracts} from '../Contracts.js';

const getProjectForAddress = (address) => {
  return Contracts.BaseDao.at(address);
};

const getMergeASCForAddress = (address) => {
  return Contracts.MergeAsc.at(address);
};

const ascContractToASCJson = (contract) => {
  const ascJson = {}
  ascJson.id = contract.address;

  return Promise.all([
      contract.prId()
  ]).then((prId) => {

        ascJson.prId = prId;
      return ascJson
    })
}

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
    return Promise.all(ascAddresses.map(getMergeASCForAddress))
  }).then((asc_contracts) => {
    return Promise.all(asc_contracts.map(ascContractToASCJson))
  }).then((ascs) => {
    projectJson.ascs = ascs;
    return projectJson;
  });
}

export {
  getProjectForAddress,
  projectContractToProjectJson,
  ascAddressToJson,
    getMergeASCForAddress,
    ascContractToASCJson
}

