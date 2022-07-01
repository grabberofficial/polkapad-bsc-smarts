from brownie import accounts
from brownie.exceptions import VirtualMachineError
from scripts.deploy import deploy_whitelist

import pytest

@pytest.fixture
def whitelist():
    return deploy_whitelist()

@pytest.fixture
def multisig():
    return accounts[1]

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