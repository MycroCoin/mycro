/*
 * NB: since truffle-hdwallet-provider 0.0.5 you must wrap HDWallet providers in a 
 * function when declaring them. Failure to do so will cause commands to hang. ex:
 * ```
 * mainnet: {
 *     provider: function() { 
 *       return new HDWalletProvider(mnemonic, 'https://mainnet.infura.io/<infura-key>') 
 *     },
 *     network_id: '1',
 *     gas: 4500000,
 *     gasPrice: 10000000000,
 *   },
 */
var Web3 = require('web3');

module.exports = {
    networks: {
        development: {
            // host: "u0g9fge43j:LhDEo1KYAuHatVJ2uFaR3i6zK7uIDVBC5Q6RA4UXfHg@u0a9n6r4oc-u0qutwl2df-rpc.us-east-2.kaleido.io",
            // port: 443,
            provider: function () {
                return new Web3.providers.HttpProvider("https://u0a9n6r4oc-u0qutwl2df-rpc.us-east-2.kaleido.io", 0, "u0g9fge43j", "LhDEo1KYAuHatVJ2uFaR3i6zK7uIDVBC5Q6RA4UXfHg");
            },
            network_id: "*", // Match any network id
            gasPrice: 0,
            gas: 4500000

        }
    }
};
