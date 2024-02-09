import pytest
import time
from ape import accounts, project, networks, exceptions
from scripts.helpfulScripts import *
from scripts.LotteryVRFDFMInteract import *


@pytest.fixture
def owner():
    account = get_account()
    return account[0]


@pytest.fixture
def receiver1():
    account = get_account()
    return account[1]


@pytest.fixture
def receiver2():
    account = get_account()
    return account[2]


# @pytest.fixture
# def receiver3():
#     account = get_account()
#     return account[3]


# Successful: This test has been passed successfully on Sepolia
def test_integrated(owner, receiver1, receiver2):
    # pytest.skip()
    # Arrange
    # if networks.active_provider.network.name in LOCAL_CHAIN_NAMES:
    # pytest.skip("Only for local/forked testing")

    deploy_lottery(owner)
    # contractList = deploy_lottery(owner)
    # lottery = contractList[0]
    # argues = [owner, receiver1, receiver2]
    players = [receiver1, receiver2]

    start_lottery(owner)

    for i in range(len(players)):
        enter_lottery(players[i])

    end_lottery(owner)
    # tx = fulfill_randomness(owner)

    time.sleep(60)

    # winnerIndex = (
    #     lottery.RequestFulfilled.from_receipt(tx)[-1].randomWords[0]
    #     % get_player_amount()
    # )

    openStatus, winnerAddress = get_lottery_status()
    assert openStatus == "PENDING_WINNER_WITHDRAW"
    # assert winnerAddress == players[winnerIndex].address
    winnerAccount = [player for player in players if player.address == winnerAddress][0]
    # nonWinners = [x for x in players if x != winnerAccount] + [owner]

    # for nW in nonWinners:
    #     with pytest.raises(exceptions.VirtualMachineError):
    #         winner_withdraw(nW)

    balanceBefore = winnerAccount.balance
    winner_withdraw(winnerAccount)
    balanceChange = winnerAccount.balance - balanceBefore
    assert balanceChange > get_entrance_fee()[0] * (get_player_amount()) * 0.96
    assert balanceChange < get_entrance_fee()[0] * (get_player_amount())
    openStatus = get_lottery_status()[0]
    assert openStatus == "CLOSED"
    owner_withdraw_link(owner)
