pragma solidity ^0.4.0;
import "../module_interface.sol";

contract DummyModule is ModuleInterface {

    function getCode() public returns (uint) {
        return 9999;
    }
}
