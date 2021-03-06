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
    // Increment this any time the storage of this contract changes
    uint private constant VERSION = 1;

    string public symbol;
    string public  name;
    uint8 public decimals;
    uint public totalSupply;
    address[] public ascs;
    uint public threshold;
    address[] public transactors;

    mapping(address => uint) balances;
    mapping(address => mapping(address => uint)) allowed;
    mapping(address => address[]) ascVotes;
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

            performTransfer(address(0), currentAddress, currentBalance);
        }
        calculateThreshold();
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
        performTransfer(msg.sender, to, tokens);
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
        allowed[from][msg.sender] = safeSub(allowed[from][msg.sender], tokens);
        performTransfer(from, to, tokens);
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

    function propose(address ascAddress) public {
        require(indexOf(ascAddress, ascs) == -1);

        ascs.push(ascAddress);
    }

    function getProposals() public view returns (address[]) {
        return ascs;
    }

    function getNumberOfProposals() public view returns (uint) {
        return ascs.length;
    }

    function vote(address proposal) {
        require(indexOf(proposal, ascs) != -1);
        require(indexOf(msg.sender, ascVotes[proposal]) == -1);

        ascVotes[proposal].push(msg.sender);

        if (shouldExecuteAsc(proposal)) {
            executeAsc(proposal);
        }
    }

    //TODO test this
    function getAscVotes(address proposal) public view returns (address[]) {
      require(indexOf(proposal, ascs) != -1);
      
      return ascVotes[proposal];
    }

    function getNumVotes(address ascAddress) public view returns (uint256) {
        return ascVotes[ascAddress].length;
    }

    function getAscVoter(address ascAddress, uint index) public view returns (address) {
        return ascVotes[ascAddress][index];
    }

    function executeAsc(address ascAddress) internal returns (uint){
        BaseASC asc = BaseASC(ascAddress);

        asc.execute();

        address rewardee = asc.rewardee();
        uint reward = asc.reward();
        performTransfer(address(0), rewardee, reward);
        totalSupply += reward;
        calculateThreshold();
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

    function shouldExecuteAsc(address ascAddress) internal view returns (bool) {
        BaseASC asc = BaseASC(ascAddress);
        if (asc.hasExecuted()) {
            return false;
        }

        uint sum = 0;

        // TODO make this more efficient
        for (uint i = 0; i < ascVotes[ascAddress].length; i++) {
            sum += balances[ascVotes[ascAddress][i]];
        }

        if (sum >= threshold) {
            return true;
        }

        return false;
    }

    function calculateThreshold() internal {
        threshold = totalSupply / 2 + 1;
    }

    function getTransactors() public view returns (address[]) {
        return transactors;
    }

    function getNumberOfTransactors() public view returns (uint) {
        return transactors.length;
    }

    function performTransfer(address from, address to, uint tokens) internal {
        // only allowed to mint tokens. Transfers are not allowed yet.
        require(from == address(0));

        // can't send tokens to the dao itself
        require(to != address(0));

        // if the destination doesn't have tokens yet, remember them as a transactor
        if(balances[to] == 0) {
            transactors.push(to);
        }

        // perform the transfer
        balances[to] = safeAdd(balances[to], tokens);
        emit Transfer(from, to, tokens);
    }

    function getVersion() public constant returns (uint) {
        return VERSION;
    }

    function upgradeFrom(address previousDaoAddress) public {
        // NOTE: this specifically does not copy over allowed, or modulesByCode or modulesByAddress
        BaseDao previousDao = BaseDao(previousDaoAddress);

        // unfortunately, it seems that strings can't be passed between contracts yet, at least I couldn't figure it out
        // on my backend, maybe it's possible on mainnet. Upon further investigation this isn't yet possible with a local
        // evm version of 0.4.22+ and pyethereum because certain opcodes aren't yet implemented in pyethereum:
        // https://github.com/ethereum/web3.py/issues/926
        //
        // require(keccak256(symbol) == keccak256(previousDao.symbol()));
        // require(keccak256(name) == keccak256(previousDao.name()));
        require(decimals == previousDao.decimals());

        totalSupply = previousDao.totalSupply();
        threshold = previousDao.threshold();

        // copy the ASCs
        uint numProposals = previousDao.getNumberOfProposals();
        for(uint i = 0; i < numProposals; i++) {
            address asc = previousDao.ascs(i);
            ascs.push(asc);

            // copy the votes of each ASC
            for(uint j = 0; j < previousDao.getNumVotes(asc); j++) {
                ascVotes[asc].push(previousDao.getAscVoter(asc, j));
            }
        }

        // copy balances of coin holders. Copy the transactors too
        uint numTransactors = previousDao.getNumberOfTransactors();
        for(i = 0; i < numTransactors; i++) {
            address transactor = previousDao.transactors(i);
            transactors.push(transactor);
            balances[transactor] = previousDao.balanceOf(transactor);
        }
    }

}
