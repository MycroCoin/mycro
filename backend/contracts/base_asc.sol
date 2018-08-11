pragma solidity ^0.4.24;

contract BaseASC {
    address public rewardee;
    bool public hasExecuted;
    uint public reward;

    constructor(address _rewardee, uint _reward) {
        rewardee = _rewardee;
        hasExecuted = false;
        reward = _reward;
    }

    function execute() public;

}
