pragma solidity ^0.4.24;

// ----------------------------------------------------------------------------
// 'Mycro' token contract
//
// Deployed to : 0x5A86f0cafD4ef3ba4f0344C138afcC84bd1ED222
// Symbol      : myc
// Name        : MycroCoin
// Total supply: 100000000
// Decimals    : 18
//
// Enjoy.
//
// (c) by Moritz Neto with BokkyPooBah / Bok Consulting Pty Ltd Au 2017. The MIT Licence.
// ----------------------------------------------------------------------------
import "./base_dao.sol";


contract MycroCoin is BaseDao{
    // Increment this any time the storage of this contract changes
    uint private constant VERSION = 1;

    address[] initialAddresses;
    uint[] initialBalances;
    bool initialized = false;

    address[] public registeredProjects;

    uint public constant INITIAL_TOTAL_SUPPLY = 100000000;

    event RegisterProject(address projectAddress);

    constructor() BaseDao("myc", "MycroCoin", 18, INITIAL_TOTAL_SUPPLY, getInitialAddresses(), getInitialBalances()) public{
        initialized = true;
    }

    function getInitialAddresses() public returns (address[]){
        if (initialized){
            return initialAddresses;
        }

        initialAddresses.push(0x364ca3F935E88Fbc9e041d2032F996CAc69452e6);

        return initialAddresses;
    }

    function getInitialBalances() public returns (uint[]){
        if (initialized){
            return initialBalances;
        }

        initialBalances.push(INITIAL_TOTAL_SUPPLY);

        return initialBalances;
    }

    function registerProject(address project) public {
        registeredProjects.push(project);

        emit RegisterProject(project);
    }


    function getProjects() public view returns (address[]) {
        return registeredProjects;
    }

    function getNumberOfProjects() public view returns (uint) {
        return registeredProjects.length;
    }

    function getVersion() public constant returns (uint) {
        return VERSION;
    }

    function upgradeFrom(address previousMycroAddress) public {
        MycroCoin mycroDao = MycroCoin(previousMycroAddress);
        super.upgradeFrom(previousMycroAddress);

        for(uint i = 0; i < mycroDao.getNumberOfProjects(); i++) {
            registerProject(mycroDao.registeredProjects(i));
        }
    }
}
