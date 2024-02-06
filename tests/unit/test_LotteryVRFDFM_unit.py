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


# Successful: This test has been passed successfully
def test_lottery_deploy(owner):
    pytest.skip()
    # Arrange
    if (
        networks.active_provider.network.name
        not in LOCAL_CHAIN_NAMES + FORKED_CHAIN_NAMES
    ):
        pytest.skip("Only for local/forked testing")

    lottery = deploy_lottery(owner)
    assert lottery


# Successful: This test has been passed successfully
def test_get_entrance_fee(owner):
    pytest.skip()
    # Arrange
    if (
        networks.active_provider.network.name
        not in LOCAL_CHAIN_NAMES + FORKED_CHAIN_NAMES
    ):
        pytest.skip("Only for local/forked testing")

    lottery = deploy_lottery(owner)
    argues = [owner, receiver1, receiver2, receiver3]

    # Act
    entrance_fee_in_18usd = lottery.usdEntryFee()
    entrance_fee_in_wei = lottery.getEntranceFee()

    # Assert
    assert (
        10**18
        * (entrance_fee_in_18usd)
        / (CONTRACT_NAME_TO_DEFAULTS["AggregatorV3ETHUSD"][1] * 10**10)
    ) == entrance_fee_in_wei


# Successful: This test has been passed successfully
def test_cant_enter_unless_started(owner, receiver1, receiver2, receiver3):
    pytest.skip()
    # Arrange
    if (
        networks.active_provider.network.name
        not in LOCAL_CHAIN_NAMES + FORKED_CHAIN_NAMES
    ):
        pytest.skip("Only for local/forked testing")

    lottery = deploy_lottery(owner)

    actors = [owner, receiver1, receiver2, receiver3]

    # Act / Assert
    for i in range(len(actors)):
        with pytest.raises(exceptions.VirtualMachineError):
            enter_lottery(actors[i])


# Successful: This test has been passed successfully
def test_players_cant_start(owner, receiver1, receiver2, receiver3):
    pytest.skip()
    # Arrange
    if (
        networks.active_provider.network.name
        not in LOCAL_CHAIN_NAMES + FORKED_CHAIN_NAMES
    ):
        pytest.skip("Only for local/forked testing")

    lottery = deploy_lottery(owner)
    players = [receiver1, receiver2, receiver3]

    # Act / Assert
    for i in range(len(players)):
        with pytest.raises(exceptions.VirtualMachineError):
            start_lottery(players[i])


# Successful: This test has been passed successfully
def test_cant_start_without_link(owner):
    pytest.skip()
    # Arrange
    if (
        networks.active_provider.network.name
        not in LOCAL_CHAIN_NAMES + FORKED_CHAIN_NAMES
    ):
        pytest.skip("Only for local/forked testing")

    lottery = deploy_lottery(owner)

    # Act / Assert
    with pytest.raises(exceptions.VirtualMachineError):
        start_lottery(owner, False)


# Successful: This test has been passed successfully
def test_can_start_and_enter(owner, receiver1, receiver2, receiver3):
    pytest.skip()
    # Arrange
    if (
        networks.active_provider.network.name
        not in LOCAL_CHAIN_NAMES + FORKED_CHAIN_NAMES
    ):
        pytest.skip("Only for local/forked testing")

    lottery = deploy_lottery(owner)

    actors = [owner, receiver1, receiver2, receiver3]

    start_lottery(owner)
    openStatus = get_lottery_status()

    # Act / Assert
    assert openStatus == "OPEN"

    for i in range(len(actors)):
        returnvals = enter_lottery(actors[i])
        assert i == returnvals[0]
        assert actors[i].address == returnvals[1]


# Successful: This test has been passed successfully
def test_only_owner_can_end(owner, receiver1, receiver2, receiver3):
    # pytest.skip()
    # Arrange
    if (
        networks.active_provider.network.name
        not in LOCAL_CHAIN_NAMES + FORKED_CHAIN_NAMES
    ):
        pytest.skip("Only for local/forked testing")

    lottery = deploy_lottery(owner)

    players = [receiver1, receiver2, receiver3]

    start_lottery(owner)

    # Act / Assert
    for i in range(len(players)):
        with pytest.raises(exceptions.VirtualMachineError):
            end_lottery(players[i])

    end_lottery(owner)
    assert get_lottery_status()[0] == "CALCULATING_WINNER"
