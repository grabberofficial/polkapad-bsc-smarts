// SPDX-License-Identifier: MIT

pragma solidity ^0.8.7;

import '@openzeppelin/contracts/token/ERC20/ERC20.sol';

contract PolkapadFungibleToken is ERC20 {

    address private _owner;

    modifier owner {
        require(msg.sender == _owner);
        _;
    }

    constructor(string memory name_, string memory symbol_) ERC20(name_, symbol_) {
        _owner = msg.sender;
    }

    function mint(address to_, uint256 amount_) public owner {
        _mint(to_, amount_);
    }

    function burn(address from_, uint256 amount_) public owner {
        _burn(from_, amount_);
    }

    function transfer(address to, uint256 amount) public virtual override returns (bool) {}

    function transferFrom(
        address from,
        address to,
        uint256 amount
    ) public virtual override returns (bool) {}
}