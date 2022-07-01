// SPDX-License-Identifier: MIT

pragma solidity ^0.8.7;

import '@openzeppelin/contracts/token/ERC20/ERC20.sol';
import '@openzeppelin/contracts/utils/math/SafeMath.sol';
import '@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol';
import './PolkapadERC20.sol';
import './Whitelist.sol';

contract Locker {
    using SafeMath for uint256;

    mapping (address => uint256) public _locks;

    ERC20 public _dotContract;
    PolkapadERC20 public _plpdContract;
    Whitelist public _whitelistContract;

    AggregatorV3Interface public _dotPriceFeed;

    address public _multisig;

    event Locked(address indexed account, uint256 allocation);

    constructor(
        address multisig_,
        address dotContract_, 
        address dotFeedContract_,
        address plpdContract_,
        address whitelistContract_) {
        _multisig = multisig_;

        _plpdContract = PolkapadERC20(plpdContract_);
        _dotContract = ERC20(dotContract_);
        _whitelistContract = Whitelist(whitelistContract_);

        _dotPriceFeed = AggregatorV3Interface(dotFeedContract_);
    }

    modifier whitelisted {
        require(_whitelistContract.whitelist(msg.sender) == true);
        _;
    }

    modifier multisig {
        require(msg.sender == _multisig);
        _;
    }

    function lock(uint256 allocation_) public whitelisted {
        uint256 dotPrice = getLatestPrice();

        uint256 lockedAllocation = _locks[msg.sender];
        uint256 allocationInUsdt = lockedAllocation.add(allocation_).mul(dotPrice);

        uint256 maxAllocationSize = _whitelistContract.allocationSizes(msg.sender);
        if (maxAllocationSize == 0) {
            maxAllocationSize = _whitelistContract.defaultAllocationSize();
        }

        require(
            allocationInUsdt < maxAllocationSize,
            "Locker: you cannot allocate more than max allocation value");

        _dotContract.transferFrom(msg.sender, _multisig, allocation_);

        uint256 plpdAmount = allocationInUsdt.mul(3).div(10);
        _plpdContract.mint(msg.sender, plpdAmount);

        _locks[msg.sender] = lockedAllocation.add(allocation_);

        emit Locked(msg.sender, allocation_);
    }

    function burnPlpd(address address_) public multisig {
        uint256 plpdAmount = _plpdContract.balanceOf(address_);
        _plpdContract.burn(address_, plpdAmount);
     }

    function getLatestPrice() public view returns (uint256) {
        (
            /*uint80 roundID*/,
            int price,
            /*uint startedAt*/,
            /*uint timeStamp*/,
            /*uint80 answeredInRound*/
        ) = _dotPriceFeed.latestRoundData();
        return uint256(price);
    }
}
