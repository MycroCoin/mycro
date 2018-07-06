pragma solidity ^0.4.0;

import "./ASC_interface.sol";
import "./merge_module.sol";
import "./base_dao.sol";

contract MergeASC is ASC_interface {
    uint public prId;

    constructor(uint _prId){
        prId = _prId;
    }

    function execute() public {
        BaseDao dao = BaseDao(msg.sender);

        address merge_module_address = dao.getModuleByCode(1);
        MergeModule merge_module = MergeModule(merge_module_address);

        merge_module.merge(prId);
    }
}
