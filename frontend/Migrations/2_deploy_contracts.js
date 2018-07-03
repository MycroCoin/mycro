var contracts = [
  "MergeModule",
  "MycroCoin",
];

const imported = 
  contracts.map( (contract) => artifacts.require(contract));

module.exports = function(deployer) {
  imported.map( (contract) => deployer.deploy(contract));
};
