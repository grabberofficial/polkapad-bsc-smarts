// SPDX-License-Identifier: MIT

pragma solidity ^0.8.7;

contract Whitelist {

    struct Participant {
        bool approved;
        uint256 maxAllocationSize;
    }

    mapping (address => Participant) public participants;

    uint256 public defaultAllocationSize;
    address public multisigAddress;

    event AddedToWhitelist(address indexed account);
    event RemovedFromWhitelist(address indexed account);
    event ChangedMaxAllocationSize(
        address indexed account, 
        uint256 oldAllocationSize, 
        uint256 newAllocationSize);

    constructor(
        address multisigAddress_, 
        uint256 defaultAllocationSize_) {
        multisigAddress = multisigAddress_;
        
        defaultAllocationSize = defaultAllocationSize_;
    }

    modifier multisig {
        require(msg.sender == multisigAddress);
        _;
    }

    function add(address address_, uint256 allocationSize_) public multisig {
        participants[address_] = Participant({
            approved: true,
            maxAllocationSize: allocationSize_ != 0 ? allocationSize_ : defaultAllocationSize 
        });
        
        emit AddedToWhitelist(address_);
    }

    function remove(address address_) public multisig {
        participants[address_].approved = false;
        
        emit RemovedFromWhitelist(address_);
    }

    function changeAllocationSize(address address_, uint256 allocationSize_) public multisig {
        Participant memory oldParticipant = participants[address_];

        participants[address_] = Participant({
            approved: oldParticipant.approved,
            maxAllocationSize: allocationSize_ != 0 ? allocationSize_ : defaultAllocationSize 
        });
        
        emit ChangedMaxAllocationSize(address_, oldParticipant.maxAllocationSize, allocationSize_);
    }

    function isWhitelisted(address address_) public view returns (bool) {
        return participants[address_].approved;
    }
}