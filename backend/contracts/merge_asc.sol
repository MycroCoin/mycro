pragma solidity ^0.4.0;

import "./ASC_interface.sol";
import "./merge_module.sol";

contract MergeASC is ASC_interface {
    MergeModule public merge_module;

    constructor(address _merge_module){
        merge_module = MergeModule(_merge_module);
    }

    function execute() public {
        merge_module.execute();
    }
}
