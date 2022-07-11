// SPDX-License-Identifier: MIT

pragma solidity ^0.8.7;

contract Whitelist {

    mapping (address => bool)    public whitelist;
    mapping (address => uint256) public allocationSizes;

    uint256 public defaultAllocationSize;
    address public multisigAddress;

    event AddedToWhitelist(address indexed account);
    event RemovedFromWhitelist(address indexed account);
    event ChangedMaxAllocationSize(
        address indexed account, 
        uint256 oldMaxAllocationSize, 
        uint256 newMaxAllocationSize);

    constructor(address multisigAddress_) {
        multisigAddress = multisigAddress_;
    }

    modifier multisig {
        require(msg.sender == multisigAddress);
        _;
    }

    function add(address address_, uint256 allocationSize_) public multisig {
        whitelist[address_] = true;
        if (allocationSize_ != 0 && allocationSize_ != defaultAllocationSize) {
            allocationSizes[address_] = allocationSize_;
        }

        emit AddedToWhitelist(address_);
    }

    function remove(address address_) public multisig {
        delete whitelist[address_];
        if (allocationSizes[address_] != 0) {
            delete allocationSizes[address_];
        }
        
        emit RemovedFromWhitelist(address_);
    }

    function changeAllocationSize(address address_, uint256 newMaxAllocationSize_) public multisig {
        require(whitelist[address_] == true, "Whitelist does not contain provided address");
        
        uint256 oldMaxAllocationSize = allocationSizes[address_];
        allocationSizes[address_] = newMaxAllocationSize_;

        emit ChangedMaxAllocationSize(address_, oldMaxAllocationSize, newMaxAllocationSize_);
    }

    function setDefaultAllocationSize(uint256 allocationSize_) public multisig {
        require(allocationSize_ > 0);

        defaultAllocationSize = allocationSize_;
    }
}