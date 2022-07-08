from brownie import accounts
from brownie.exceptions import VirtualMachineError
from utils.utils import get_contract_from_abi
from scripts.deploy import *

import pytest

@pytest.fixture
def whitelist():
    return deploy_whitelist()

@pytest.fixture
def locker(plpd, whitelist):
    return deploy_locker(plpd, whitelist)

@pytest.fixture
def dot():
    return get_contract_from_abi(
        "abi/dot.json", 
        "Polkadot", 
        "dot")

@pytest.fixture
def dot_feed():
    return get_contract_from_abi(
        "abi/dot_feed.json", 
        "Chainlink: DOT/USDT Price Feed", 
        "feed")

@pytest.fixture
def whitelist(owner, multisig):
    return deploy_whitelist(owner, multisig, 100 * 1e18)

@pytest.fixture
def locker(owner, multisig, burner, plpd, whitelist):
    return deploy_locker(owner, multisig, burner, plpd, whitelist)


@pytest.fixture
def plpd(owner, multisig):
    return deploy_plpd(owner, multisig)

@pytest.fixture
def owner():
    return accounts[0]

@pytest.fixture
def multisig():
    return accounts[1]

@pytest.fixture
def burner():
    return accounts[2]

@pytest.fixture
def sender():
    return accounts[3]

def test_added_to_whitelist(whitelist, multisig):
    participiant = accounts[2]

    whitelist.add(participiant, 50, { "from": multisig })

    actual_existing = whitelist.whitelist(participiant)
    expected_existing = True
    actual_allocation_size = whitelist.allocationSizes(participiant)
    expected_allocation_size = 50

    assert actual_existing == expected_existing
    assert actual_allocation_size == expected_allocation_size

def test_removed_to_whitelist(whitelist, multisig):
    participiant = accounts[2]

    whitelist.add(participiant, 50, { "from": multisig })

    exists = whitelist.whitelist(participiant)
    assert exists

    whitelist.remove(participiant, { "from": multisig })
    actual_existing = whitelist.whitelist(participiant)
    expected_existing = False
    actual_allocation_size = whitelist.allocationSizes(participiant)
    expected_allocation_size = 0

    assert actual_existing == expected_existing
    assert actual_allocation_size == expected_allocation_size

def test_change_allocation_size(whitelist, multisig):
    participiant = accounts[2]

    allocation_size = 150

    whitelist.add(participiant, allocation_size, { "from": multisig })

    actual_allocation_size = whitelist.allocationSizes(participiant)
    assert actual_allocation_size == allocation_size

    whitelist.changeAllocationSize(participiant, 160, { "from": multisig })
    actual_allocation_size = whitelist.allocationSizes(participiant)
    expected_allocation_size = 160

    assert actual_allocation_size == expected_allocation_size

def test_add_to_whitelist_from_not_multisig(whitelist):
    participiant = accounts[2]
    not_multisig = accounts[3]

    with pytest.raises(VirtualMachineError):
        whitelist.add(participiant, 50, { "from": not_multisig })

def test_remove_to_whitelist_from_not_multisig(whitelist, multisig):
    participiant = accounts[2]
    not_multisig = accounts[3]

    whitelist.add(participiant, 50, { "from": multisig })

    exists = whitelist.whitelist(participiant)
    assert exists

    with pytest.raises(VirtualMachineError):
        whitelist.remove(participiant, { "from": not_multisig })

def test_change_allocation_size_from_not_multisig(whitelist, multisig):
    participiant = accounts[2]
    not_multisig = accounts[3]

    whitelist.add(participiant, 50, { "from": multisig })

    exists = whitelist.whitelist(participiant)
    assert exists

    with pytest.raises(VirtualMachineError):
        whitelist.changeAllocationSize(participiant, 160, { "from": not_multisig })