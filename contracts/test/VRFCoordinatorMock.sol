// SPDX-License-Identifier: MIT
pragma solidity ^0.8.4;

// import {LinkTokenInterface} from "@chainlink/src/v0.8/shared/interfaces/LinkTokenInterface.sol";
// import {VRFConsumerBaseV2} from "@chainlink/src/v0.8/vrf/VRFConsumerBaseV2.sol";
// import {BlockhashStoreInterface} from "@chainlink/src/v0.8/interfaces/BlockhashStoreInterface.sol";
// import {AggregatorV3Interface} from "@chainlink/src/v0.8/shared/interfaces/AggregatorV3Interface.sol";
// import {VRFCoordinatorV2Interface} from "@chainlink/src/v0.8/vrf/interfaces/VRFCoordinatorV2Interface.sol";
// import {TypeAndVersionInterface} from "@chainlink/src/v0.8/interfaces/TypeAndVersionInterface.sol";
// import {IERC677Receiver} from "@chainlink/src/v0.8/shared/interfaces/IERC677Receiver.sol";
// import {VRF} from "@chainlink/src/v0.8/vrf/VRF.sol";
// import {ConfirmedOwner} from "@chainlink/src/v0.8/shared/access/ConfirmedOwner.sol";
// import {ChainSpecificUtil} from "@chainlink/src/v0.8/ChainSpecificUtil.sol";

import "@chainlink/src/v0.8/shared/interfaces/LinkTokenInterface.sol";
import "@chainlink/src/v0.8/vrf/VRFConsumerBaseV2.sol";

contract VRFCoordinatorMock {
    LinkTokenInterface public LINK;

    event RandomnessRequest(
        address indexed sender,
        bytes32 indexed keyHash,
        uint256 indexed seed
    );

    constructor(address linkAddress) public {
        LINK = LinkTokenInterface(linkAddress);
    }

    function onTokenTransfer(
        address sender,
        uint256 fee,
        bytes memory _data
    ) public onlyLINK {
        (bytes32 keyHash, uint256 seed) = abi.decode(_data, (bytes32, uint256));
        emit RandomnessRequest(sender, keyHash, seed);
    }

    function callBackWithRandomness(
        bytes32 requestId,
        uint256 randomness,
        address consumerContract
    ) public {
        VRFConsumerBaseV2 v;
        bytes memory resp = abi.encodeWithSelector(
            v.rawFulfillRandomWords.selector,
            requestId,
            randomness
        );
        uint256 b = 206000;
        require(gasleft() >= b, "not enough gas for consumer");
        (bool success, ) = consumerContract.call(resp);
    }

    modifier onlyLINK() {
        require(msg.sender == address(LINK), "Must use LINK token");
        _;
    }
}
