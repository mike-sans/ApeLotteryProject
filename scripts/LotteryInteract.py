from ape import networks, accounts, project
from scripts.helpfulScripts import *

OPEN_STATE_MAPPING = {0: "OPEN", 1: "CLOSED", 2: "PENDING_WINNER_WITHDRAW"}


def deploy_lottery(daccount=False):
    if not daccount:
        daccount = get_account()[0]
    if networks.active_provider.network.name in ("sepolia", "goerli"):
        daccount[0].set_autosign(True)

    # this will get info from chainlink or deploy a mock chain if in a test network
    price_feed = get_or_deploy_contract("AggregatorV3Interface")
    publishStat = True
    if networks.active_provider.network.name in ("local", "mainnet-fork"):
        publishStat = False
    lottery = project.Lottery.deploy(
        price_feed.address, sender=daccount, publish=publishStat
    )
    print(f"Contract deployed to {lottery.address}")
    return lottery


def open_lottery(oaccount=False):
    if not oaccount:
        oaccount = get_account()[0]

    lottery = project.Lottery.deployments[-1]
    tx = lottery.startLottery(sender=oaccount)
    tx.await_confirmations()
    print(f"Contract entered, txn receipt:{tx}")
    return lottery.openStatus()


# // TODO: need to implement commit
def enter_lottery(faccount=False, entrance_fee=False):
    if not faccount:
        faccount = get_account()[1]
    lottery = project.Lottery.deployments[-1]
    if not entrance_fee:
        entrance_fee = lottery.getEntranceFee() + 100
    tx = lottery.enter(sender=faccount, value=entrance_fee)
    print(f"Contract entered, txn receipt:{tx}")
    return (entrance_fee, lottery.addressToAmountFunded(faccount))


def get_lottery_status():
    lottery = project.Lottery.deployments[-1]
    status_value = lottery.openStatus()
    status_name = OPEN_STATE_MAPPING.get(status_value, "Unknown")
    if status_value == 2:
        winner = lottery.winner()
    try:
        winner
    except:
        return status_name
    return status_name, winner


def end_lottery(eaccount=False):
    if not eaccount:
        eaccount = get_account()[0]
    lottery = project.Lottery.deployments[-1]
    winner = lottery.endLottery(sender=eaccount)
    print(f"Contract withdrawn from, txn receipt:{winner.txn_hash}")
    return winner.return_value


# // TODO: need to implement reveal
def reveal_lottery(waccount=False):
    pass


# // TODO: need to implement winner withdraw
def withdraw_lottery(waccount=False):
    pass


def main():
    deploy_lottery()
