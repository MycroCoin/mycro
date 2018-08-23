pragma solidity ^0.4.0;

import "./base_asc.sol";
import "./merge_module.sol";
import "./base_dao.sol";

contract MergeASC is BaseASC {
    uint public prId;

    constructor(address _rewardee, uint _reward, uint _prId) BaseASC(_rewardee, _reward) {
        prId = _prId;
    }

    function execute() public {
        if(hasExecuted) {
            return;
        }

        BaseDao dao = BaseDao(msg.sender);

        address merge_module_address = dao.getModuleByCode(1);
        MergeModule merge_module = MergeModule(merge_module_address);

        merge_module.merge(prId);
        hasExecuted = true;
    }

    function upgradeFrom(address previousMergeAscAddress) public {
        super.upgradeFrom(previousMergeAscAddress);

        MergeASC previousMergeASC = MergeASC(previousMergeAscAddress);

        prId = previousMergeASC.prId();
    }
}
