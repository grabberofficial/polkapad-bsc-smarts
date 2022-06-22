// SPDX-License-Identifier: MIT

pragma solidity ^0.8.7;

import '@openzeppelin/contracts/token/ERC20/ERC20.sol';

contract PolkapadERC20 is ERC20 {

    address public _locker;

    modifier locker {
        require(msg.sender == _locker);
        _;
    }

    constructor(
        string memory name_, 
        string memory symbol_, 
        address lockerContract_) ERC20(name_, symbol_) {
        _locker = lockerContract_;
    }

    function mint(address to_, uint256 amount_) public locker {
        _mint(to_, amount_);
    }

    function burn(address from_, uint256 amount_) public locker {
        _burn(from_, amount_);
    }

    function transfer(address to_, uint256 amount_) public virtual override returns(bool) {
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