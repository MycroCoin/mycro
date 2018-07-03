pragma solidity ^0.4.0;

import "../ASC_interface.sol";
import "../merge_module.sol";

contract DummyASC is ASC_interface {
    MergeModule public merge_module;

    event Execution();

    constructor(){
        merge_module = new MergeModule();
    }

    function execute() public {
        // TODO this should execute a module instead of do nothing
        // TODO this emits an Execution event while we wait for @kyle to finish off the merge_module event
        emit Execution();
    }
}
