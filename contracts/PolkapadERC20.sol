// SPDX-License-Identifier: MIT

pragma solidity ^0.8.7;

import '@openzeppelin/contracts/token/ERC20/ERC20.sol';

contract PolkapadERC20 is ERC20 {

    address public _locker;
    address public _multisig;

    modifier locker {
        require(msg.sender == _locker);
        _;
    }

    modifier multisig {
        require(msg.sender == _multisig);
        _;
    }

    constructor(
        string memory name_,
        string memory symbol_,
        address multisig_) ERC20(name_, symbol_) {
        _multisig = multisig_;
    }

    function mint(address to_, uint256 amount_) public locker {
        _mint(to_, amount_);
    }

    function burn(address from_, uint256 amount_) public locker {
        _burn(from_, amount_);
    }

    function setLockerContractAddress(address address_) public multisig {
        _locker = address_;
    }

    function transfer(address to_, uint256 amount_) public virtual override returns (bool) {
        revert();
    }

    function transferFrom(
        address from,
        address to,
        uint256 amount
    ) public virtual override returns(bool) {
        revert();
    }
}