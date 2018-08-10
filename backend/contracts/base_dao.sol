pragma solidity ^0.4.24;

// ----------------------------------------------------------------------------
// 'Mycro' token contract
//
// Deployed to : 0x5A86f0cafD4ef3ba4f0344C138afcC84bd1ED222
// Symbol      : myc
// Name        : MycroCoin
// Total supply: 100000000
// Decimals    : 18
//
// Enjoy.
//
// (c) by Moritz Neto with BokkyPooBah / Bok Consulting Pty Ltd Au 2017. The MIT Licence.
// ----------------------------------------------------------------------------
import "./safe_math.sol";
import "./erc20_interface.sol";
import "./approve_and_call_fallback.sol";
import "./owned.sol";
import "./base_asc.sol";
import "./module_interface.sol";


// ----------------------------------------------------------------------------
// ERC20 Token, with the addition of symbol, name and decimals and assisted
// token transfers
// ----------------------------------------------------------------------------
contract BaseDao is ERC20Interface, Owned, SafeMath {
    string public symbol;
    string public  name;
    uint8 public decimals;
    uint public totalSupply;
    address[] action_smart_contracts;
    uint public threshold;

    mapping(address => uint) balances;
    mapping(address => mapping(address => uint)) allowed;
    mapping(address => address[]) asc_votes;
    mapping(uint => address) modulesByCode;
    mapping(address => uint) modulesByAddress;




    // ------------------------------------------------------------------------
    // Constructor
    // ------------------------------------------------------------------------
    constructor(string _symbol, string _name, uint8 _decimals, uint _totalSupply, address[] _initialAddresses, uint[] _initialBalances) public {
        // TODO check that the sum of the initial balances == _totalSupply
        // TODO figure out why this always fails with the Mycro DAO
        require(_initialAddresses.length == _initialBalances.length);

        symbol = _symbol;
        name = _name;
        decimals = _decimals;
        totalSupply = _totalSupply;

        for (uint i = 0; i < _initialAddresses.length; i++) {
            address currentAddress = _initialAddresses[i];
            uint currentBalance = _initialBalances[i];

            balances[currentAddress] = currentBalance;
            emit Transfer(address(0), currentAddress, currentBalance);
        }

        threshold = totalSupply / 2 + 1;
    }


    // ------------------------------------------------------------------------
    // Total supply
    // ------------------------------------------------------------------------
    function totalSupply() public constant returns (uint) {
        return totalSupply - balances[address(0)];
    }


    // ------------------------------------------------------------------------
    // Get the token balance for account tokenOwner
    // ------------------------------------------------------------------------
    function balanceOf(address tokenOwner) public constant returns (uint balance) {
        return balances[tokenOwner];
    }


    // ------------------------------------------------------------------------
    // Transfer the balance from token owner's account to to account
    // - Owner's account must have sufficient balance to transfer
    // - 0 value transfers are allowed
    // ------------------------------------------------------------------------
    function transfer(address to, uint tokens) public returns (bool success) {
        balances[msg.sender] = safeSub(balances[msg.sender], tokens);
        balances[to] = safeAdd(balances[to], tokens);
        emit Transfer(msg.sender, to, tokens);
        return true;
    }


    // ------------------------------------------------------------------------
    // Token owner can approve for spender to transferFrom(...) tokens
    // from the token owner's account
    //
    // https://github.com/ethereum/EIPs/blob/master/EIPS/eip-20-token-standard.md
    // recommends that there are no checks for the approval double-spend attack
    // as this should be implemented in user interfaces
    // ------------------------------------------------------------------------
    function approve(address spender, uint tokens) public returns (bool success) {
        allowed[msg.sender][spender] = tokens;
        Approval(msg.sender, spender, tokens);
        return true;
    }


    // ------------------------------------------------------------------------
    // Transfer tokens from the from account to the to account
    //
    // The calling account must already have sufficient tokens approve(...)-d
    // for spending from the from account and
    // - From account must have sufficient balance to transfer
    // - Spender must have sufficient allowance to transfer
    // - 0 value transfers are allowed
    // ------------------------------------------------------------------------
    function transferFrom(address from, address to, uint tokens) public returns (bool success) {
        balances[from] = safeSub(balances[from], tokens);
        allowed[from][msg.sender] = safeSub(allowed[from][msg.sender], tokens);
        balances[to] = safeAdd(balances[to], tokens);
        emit Transfer(from, to, tokens);
        return true;
    }


    // ------------------------------------------------------------------------
    // Returns the amount of tokens approved by the owner that can be
    // transferred to the spender's account
    // ------------------------------------------------------------------------
    function allowance(address tokenOwner, address spender) public constant returns (uint remaining) {
        return allowed[tokenOwner][spender];
    }


    // ------------------------------------------------------------------------
    // Token owner can approve for spender to transferFrom(...) tokens
    // from the token owner's account. The spender contract function
    // receiveApproval(...) is then executed
    // ------------------------------------------------------------------------
    function approveAndCall(address spender, uint tokens, bytes data) public returns (bool success) {
        allowed[msg.sender][spender] = tokens;
        Approval(msg.sender, spender, tokens);
        ApproveAndCallFallBack(spender).receiveApproval(msg.sender, tokens, this, data);
        return true;
    }


    // ------------------------------------------------------------------------
    // Don't accept ETH
    // ------------------------------------------------------------------------
    function() public payable {
        revert();
    }


    // ------------------------------------------------------------------------
    // Owner can transfer out any accidentally sent ERC20 tokens
    // ------------------------------------------------------------------------
    function transferAnyERC20Token(address tokenAddress, uint tokens) public onlyOwner returns (bool success) {
        return ERC20Interface(tokenAddress).transfer(owner, tokens);
    }

    function propose(address asc_address) public {
        require(indexOf(asc_address, action_smart_contracts) == -1);

        action_smart_contracts.push(asc_address);
    }

    function get_proposals() public view returns (address[]) {
        return action_smart_contracts;
    }

    function vote(address proposal) {
        require(indexOf(proposal, action_smart_contracts) != -1);
        require(indexOf(msg.sender, asc_votes[proposal]) == -1);

        asc_votes[proposal].push(msg.sender);

        if (shouldExecuteAsc(proposal)) {
            execute_asc(proposal);
        }
    }

    //TODO test this
    function get_asc_votes(address proposal) public view returns (address[]) {
      require(indexOf(proposal, action_smart_contracts) != -1);
      
      return asc_votes[proposal];
    }

    function get_num_votes(address asc_address) public view returns (uint256) {
        return asc_votes[asc_address].length;
    }

    function execute_asc(address asc_address) internal returns (uint){
        BaseASC asc = BaseASC(asc_address);

        asc.execute();

        address rewardee = asc.rewardee();
        balances[rewardee] = safeAdd(balances[rewardee], 10);
        emit Transfer(address(0), rewardee, 10);
    }

    function registerModule(address add) public {
        ModuleInterface module = ModuleInterface(add);
        uint code = module.getCode();
        modulesByAddress[module] = code;
        modulesByCode[code] = module;
    }


    function isModuleRegistered(ModuleInterface module) public view returns (bool) {
        return modulesByCode[module.getCode()] != 0;
    }

    function getModuleByCode(uint code) public view returns (address){
        return modulesByCode[code];
    }

    function indexOf(address needle, address[] haystack) internal pure returns (int) {

        // TODO make this more efficient
        for(uint i = 0; i < haystack.length; i++) {
            if (haystack[i] == needle) {
                return int(i);
            }
        }

        return -1;
    }

    function shouldExecuteAsc(address asc_address) internal view returns (bool) {
        BaseASC asc = BaseASC(asc_address);
        if (!asc.canExecute()) {
            return false;
        }

        uint sum = 0;

        // TODO make this more efficient
        for (uint i = 0; i < asc_votes[asc_address].length; i++) {
            sum += balances[asc_votes[asc_address][i]];
        }

        if (sum >= threshold) {
            return true;
        }

        return false;
    }

}
