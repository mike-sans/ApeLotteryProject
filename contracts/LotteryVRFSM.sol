// SPDX-License-Identifier: MIT
// pragma solidity >=0.6.6 <0.9.0;
pragma solidity ^0.8;

import "@chainlink/contracts/src/v0.8/shared/interfaces/AggregatorV3Interface.sol";
import "@chainlink/contracts/src/v0.8/vrf/VRFV2WrapperConsumerBase.sol";

contract LotteryVRFSM is VRFV2WrapperConsumerBase {
    // probably better to not have this array be payable, just to be extra safe
    address[] public players;
    address payable public winner;
    address public owner;
    uint256 public usdEntryFee = uint256(50 * (10 ** 18));
    uint256 public lotteryRound = 1;
    AggregatorV3Interface public priceFeed;
    LinkTokenInterface public link;

    enum OPEN_STATE {
        CLOSED,
        OPEN,
        CALCULATING_WINNER,
        PENDING_WINNER_WITHDRAW
    }
    OPEN_STATE public openStatus = OPEN_STATE.CLOSED;

    // Variables for VRF
    uint32 callbackGasLimit = 100000;
    uint16 requestConfirmations = 3;
    uint32 numWords = 1;
    event RequestSent(uint256 requestId, uint32 numWords);
    event RequestFulfilled(
        uint256 requestId,
        uint256[] randomWords,
        uint256 payment
    );

    struct RequestStatus {
        uint256 paid; // amount paid in link
        bool fulfilled; // whether the request has been successfully fulfilled
        uint256[] randomWords;
    }
    mapping(uint256 => RequestStatus)
        public s_requests; /* requestId --> requestStatus */

    // past requests Id.
    uint256[] public requestIds;
    uint256 public lastRequestId;

    // End of VRF variables

    constructor(
        address _priceFeed,
        address _link,
        address _wrapperAddress
    ) VRFV2WrapperConsumerBase(_link, _wrapperAddress) {
        priceFeed = AggregatorV3Interface(_priceFeed);
        link = LinkTokenInterface(_link);
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

    modifier cleanSlate() {
        require(
            address(this).balance == 0 && openStatus == OPEN_STATE.CLOSED,
            "Lottery is ongoing!"
        );
        _;
    }

    modifier openLottery() {
        require(openStatus == OPEN_STATE.OPEN, "Lottery is not open!");
        _;
    }

    modifier calculating() {
        require(
            openStatus == OPEN_STATE.CALCULATING_WINNER,
            "Lottery is not at the calculating stage!"
        );
        _;
    }

    modifier pendingWithdraw() {
        require(openStatus == OPEN_STATE.PENDING_WINNER_WITHDRAW);
        _;
    }

    modifier sufficientFunds() {
        require(
            getConversionRate(msg.value) >= usdEntryFee,
            "Not enough funds!"
        );
        _;
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

    function startLottery() public onlyOwner cleanSlate {
        openStatus = OPEN_STATE.OPEN;
    }

    function enter() public payable sufficientFunds openLottery {
        players.push(msg.sender);
    }

    function endLottery()
        external
        onlyOwner
        openLottery
        returns (uint256 requestId)
    {
        openStatus = OPEN_STATE.CALCULATING_WINNER;
        requestId = requestRandomness(
            callbackGasLimit,
            requestConfirmations,
            numWords
        );
        s_requests[requestId] = RequestStatus({
            paid: VRF_V2_WRAPPER.calculateRequestPrice(callbackGasLimit),
            randomWords: new uint256[](0),
            fulfilled: false
        });
        requestIds.push(requestId);
        lastRequestId = requestId;
        emit RequestSent(requestId, numWords);
        return requestId;
    }

    function fulfillRandomWords(
        uint256 _requestId,
        uint256[] memory _randomWords
    ) internal override calculating {
        require(s_requests[_requestId].paid > 0, "request not found");
        s_requests[_requestId].fulfilled = true;
        s_requests[_requestId].randomWords = _randomWords;
        emit RequestFulfilled(
            _requestId,
            _randomWords,
            s_requests[_requestId].paid
        );
        calculateWinner(_requestId);
    }

    function calculateWinner(uint256 _requestId) internal calculating {
        openStatus = OPEN_STATE.PENDING_WINNER_WITHDRAW;
        uint256 randNumber = s_requests[_requestId].randomWords[0];
        uint256 winnerIndex = randNumber % players.length;
        winner = payable(players[winnerIndex]);
    }

    function winnerWithdraw() external onlyWinner pendingWithdraw {
        openStatus = OPEN_STATE.CLOSED;
        winner.transfer(address(this).balance);
    }

    function getEntranceFee() public view returns (uint256) {
        return uint256((usdEntryFee * (10 ** 18)) / getPrice());
    }

    function getRequestStatus(
        uint256 _requestId
    )
        external
        view
        returns (uint256 paid, bool fulfilled, uint256[] memory randomWords)
    {
        require(s_requests[_requestId].paid > 0, "request not found");
        RequestStatus memory request = s_requests[_requestId];
        return (request.paid, request.fulfilled, request.randomWords);
    }

    function getWinner() external view returns (string memory, address) {
        if (winner == address(0)) {
            return (
                "No winner has been decided for the current round yet! ",
                winner
            );
        } else {
            return ("The winner of this round was: ", winner);
        }
    }

    function withdrawLink() public onlyOwner cleanSlate {
        require(
            link.transfer(msg.sender, link.balanceOf(address(this))),
            "Unable to transfer"
        );
    }
}
