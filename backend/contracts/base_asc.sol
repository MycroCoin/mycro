pragma solidity ^0.4.24;

interface ASC_interface {
    function execute() public;
}

contract BaseASC is ASC_interface {
    address public rewardee;

    constructor() {
        rewardee = msg.sender;
    }

    function execute() public;

}
