pragma solidity ^0.4.24;
import "./module_interface.sol";

contract MergeModule {

    event Merge(uint prId);
    uint[] public pullRequestsToMerge;

    constructor(){
    }

    function merge(uint prId) public {
        // TODO validate that this module is allowed to execute
        emit Merge(prId);
        pullRequestsToMerge.push(prId);
    }

    function getCode() public returns (uint) {
        return 1;
    }

    // for some reason the getter that's autocreated won't return the whole array
    // the getter has a signature of `getPullRequestsToMerge(uint256)` and returns an element of the array based on the
    // given parameter
    function pullRequestsToMerge() public view returns (uint[]) {
        return pullRequestsToMerge;
    }
}
