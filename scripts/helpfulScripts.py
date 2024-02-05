from ape import networks, accounts, project, config, Contract

__all__ = [
    "get_account",
    "print18",
    "get_or_deploy_contract",
    "LOCAL_CHAIN_NAMES",
    "FORKED_CHAIN_NAMES",
    "CONTRACT_NAME_TO_DEFAULTS",
]

# All local chains across "ecosystems" have the same name
LOCAL_CHAIN_NAMES = ["local", "development"]
FORKED_CHAIN_NAMES = ["mainnet-fork"]

CONTRACT_NAME_TO_MOCK = {
    "AggregatorV3ETHUSD": project.MockV3Aggregator,
    "VRFCoordinator": project.VRFCoordinatorV2Mock,
    "LinkToken": project.MockLinkToken,
    "VRFV2Wrapper": project.VRFV2WrapperMock,
}


## Mock Contract Initial Values
# Default for Aggregator
DECIMALS = 8
INITIAL_VALUE = 2000_00000000  # 8 decimals, which is how chainlink gives it

# Default for VRFCoordinator
BASE_FEE = 1_00000000000000000  # 0.1
GAS_PRICE_LINK = 1_000000000  # Some value calculated depending on the Layer 1 cost and Link. This is 1e9

# Default for VRFV2Wrapper
LINK_ETH_PRICE = 771000_000000000  # (0.007710)
WRAPPER_GAS_OVERHEAD = 200000
COORDINATOR_GAS_OVERHEAD = 200000
WRAPPER_PREMIUM_PERCENTAGE = 20
KEY_HASH = "0x0"  # This variable is automatically converted to a Bytes32 type, but isn't used anyway
MAX_NUM_WORDS = 10

# Mock Default Values
CONTRACT_NAME_TO_DEFAULTS = {
    "AggregatorV3ETHUSD": [DECIMALS, INITIAL_VALUE],
    "VRFCoordinator": [BASE_FEE, GAS_PRICE_LINK],
    "LinkToken": [],
    "VRFV2Wrapper": [
        LINK_ETH_PRICE,
        WRAPPER_GAS_OVERHEAD,
        COORDINATOR_GAS_OVERHEAD,
        WRAPPER_PREMIUM_PERCENTAGE,
        KEY_HASH,
        MAX_NUM_WORDS,
    ],
}


def get_account():
    account = []
    if networks.active_provider.network.name in ("local", "mainnet-fork"):
        accountnum = 10
        for i in range(accountnum):
            account.append(accounts.test_accounts[i])
    else:
        account.append(accounts.load("myAccount"))
        account.append(accounts.load("real"))
        account.append(accounts.load("real2"))
        # etc.
    return account


# converts your integer that is 10**18 enlarged to be
def print18(returnInt):
    if type(returnInt) == int:
        print(returnInt / (10**18))
    else:
        print("Formatting did not work out")


def deploy_mocks(contract_name, *args):
    """
    Deploys mock contracts to a local network. Should take care to make sure you
    only call this function when running on a local network.
    """
    mock_contract_type = CONTRACT_NAME_TO_MOCK[contract_name]

    print(f"The active network is {networks.active_provider.network.name}")
    print(f"Deploying mock {contract_name} contract")
    account = get_account()

    mock_contract = account[0].deploy(mock_contract_type, *args)
    print(f"Deployed to {mock_contract.address}")
    print("Mock Deployed!")


def get_or_deploy_contract(contract_name, *args):
    """If you want to use this function, go to the ape config and add a new entry for
    the contract that you want to be able to 'get'. Then add an entry in the variable 'CONTRACT_NAME_TO_MOCK'.
    You'll see examples like the 'price_feed'.
        This script will then either:
            - Get a address from the config
            - Or deploy a mock to use for a network that doesn't have it

        Args:
            contract_name (name of ape.contracts.base.ContractContainer): This is the name that is referred to in the
            'CONTRACT_NAME_TO_MOCK' variable. It could be something like `project.AggregatorV3`. It takes
            a contract or deployment on a real chain, and gets the mock version of it.

        Returns:
            contract
    """
    if () == args:
        args = CONTRACT_NAME_TO_DEFAULTS[contract_name]

    mock_contract_type = CONTRACT_NAME_TO_MOCK[contract_name]
    if (
        networks.active_provider.network.name
        in LOCAL_CHAIN_NAMES
        # in [*LOCAL_CHAIN_NAMES, *FORKED_CHAIN_NAMES]
        # or networks.active_provider.chain_id == 31337
    ):
        if len(mock_contract_type.deployments) <= 0:
            deploy_mocks(contract_name, *args)
        contract = mock_contract_type.deployments[-1]
        # address = contract.address
    else:
        try:
            ecosystem = networks.active_provider.network.ecosystem.name
            chain_name = networks.active_provider.network.name
            # contract_addresses = [
            #     contract_and_address["address"]
            #     for contract_and_address in config.get_config("deployments").root[
            #         ecosystem
            #     ][chain_name]
            #     if contract_and_address["contract_type"] == contract_name
            # ]
            for deployedContracts in config.get_config("deployments").root[ecosystem][
                chain_name
            ]:
                if deployedContracts["contract_type"] == contract_name:
                    contract_address = deployedContracts["address"]
                    break
            contract = mock_contract_type.at(contract_address)
            print(f"Contract {contract_name} retrieved!")
            # address = contract_addresses[0]
            # address = contract_address

        except KeyError:
            raise Exception(
                f"{networks.active_provider.network.name} address not found, perhaps you should add it to the ape-config.yaml or CONTRACT_NAME_TO_MOCK in the helper_functions.py file?"
            )
    return contract
    # return address


def main():
    pass
