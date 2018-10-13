const web3 = window.web3;

const networkNames = {
  "1": "MainNet",
  "2": "Morden",
  "3": "Ropsten",
  "4": "Rinkeby",
};

const getNetworkName = () => {
  return new Promise((resolve) => {
    if(!web3) {
      resolve('unknown');
      return;
    }
    web3.version.getNetwork((err, networkId) => {
      if (err != null) {
        console.error("Error when getting network: " + err)
        return
      }
      const networkName = networkNames[networkId] || 'unknown';
      if(networkName === 'unknown') {
          console.log('This is an unknown network.')
      }
      resolve(networkName);
    })
  });
}

const getAccount = () => {
  if(!web3) return Promise.resolve(null);

  return new Promise((resolve, reject) => {
    web3.eth.getAccounts((err, accounts) => {
      if(!err && accounts && accounts.length){
        resolve(accounts[0]);
        return;
      }
      if (err != null) {
        console.error("An error occurred: " + err);
      }

      resolve(null);
    });
  });

}

export default {
  getNetworkName,
  getAccount
};
