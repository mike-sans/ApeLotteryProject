import pytest
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


@pytest.fixture
def receiver3():
    account = get_account()
    return account[3]


# Successful: This test has been passed successfully on local networks
def test_lottery_deploy(owner):
    pytest.skip()
    # Arrange
    if (
        networks.active_provider.network.name
        not in LOCAL_CHAIN_NAMES + FORKED_CHAIN_NAMES
    ):
        pytest.skip("Only for local/forked testing")

    contractList = deploy_lottery(owner)
    lottery = contractList[0]
    assert lottery


# Successful: This test has been passed successfully on local networks
def test_get_entrance_fee(owner):
    pytest.skip()
    # Arrange
    if (
        networks.active_provider.network.name
        not in LOCAL_CHAIN_NAMES + FORKED_CHAIN_NAMES
    ):
        pytest.skip("Only for local/forked testing")

    deploy_lottery(owner)
    argues = [owner, receiver1, receiver2, receiver3]

    # Act
    # entrance_fee_in_18usd = lottery.usdEntryFee()
    # entrance_fee_in_wei = lottery.getEntranceFee()
    entrance_fees = get_entrance_fee()

    # Assert
    assert (
        10**18
        * (entrance_fees[1])
        / (CONTRACT_NAME_TO_DEFAULTS["AggregatorV3ETHUSD"][1] * 10**10)
    ) == entrance_fees[0]


# Successful: This test has been passed successfully on local networks
def test_cant_enter_unless_started(owner, receiver1, receiver2, receiver3):
    pytest.skip()
    # Arrange
    if (
        networks.active_provider.network.name
        not in LOCAL_CHAIN_NAMES + FORKED_CHAIN_NAMES
    ):
        pytest.skip("Only for local/forked testing")

    deploy_lottery(owner)

    actors = [owner, receiver1, receiver2, receiver3]

    # Act / Assert
    for i in range(len(actors)):
        with pytest.raises(exceptions.VirtualMachineError):
            enter_lottery(actors[i])


# Successful: This test has been passed successfully on local networks
def test_players_cant_start(owner, receiver1, receiver2, receiver3):
    pytest.skip()
    # Arrange
    if (
        networks.active_provider.network.name
        not in LOCAL_CHAIN_NAMES + FORKED_CHAIN_NAMES
    ):
        pytest.skip("Only for local/forked testing")

    deploy_lottery(owner)
    players = [receiver1, receiver2, receiver3]

    # Act / Assert
    for i in range(len(players)):
        with pytest.raises(exceptions.VirtualMachineError):
            start_lottery(players[i])


# Successful: This test has been passed successfully on local networks
def test_cant_start_without_link(owner):
    pytest.skip()
    # Arrange
    if (
        networks.active_provider.network.name
        not in LOCAL_CHAIN_NAMES + FORKED_CHAIN_NAMES
    ):
        pytest.skip("Only for local/forked testing")

    deploy_lottery(owner)

    # Act / Assert
    with pytest.raises(exceptions.VirtualMachineError):
        start_lottery(owner, False)


# Successful: This test has been passed successfully on local networks
def test_can_start_and_enter(owner, receiver1, receiver2, receiver3):
    pytest.skip()
    # Arrange
    if (
        networks.active_provider.network.name
        not in LOCAL_CHAIN_NAMES + FORKED_CHAIN_NAMES
    ):
        pytest.skip("Only for local/forked testing")

    deploy_lottery(owner)

    actors = [owner, receiver1, receiver2, receiver3]

    start_lottery(owner)
    openStatus = get_lottery_status()

    # Act / Assert
    assert openStatus == "OPEN"

    for i in range(len(actors)):
        tx = enter_lottery(actors[i])
        # assert i == returnvals[0].return_value
        # assert i == tx.return_value
        assert i == get_player_amount() - 1
        # resultAddress = get_player_address(tx.return_value)
        # assert actors[i].address == tx[1]
        # assert actors[i].address == get_player_address(tx.return_value)
        assert actors[i].address == get_player_address(get_player_amount() - 1)


# Successful: This test has been passed successfully on local networks
def test_only_owner_can_end(owner, receiver1, receiver2, receiver3):
    pytest.skip()
    # Arrange
    if (
        networks.active_provider.network.name
        not in LOCAL_CHAIN_NAMES + FORKED_CHAIN_NAMES
    ):
        pytest.skip("Only for local/forked testing")

    contractList = deploy_lottery(owner)
    lottery = contractList[0]
    vrfCoordinatorContract = contractList[2]

    players = [receiver1, receiver2, receiver3]

    start_lottery(owner)

    # Act / Assert
    for i in range(len(players)):
        with pytest.raises(exceptions.VirtualMachineError):
            end_lottery(players[i])

    tx = end_lottery(owner)
    assert get_lottery_status()[0] == "CALCULATING_WINNER"

    # testing that the randomness request was indeed sent
    assert (
        vrfCoordinatorContract.RandomWordsRequested.from_receipt(tx)[-1].requestId,
        vrfCoordinatorContract.RandomWordsRequested.from_receipt(tx)[-1].numWords,
    ) == (get_last_request_id(), get_num_words())
    assert (
        lottery.RequestSent.from_receipt(tx)[-1].requestId,
        lottery.RequestSent.from_receipt(tx)[-1].numWords,
    ) == (get_last_request_id(), get_num_words())


# Successful: This test has been passed successfully on local networks
def test_can_reward_winner_and_only_winner(owner, receiver1, receiver2, receiver3):
    pytest.skip()
    # Arrange
    if (
        networks.active_provider.network.name
        not in LOCAL_CHAIN_NAMES + FORKED_CHAIN_NAMES
    ):
        pytest.skip("Only for local/forked testing")

    contractList = deploy_lottery(owner)
    lottery = contractList[0]
    players = [receiver1, receiver2, receiver3]
    start_lottery(owner)

    for i in range(len(players)):
        enter_lottery(players[i])

    end_lottery(owner)
    tx = fulfill_randomness(owner)
    # testing that the random words were in fact fulfilled
    assert (
        lottery.RequestFulfilled.from_receipt(tx)[-1].requestId == get_last_request_id()
    )
    assert lottery.RequestFulfilled.from_receipt(tx)[-1].randomWords[0] >= 0
    winnerIndex = (
        lottery.RequestFulfilled.from_receipt(tx)[-1].randomWords[0]
        % get_player_amount()
    )

    openStatus, winnerAddress = get_lottery_status()
    assert openStatus == "PENDING_WINNER_WITHDRAW"
    assert winnerAddress == players[winnerIndex].address
    winnerAccount = [player for player in players if player.address == winnerAddress][0]
    nonWinners = [x for x in players if x != winnerAccount] + [owner]

    for nW in nonWinners:
        with pytest.raises(exceptions.VirtualMachineError):
            winner_withdraw(nW)

    balanceBefore = winnerAccount.balance
    winner_withdraw(winnerAccount)
    balanceChange = winnerAccount.balance - balanceBefore
    assert balanceChange > get_entrance_fee()[0] * (get_player_amount()) * 0.999
    assert balanceChange < get_entrance_fee()[0] * (get_player_amount())
    openStatus = get_lottery_status()[0]
    assert openStatus == "CLOSED"
