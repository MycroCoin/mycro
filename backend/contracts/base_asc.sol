pragma solidity ^0.4.24;

contract BaseASC {
    address public rewardee;
    bool public canExecute;

    constructor(address _rewardee) {
        rewardee = _rewardee;
        canExecute = true;
    }

    function execute() public;

}
