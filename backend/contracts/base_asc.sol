pragma solidity ^0.4.24;

contract BaseASC {
    address public rewardee;

    constructor() {
        rewardee = msg.sender;
    }

    function execute() public;

}
