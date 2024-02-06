from ape import networks, accounts, project
from scripts.helpfulScripts import *

OPEN_STATE_MAPPING = {
    0: "CLOSED",
    1: "OPEN",
    2: "CALCULATING_WINNER",
    3: "PENDING_WINNER_WITHDRAW",
}


# This script deploys the lottery contract
def deploy_lottery(daccount=None):
    if not daccount:
        daccount = get_account()[0]
    if networks.active_provider.network.name in ("sepolia", "goerli", "mainnet"):
        daccount[0].set_autosign(True)

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

    if networks.active_provider.network.name in ("sepolia", "local"):
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
    return lottery


def start_lottery(oaccount=None, linkTransfer=True):
    oaccount = oaccount if oaccount else get_account()[0]
    # if not oaccount:
    #     oaccount = get_account()[0]

    lottery = project.LotteryVRFDFM.deployments[-1]
    vrfWrapperContract = get_or_deploy_contract("VRFV2Wrapper")
    linkTokenContract = get_or_deploy_contract("LinkToken")

    if linkTransfer:
        linkRequired = vrfWrapperContract.calculateRequestPrice(
            lottery.callbackGasLimit()
        )
        linkTokenContract.transfer(lottery.address, linkRequired, sender=oaccount)

    tx = lottery.startLottery(sender=oaccount)
    tx.await_confirmations()
    print(f"Contract entered, txn receipt:{tx}")
    return lottery.openStatus()


def enter_lottery(faccount=None, entrance_fee=None):
    faccount = faccount if faccount else get_account()[1]
    # if not faccount:
    #     faccount = get_account()[1]

    lottery = project.LotteryVRFDFM.deployments[-1]

    entrance_fee = entrance_fee if entrance_fee else lottery.getEntranceFee() + 100
    # if not entrance_fee:
    #     entrance_fee = lottery.getEntranceFee() + 100

    tx = lottery.enter(sender=faccount, value=entrance_fee)
    funderIndex = tx.return_value
    print(f"Contract entered, txn receipt:{tx}")
    return (funderIndex, lottery.players(funderIndex), entrance_fee)


def end_lottery(eaccount=False):
    eaccount = eaccount if eaccount else get_account()[1]
    # if not eaccount:
    #     eaccount = get_account()[0]
    lottery = project.LotteryVRFDFM.deployments[-1]
    # winner = lottery.endLottery(sender=eaccount)
    requestId = lottery.endLottery(sender=eaccount)
    print(f"Contract ended, txn receipt:{requestId.txn_hash}")

    # return winner.return_value
    return requestId.return_value


def get_lottery_status():
    lottery = project.LotteryVRFDFM.deployments[-1]
    status_value = lottery.openStatus()
    status_name = OPEN_STATE_MAPPING.get(status_value, "Unknown")
    if status_value == 2:
        winner = lottery.winner()
        return status_name, winner
    return status_name


def get_player_address(index):
    lottery = project.LotteryVRFDFM.deployments[-1]
    return lottery.players(index)


# TODO: need to implement winner withdraw
def withdraw_lottery(waccount=False):
    pass


def main():
    deploy_lottery()
