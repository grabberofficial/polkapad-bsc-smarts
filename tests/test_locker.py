from brownie import accounts, config
from brownie.exceptions import VirtualMachineError
from utils.utils import get_contract_from_abi
from scripts.deploy import *

import pytest

@pytest.fixture
def dot():
    return get_contract_from_abi(
        "abi/dot.json", 
        "Polkadot", 
        "dot")

@pytest.fixture
def whitelist(deployer, multisig):
    return deploy_whitelist(deployer, multisig, 100 * 1e18)

@pytest.fixture
def locker(deployer, multisig, burner, plpd, whitelist):
    return deploy_locker(deployer, multisig, burner, plpd, whitelist)

@pytest.fixture
def plpd(deployer, multisig):
    return deploy_plpd(deployer, multisig)

@pytest.fixture
def deployer():
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

def test_lock_5_dots(dot, whitelist, locker, plpd, multisig, sender):
    max_allocation_size = 60 * 1e18
    actual_allocation_size = 5 * 1e18

    plpd.setLockerContractAddress(locker, { "from": multisig })

    dot_account = accounts.at(config["addresses"]["dot_owner"], force=True)

    dot.mint(100 * 1e18, { "from": dot_account })
    dot.approve(sender, actual_allocation_size, { "from": dot_account })
    dot.transferFrom(dot_account, sender, actual_allocation_size, { "from": sender })

    dot.approve(locker, actual_allocation_size, { "from": sender })

    whitelist.add(sender, max_allocation_size, { "from": multisig })

    locker.lock(actual_allocation_size, { "from": sender })
    actual_amount = locker._locks(sender)

    expected_amount = actual_allocation_size

    assert actual_amount == expected_amount

def test_lock_more_than_max_allocation_size(dot, whitelist, locker, plpd, multisig, sender):
    max_allocation_size = 60 * 1e18
    actual_allocation_size = 61 * 1e18

    plpd.setLockerContractAddress(locker, { "from": multisig })
    dot_account = accounts.at(config["addresses"]["dot_owner"], force=True)
    dot.mint(100 * 1e18, { "from": dot_account })
    dot.approve(sender, actual_allocation_size, { "from": dot_account })
    dot.transferFrom(dot_account, sender, actual_allocation_size, { "from": sender })

    dot.approve(locker, actual_allocation_size, { "from": sender })

    whitelist.add(sender, max_allocation_size, { "from": multisig })

    with pytest.raises(VirtualMachineError):
        locker.lock(actual_allocation_size, { "from": sender })

def test_lock_when_sender_is_not_in_whitelist(dot, locker, plpd, sender, multisig):
    actual_allocation_size = 5 * 1e18

    plpd.setLockerContractAddress(locker, { "from": multisig })

    dot_account = accounts.at(config["addresses"]["dot_owner"], force=True)

    dot.mint(100 * 1e18, { "from": dot_account })
    dot.approve(sender, actual_allocation_size, { "from": dot_account })
    dot.transferFrom(dot_account, sender, actual_allocation_size, { "from": sender })

    dot.approve(locker, actual_allocation_size, { "from": sender })

    with pytest.raises(VirtualMachineError):
        locker.lock(actual_allocation_size, { "from": sender })

def test_lock_more_than_dots_on_account(dot, whitelist, locker, plpd, multisig, sender):
    max_allocation_size = 200 * 1e18
    actual_allocation_size = 5 * 1e18
    actual_dots_amount = 1 * 1e18

    plpd.setLockerContractAddress(locker, { "from": multisig })
    dot_account = accounts.at(config["addresses"]["dot_owner"], force=True)
    dot.mint(actual_dots_amount, { "from": dot_account })
    dot.approve(sender, actual_dots_amount, { "from": dot_account })
    dot.transferFrom(dot_account, sender, actual_dots_amount, { "from": sender })

    dot.approve(locker, actual_dots_amount, { "from": sender })

    whitelist.add(sender, max_allocation_size, { "from": multisig })

    with pytest.raises(VirtualMachineError):
        locker.lock(actual_allocation_size, { "from": sender })

def test_lock_when_canBurn_false(dot, whitelist, locker, plpd, multisig, sender):
    max_allocation_size = 60 * 1e18
    actual_allocation_size = 5 * 1e18

    plpd.setLockerContractAddress(locker, { "from": multisig })

    dot_account = accounts.at(config["addresses"]["dot_owner"], force=True)

    dot.mint(100 * 1e18, { "from": dot_account })
    dot.approve(sender, actual_allocation_size, { "from": dot_account })
    dot.transferFrom(dot_account, sender, actual_allocation_size, { "from": sender })

    dot.approve(locker, actual_allocation_size, { "from": sender })

    whitelist.add(sender, max_allocation_size, { "from": multisig })
    
    locker.activateBurning({ "from": multisig })

    with pytest.raises(VirtualMachineError):
        locker.lock(actual_allocation_size, { "from": sender })

def test_burn_when_canBurn_false(locker, burner):
    with pytest.raises(VirtualMachineError):
        locker.burnPlpd([], { "from": burner })

def test_burn_when_canBurn_true(dot, whitelist, plpd, locker, burner, multisig, sender):
    max_allocation_size = 60 * 1e18
    actual_allocation_size = 5 * 1e18

    plpd.setLockerContractAddress(locker, { "from": multisig })

    dot_account = accounts.at(config["addresses"]["dot_owner"], force=True)

    dot.mint(100 * 1e18, { "from": dot_account })
    dot.approve(sender, actual_allocation_size, { "from": dot_account })
    dot.transferFrom(dot_account, sender, actual_allocation_size, { "from": sender })

    dot.approve(locker, actual_allocation_size, { "from": sender })

    whitelist.add(sender, max_allocation_size, { "from": multisig })

    locker.lock(actual_allocation_size, { "from": sender })
    actual_amount = locker._locks(sender)
    
    assert actual_allocation_size == actual_amount

    locker.activateBurning({ "from": multisig })
    locker.burnPlpd([sender], { "from": burner })

    actual_plpd_balance = plpd.balanceOf(sender)
    expected_plpd_balance = 0

    assert actual_plpd_balance == expected_plpd_balance