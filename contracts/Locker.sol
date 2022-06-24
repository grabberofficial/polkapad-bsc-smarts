// SPDX-License-Identifier: MIT

pragma solidity ^0.8.7;

import '@openzeppelin/contracts/token/ERC20/IERC20.sol';
import '@openzeppelin/contracts/utils/math/SafeMath.sol';
import '@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol';
import './PolkapadERC20.sol';
import './Whitelist.sol';

contract Locker {
    using SafeMath for uint256;

    uint256 public constant DENOMINATOR = 10e7;

    mapping (address => uint256) public _locks;

    IERC20 public _dotContract;
    PolkapadERC20 public _plpdContract;
    Whitelist public _whitelistContract;

    AggregatorV3Interface public _dotPriceFeed;

    address public _owner;
    address public _multisig;

    event Locked(address indexed account, uint256 allocation);

    constructor(
        address multisig_,
        address dotContract_, 
        address dotFeedContract_,
        address whitelistContract_) {
        _owner = msg.sender;

        _multisig = multisig_;

        _dotContract = IERC20(dotContract_);
        _whitelistContract = Whitelist(whitelistContract_);

        _dotPriceFeed = AggregatorV3Interface(dotFeedContract_);
    }

    modifier owner {
        require(msg.sender == _owner);
        _;
    }

    modifier whitelisted {
        require(_whitelistContract.isWhitelisted(msg.sender));
        _;
    }

    function lock(uint256 toLockAmount_) public whitelisted {
        uint256 dotPrice = getLatestPrice();

        uint256 lockedAmount = _locks[msg.sender];
        uint256 toLockAmount = lockedAmount.add(toLockAmount_).mul(dotPrice).div(DENOMINATOR);

        (/* approved */, uint256 maxAllocationSize) = _whitelistContract.participants(msg.sender);

        require(
            toLockAmount < maxAllocationSize,
            "Locker: you cannot allocate more than max allocation value");

        _locks[msg.sender] = lockedAmount.add(toLockAmount_);

        _dotContract.transferFrom(msg.sender, _multisig, toLockAmount_);

        uint256 plpdAmount = toLockAmount_.mul(dotPrice).div(DENOMINATOR).mul(3).div(10);
        _plpdContract.mint(msg.sender, plpdAmount); // probably need to replace it with argument

        emit Locked(msg.sender, toLockAmount_);
    }

    function setPlpdContractAddress(address plpdContract_) public owner {
        _plpdContract = PolkapadERC20(plpdContract_);
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
