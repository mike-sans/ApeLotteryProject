# In order to make a mock direct funding method pipeline, following are the things to do:

## Test deployment/interaction order
When in a local testing environment, first one must deploy (1) MockV3Aggregator, (2) MockLinkToken, (3) VRFCoordinatorV2Mock, then (4) VRFV2WrapperMock, in that order. Then, one can go ahead and deploy 

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
This script's code is (essentially) the same as the actual VRFV2Wrapper.sol, but just has to be locally deployed with the coordinator address being the address of the mock coordinator. The one change I make to the script is having the link-eth price being input at deployment as the first argument in place of the address to a pricefeed aggregator (which had been the second argument).

This script's onTokenTransfer will send VRFCoordinatorV2's requestRandomWords(s_keyHash, SUBSCRIPTION_ID, requestConfirmations, callbackGasLimit + eip150Overhead + s_wrapperGasOverhead, numWords);

## VRFCoordinatorV2Mock.sol
 //TODO

# Sample ape console execution code (currently functional on testnets!)
from scripts.helpfulScripts import *

account = get_account()

aggregatorContract = get_or_deploy_contract("AggregatorV3ETHUSD")

vrfCoordinatorContract = get_or_deploy_contract("VRFCoordinator")

linkTokenContract = get_or_deploy_contract("LinkToken")

vrfWrapperContract = get_or_deploy_contract("VRFV2Wrapper", CONTRACT_NAME_TO_DEFAULTS["VRFV2Wrapper"][0], linkTokenContract.address, vrfCoordinatorContract.address)

vrfWrapperContract.setConfig(*CONTRACT_NAME_TO_DEFAULTS["VRFV2Wrapper"][1:], sender = account[0])

lottery = project.LotteryVRFDFM.deploy(aggregatorContract.address, linkTokenContract.address, vrfWrapperContract.address, sender = account[0])

linkRequired = vrfWrapperContract.calculateRequestPrice(lottery.callbackGasLimit())

linkTokenContract.transfer(lottery.address, linkRequired, sender = account[0])

lottery.startLottery(sender = account[0])

for i in range(1,10):
    lottery.enter(sender = account[i], value = lottery.getEntranceFee()+100)

lottery.endLottery(sender = account[0])

import secrets

vrfCoordinatorContract.fundSubscription(1,25*10**18,sender = account[0])

vrfCoordinatorContract.fulfillRandomWordsWithOverride(lottery.lastRequestId(), vrfWrapperContract.address, [secrets.randbits(32),], sender = account[0])

winnerAddress = lottery.winner()

lottery.winnerWithdraw(sender = accounts[winnerAddress])



And then to check that the winner received funds: accounts[winnerAddress].balance > 10 ** 21 (or whatever your test accounts' default balances are)



