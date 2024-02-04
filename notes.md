# In order to make a mock direct funding method pipeline, following are the things to do:

## Test deployment order
When in a local testing environment, the order should be (1) MockV3Aggregator, (2) MockLinkToken, (3) VRFCoordinatorV2Mock, (4) VRFV2WrapperMock

## LotteryVRFDFM.sol
This will stay the same for obvious reasons

This script calls requestRandomness(callbackGasLimit, requestConfirmations, numWords); which is defined in VRFV2WrapperConsumerBase.sol

## VRFV2WrapperConsumerBase.sol
This can stay the same. What is does is call a linktoken contract. I just have to make sure that the linktoken contract address I use in my tests when interacting with LotteryVRFDFM.sol is a deployed mock linktoken contract, and the VRFV2Wrapper contract address I use in these tests is that of a deployed mock VRFV2Wrapper contract. There shouldn't be any issue using the standard LinkTokenInterface.sol nor the standard VRFV2WrapperInterface.sol

This script defines LotteryVRFDFM.sol's requestRandomness call, a function that primarily calls LINK.transferAndCall(address(VRF_V2_WRAPPER), VRF_V2_WRAPPER.calculateRequestPrice(_callbackGasLimit), abi.encode(_callbackGasLimit, _requestConfirmations, _numWords)); where LINK is the provided LINKTOKEN contract accessed through the LinkTokenInterface.sol interface.

## MockLinkToken.sol
I have this set up under contracts/test. 

This script receives the transferAndCall call from LotteryVRFDFM.sol, does the transfers LINK to the VRF, then calls it's function contractFallback which in turn calls VRFV2Wrapper.onTokenTransfer(msg.sender, _value, _data)

## VRFV2WrapperMock.sol
This script's code can be (essentially) the same as the actual VRFV2Wrapper.sol, but just has to be locally deployed with the coordinator address being the address of the mock coordinator. The one change I make to the script is having the link-eth price being input at deployment as the first argument in place of the address to a pricefeed aggregator (which had been the second argument).

This script's onTokenTransfer will send VRFCoordinatorV2's requestRandomWords(s_keyHash, SUBSCRIPTION_ID, requestConfirmations, callbackGasLimit + eip150Overhead + s_wrapperGasOverhead, numWords);

## VRFCoordinatorV2Mock.sol
I have this set up under contracts/test

