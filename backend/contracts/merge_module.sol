pragma solidity ^0.4.24;
import "./module_interface.sol";

contract MergeModule {

    event Merge(uint pr_id);

    constructor(){
    }

    function merge(uint pr_id) public {
        // TODO validate that this module is allowed to execute
        emit Merge(pr_id);
    }

    function getName() public returns (string) {
        return "MergeModule";
    }
}
