import pytest
from ape import accounts, project, networks, exceptions
from scripts.helpfulScripts import *
from scripts.LotteryCaRInteract import *

# from scripts.FundMeInteract import deploy_fund_me, fund_fund_me, withdraw_fund_me


@pytest.fixture
def owner():
    account = get_account()
    return account[0]


@pytest.fixture
def receiver():
    account = get_account()
    return account[1]


@pytest.fixture
def receiver2():
    account = get_account()
    return account[2]


def test_LotteryDeploy(owner):
    # account = get_account()
    # account = accounts[0]
    # an = networks.active_provider.network.name
    # print(account)

    if (
        networks.active_provider.network.name
        not in LOCAL_CHAIN_NAMES + FORKED_CHAIN_NAMES
    ):
        pytest.skip("Only for local/forked testing")

    # price_feed = get_or_deploy_contract("AggregatorV3Interface")
    # fundMe = project.FundMe.deploy(price_feed.address, sender=owner)
    fundMe = deploy_lottery(owner)
    assert fundMe


# // TODO
def test_LotteryOn(owner, receiver, receiver2):
    if (
        networks.active_provider.network.name
        not in LOCAL_CHAIN_NAMES + FORKED_CHAIN_NAMES
    ):
        pytest.skip("Only for local/forked testing")


# // TODO
# dependent on test_FundMeDeploy being run right before it
def test_LotteryFund(owner, receiver, receiver2):
    if (
        networks.active_provider.network.name
        not in LOCAL_CHAIN_NAMES + FORKED_CHAIN_NAMES
    ):
        pytest.skip("Only for local/forked testing")

    lottery = project.LotteryCaR.deployments[-1]


# // TODO
# dependent on test_FundMeDeploy being run right before it
def test_LotteryEnd(owner, receiver, receiver2):
    if (
        networks.active_provider.network.name
        not in LOCAL_CHAIN_NAMES + FORKED_CHAIN_NAMES
    ):
        pytest.skip("Only for local/forked testing")


# // TODO
# dependent on test_FundMeDeploy and test_FundMeFund being run right before it
def test_FundMeAuthWithdraw(owner, receiver, receiver2):
    if (
        networks.active_provider.network.name
        not in LOCAL_CHAIN_NAMES + FORKED_CHAIN_NAMES
    ):
        pytest.skip("Only for local/forked testing")
