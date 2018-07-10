var contracts = [
  ["MergeModule"],
  ["MycroCoin"],
];

const imported = 
  contracts.map( ([contract, ...args]) => [artifacts.require(contract), ...args]);

module.exports = function(deployer) {
  imported.map( ([contract, ...args]) => deployer.deploy(contract, ...args));
};
