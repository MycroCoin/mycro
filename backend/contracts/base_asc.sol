pragma solidity ^0.4.24;

contract BaseASC {
    address public rewardee;

    constructor(address _rewardee) {
        rewardee = _rewardee;
    }

    function execute() public;

}
