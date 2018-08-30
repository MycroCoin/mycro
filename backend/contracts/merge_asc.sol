pragma solidity ^0.4.0;

import "./base_asc.sol";
import "./merge_module.sol";
import "./base_dao.sol";

contract MergeASC is BaseASC {
    // Increment this any time the storage of this contract changes
    uint private constant VERSION = 1;

    uint public prId;

    constructor(address _rewardee, uint _reward, uint _prId) BaseASC(_rewardee, _reward) {
        prId = _prId;
    }

    function execute() public {
        if(hasExecuted) {
            return;
        }

        BaseDao dao = BaseDao(msg.sender);

        address mergeModuleAddress = dao.getModuleByCode(1);
        MergeModule mergeModule = MergeModule(mergeModuleAddress);

        mergeModule.merge(prId);
        hasExecuted = true;
    }

    function getVersion() public constant returns (uint) {
        return VERSION;
    }

    function upgradeFrom(address previousMergeAscAddress) public {
        super.upgradeFrom(previousMergeAscAddress);

        MergeASC previousMergeASC = MergeASC(previousMergeAscAddress);

        prId = previousMergeASC.prId();
    }
}
