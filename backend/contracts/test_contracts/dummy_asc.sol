pragma solidity ^0.4.0;

import "../ASC_interface.sol";
import "../merge_module.sol";

contract DummyASC is ASC_interface {
    MergeModule public merge_module;

    constructor(){
        merge_module = new MergeModule();
    }

    function execute() public {
        // TODO this should execute a module instead of do nothing
    }
}
