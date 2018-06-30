pragma solidity ^0.4.24;
import "./module_interface.sol";

contract MergeModule {
    uint pr_id;

    event Merge(uint pr_id);

    constructor(uint id){
        pr_id = id;
    }

    function execute() public {
        // TODO validate that this module is allowed to execute
        emit Merge(pr_id);
    }
}
