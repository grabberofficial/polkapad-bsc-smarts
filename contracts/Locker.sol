// SPDX-License-Identifier: MIT

pragma solidity ^0.8.7;

import '@openzeppelin/contracts/token/ERC20/IERC20.sol';
import '@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol';

contract Locker {

    uint256 public constant DENOMINATOR = 10e8;

    address public targetWallet;
    uint256 public upperBoundAmount;
    mapping (address => uint256) public locks;

    IERC20 private _dotContract;
    IERC20 private _plpdContract;
    AggregatorV3Interface private _priceFeed;
    address private _owner;

    /**
     * Network: BSC Testnet
     * Aggregator: DOT/USD
     * Address: 0xEA8731FD0685DB8AeAde9EcAE90C4fdf1d8164ed

     * Network: BSC Mainnet
     * Aggregator: DOT/USD
     * Address: 0xC333eb0086309a16aa7c8308DfD32c8BBA0a2592

     * Network: BSC Mainnet
     * Contract: DOT
     * Address: 0x7083609fCE4d1d8Dc0C979AAb8c869Ea2C873402

     * 1 PPAD TOKEN is $0.30
     */
    constructor(
        address plpdContract_, 
        address dotContract_, 
        address feedContract_,
        address targetWallet_) {
        _owner = msg.sender;
        _dotContract = IERC20(dotContract_);
        _plpdContract = IERC20(plpdContract_);
        _priceFeed = AggregatorV3Interface(feedContract_);

        targetWallet = targetWallet_;
    }

    modifier owner {
        require(msg.sender == _owner);
        _;
    }

    function lock(uint256 toLockAmount_) public {
        uint256 price = getLatestPrice();

        uint256 lockedAmount = locks[msg.sender];
        uint256 toLockAmount = (lockedAmount + toLockAmount_) * price / DENOMINATOR;

        require(
            toLockAmount < upperBoundAmount,
            "Locker: you cannot allocate more than ~~~ USD");

        locks[msg.sender] = lockedAmount + toLockAmount_;

        _dotContract.transferFrom(msg.sender, targetWallet, toLockAmount_);
        // _plpdContract.mint(msg.sender, 10);
    }

    // upper bound in USD
    function setUpperBound(uint256 amount) public owner {
        upperBoundAmount = amount;
    }

    function getLatestPrice() public view returns (uint256) {
        (
            /*uint80 roundID*/,
            int price,
            /*uint startedAt*/,
            /*uint timeStamp*/,
            /*uint80 answeredInRound*/
        ) = _priceFeed.latestRoundData();
        return uint256(price);
    }
}
