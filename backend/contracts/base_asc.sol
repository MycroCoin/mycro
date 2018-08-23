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

    function upgradeFrom(address previousAscAddress) public {
        BaseASC previousASC = BaseASC(previousAscAddress);

        require(!previousASC.hasExecuted());
        require(!hasExecuted);

        reward = previousASC.reward();
        rewardee = previousASC.rewardee();
    }

}
