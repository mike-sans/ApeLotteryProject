// SPDX-License-Identifier: MIT
pragma solidity ^0.8;
import "@chainlink/contracts/src/v0.8/shared/interfaces/AggregatorV3Interface.sol";

contract LotteryCaR {
    // probably better to not have this array be payable, just to be extra secure
    // address payable[] public players;
    address[] public players;
    address owner;
    AggregatorV3Interface public priceFeed;
    uint256 public usdEntryFee = uint256(200 * (10 ** 18));
    mapping(address => uint256) public addressToAmountFunded;
    address public winner;

    enum OPEN_STATE {
        CLOSED,
        OPEN,
        PENDING_REVEAL,
        PENDING_WINNER_WITHDRAW
    }
    OPEN_STATE public openStatus = OPEN_STATE.CLOSED;

    constructor(address _priceFeed) {
        priceFeed = AggregatorV3Interface(_priceFeed);
        owner = msg.sender;
    }

    modifier onlyOwner() {
        require(msg.sender == owner);
        _;
    }

    modifier onlyWinner() {
        require(msg.sender == winner);
        _;
    }

    modifier openLottery() {
        require(openStatus == OPEN_STATE.OPEN);
        _;
    }

    modifier cleanSlate() {
        require(address(this).balance == 0);
        _;
    }

    modifier sufficientFunds() {
        require(getConversionRate(msg.value) >= usdEntryFee);
        _;
    }

    function enter() public payable sufficientFunds openLottery {
        addressToAmountFunded[msg.sender] += msg.value;
        players.push(msg.sender);
    }

    function getEntranceFee() public view returns (uint256) {
        return uint256((usdEntryFee * (10 ** 18)) / getPrice());
    }

    function startLottery() public onlyOwner cleanSlate {
        openStatus = OPEN_STATE.OPEN;
    }

    // TODO
    function endLottery() public onlyOwner openLottery returns (address) {
        openStatus = OPEN_STATE.PENDING_WINNER_WITHDRAW;
        // address winner = random(players);

        for (
            uint256 funderIndex = 0;
            funderIndex < players.length;
            funderIndex++
        ) {
            addressToAmountFunded[players[funderIndex]] = 0;
        }
        players = new address[](0);
        return winner;
    }

    function winnerWithdraw() public onlyWinner {
        address payable winnerPayable = payable(winner);
        winner = address(0);
        openStatus = OPEN_STATE.CLOSED;
        winnerPayable.transfer(address(this).balance);
    }

    function getConversionRate(
        uint256 ethAmount
    ) public view returns (uint256) {
        uint256 ethPrice = getPrice();
        uint256 ethAmountInUSD = (ethPrice * ethAmount) / (10 ** 18);
        return ethAmountInUSD;
    }

    function getPrice() public view returns (uint256) {
        (, int256 answer, , , ) = priceFeed.latestRoundData();
        return uint256(answer * (10 ** 10));
    }
}
