import secrets
from ape import networks, accounts, project
from scripts.helpfulScripts import *

OPEN_STATE_MAPPING = {
    0: "CLOSED",
    1: "OPEN",
    2: "CALCULATING_WINNER",
    3: "PENDING_WINNER_WITHDRAW",
}


# This script deploys the lottery contract
def deploy_lottery(daccount=False):
    daccount = daccount if daccount else get_account()[0]
    # if not daccount:
    #     daccount = get_account()[0]
    if networks.active_provider.network.name in ("sepolia", "goerli"):
        daccount.set_autosign(True)

    # this will get info from chainlink or deploy a mock chain if in a test network
    aggregatorContract = get_or_deploy_contract("AggregatorV3ETHUSD")
    vrfCoordinatorContract = get_or_deploy_contract("VRFCoordinator")
    linkTokenContract = get_or_deploy_contract("LinkToken")
    vrfWrapperContract = get_or_deploy_contract(
        "VRFV2Wrapper",
        CONTRACT_NAME_TO_DEFAULTS["VRFV2Wrapper"][0],
        linkTokenContract.address,
        vrfCoordinatorContract.address,
    )

    if networks.active_provider.network.name in ("local"):
        vrfWrapperContract.setConfig(
            *CONTRACT_NAME_TO_DEFAULTS["VRFV2Wrapper"][1:], sender=daccount
        )

    publishStat = True
    if networks.active_provider.network.name in ("local", "mainnet-fork"):
        publishStat = False
    lottery = project.LotteryVRFDFM.deploy(
        aggregatorContract.address,
        linkTokenContract.address,
        vrfWrapperContract.address,
        sender=daccount,
        publish=publishStat,
    )

    print(f"Contract deployed to {lottery.address}")
    # return contract api's
    return (
        lottery,
        aggregatorContract,
        vrfCoordinatorContract,
        linkTokenContract,
        vrfWrapperContract,
    )


def start_lottery(oaccount=False, linkTransfer=True):
    oaccount = oaccount if oaccount else get_account()[0]
    # if not oaccount:
    #     oaccount = get_account()[0]

    lottery = project.LotteryVRFDFM.deployments[-1]
    vrfWrapperContract = get_or_deploy_contract("VRFV2Wrapper")
    linkTokenContract = get_or_deploy_contract("LinkToken")

    if linkTransfer:
        # linkRequired = vrfWrapperContract.calculateRequestPrice(
        #     lottery.callbackGasLimit()
        # )
        linkRequired = lottery.linkNeeded()
        tx = linkTokenContract.transfer(lottery.address, linkRequired, sender=oaccount)
        tx.await_confirmations()

    tx = lottery.startLottery(sender=oaccount)
    # tx = lottery.enoughLink2(sender=oaccount)
    # print("hello hello hello")
    # print(tx.return_value)
    # tx.await_confirmations()
    print(f"Contract entered, txn receipt:{tx}")
    # return lottery.openStatus()
    return tx


def enter_lottery(faccount=False, entrance_fee=None):
    faccount = faccount if faccount else get_account()[1]
    # if not faccount:
    #     faccount = get_account()[1]

    lottery = project.LotteryVRFDFM.deployments[-1]

    entrance_fee = entrance_fee if entrance_fee else lottery.getEntranceFee() + 100
    # if not entrance_fee:
    #     entrance_fee = lottery.getEntranceFee() + 100

    tx = lottery.enter(sender=faccount, value=entrance_fee)
    # funderIndex = tx.return_value
    print(f"Contract entered, txn receipt:{tx}")
    return tx
    # return (tx, lottery.players(tx.return_value))


def end_lottery(eaccount=False):
    eaccount = eaccount if eaccount else get_account()[0]
    # if not eaccount:
    #     eaccount = get_account()[0]
    lottery = project.LotteryVRFDFM.deployments[-1]
    # winner = lottery.endLottery(sender=eaccount)
    tx = lottery.endLottery(sender=eaccount)
    tx.await_confirmations()
    print(f"Contract ended, txn receipt:{tx.txn_hash}")

    # return winner.return_value
    # return requestId.return_value
    return tx


def fulfill_randomness(account=False):
    if networks.active_provider.network.name not in ("local"):
        raise Exception("Can only fulfill randomness on a test network")
    account = account if account else get_account()[0]

    lottery = project.LotteryVRFDFM.deployments[-1]
    vrfWrapperContract = get_or_deploy_contract("VRFV2Wrapper")
    vrfCoordinatorContract = get_or_deploy_contract("VRFCoordinator")
    vrfCoordinatorContract.fundSubscription(1, 25 * 10**18, sender=account)
    tx = vrfCoordinatorContract.fulfillRandomWordsWithOverride(
        lottery.lastRequestId(),
        vrfWrapperContract.address,
        [
            secrets.randbits(32),
        ],
        sender=account,
    )
    return tx


def winner_withdraw(account=False):
    account = account if account else get_account()[0]
    lottery = project.LotteryVRFDFM.deployments[-1]
    tx = lottery.winnerWithdraw(sender=account)
    return tx


def owner_withdraw_link(account=False):
    account = account if account else get_account()[0]
    lottery = project.LotteryVRFDFM.deployments[-1]
    tx = lottery.withdrawLink(sender=account)
    return tx


def get_lottery_status():
    lottery = project.LotteryVRFDFM.deployments[-1]
    status_value = lottery.openStatus()
    status_name = OPEN_STATE_MAPPING.get(status_value, "Unknown")
    if status_value in (0, 3):
        winner = lottery.winner()
        return status_name, winner
    return status_name


def get_player_address(index):
    lottery = project.LotteryVRFDFM.deployments[-1]
    returnVal = lottery.players(index)
    return returnVal


def get_player_amount():
    lottery = project.LotteryVRFDFM.deployments[-1]
    returnVal = lottery.getPlayerAmount()
    return returnVal


def get_entrance_fee():
    lottery = project.LotteryVRFDFM.deployments[-1]
    returnVal1 = lottery.getEntranceFee()
    returnVal2 = lottery.usdEntryFee()
    return (returnVal1, returnVal2)


def get_num_words():
    lottery = project.LotteryVRFDFM.deployments[-1]
    returnVal = lottery.numWords()
    return returnVal


def get_last_request_id():
    lottery = project.LotteryVRFDFM.deployments[-1]
    returnVal = lottery.lastRequestId()
    return returnVal


# TODO: need to implement winner withdraw
def withdraw_lottery(waccount=False):
    pass


def main():
    deploy_lottery()
