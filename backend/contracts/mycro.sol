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

    address[] initialAddresses;
    uint[] initialBalances;
    bool initialized = false;

    address[] public registeredProjects;

    event RegisterProject(address projectAddress);

    constructor() BaseDao("myc", "MycroCoin", 18, 100000000000000000000000000, getInitialAddresses(), getInitialBalances()) public{
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

        initialBalances.push(100000000000000000000000000);

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

    function upgradeFrom(address previousMycroAddress) public {
        MycroCoin mycroDao = MycroCoin(previousMycroAddress);
        super.upgradeFrom(previousMycroAddress);

        for(uint i = 0; i < mycroDao.getNumberOfProjects(); i++) {
            registerProject(mycroDao.registeredProjects(i));
        }
    }
}
