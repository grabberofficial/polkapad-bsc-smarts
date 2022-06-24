from brownie import accounts, config, Contract
from brownie.exceptions import VirtualMachineError
from scripts.deploy import *

import pytest

@pytest.fixture
def dot():
    return Contract.from_explorer(config["addresses"]["dot"])

@pytest.fixture
def whitelist():
    return deploy_whitelist()

@pytest.fixture
def locker(whitelist):
    return deploy_locker(whitelist)

@pytest.fixture
def plpd(locker):
    return deploy_plpd(locker)

@pytest.fixture
def multisig():
    return accounts[1]

@pytest.fixture
def sender():
    return accounts[2]

def test_lock_5_dots(dot, whitelist, locker, plpd, multisig, sender):
    owner = get_account()

    max_allocation_size = 60
    actual_allocation_size = 5
    plpd_sender_balance = int(actual_allocation_size * locker.getLatestPrice() / 10e7 * 3 / 10)

    locker.setPlpdContractAddress(plpd, { "from": owner })

    dot_account = accounts.at(config["addresses"]["dot_owner"], force=True)

    dot.mint(100, { "from": dot_account })
    dot.approve(sender, actual_allocation_size, { "from": dot_account })
    dot.transferFrom(dot_account, sender, actual_allocation_size, { "from": sender })

    dot.approve(locker, actual_allocation_size, { "from": sender })

    whitelist.add(sender, max_allocation_size, { "from": multisig })

    locker.lock(actual_allocation_size, { "from": sender })
    actual_amount = locker._locks(sender)
    actual_plpd_balance = plpd.balanceOf(sender)

    expected_amount = actual_allocation_size

    assert actual_amount == expected_amount
    print("BALANCE \n ", actual_plpd_balance)
    assert actual_plpd_balance == plpd_sender_balance

def test_lock_more_than_max_allocation_size(dot, whitelist, locker, plpd, multisig, sender):
    owner = get_account()

    max_allocation_size = 60
    actual_allocation_size = 61

    locker.setPlpdContractAddress(plpd, { "from": owner })
    dot_account = accounts.at(config["addresses"]["dot_owner"], force=True)
    dot.mint(100, { "from": dot_account })
    dot.approve(sender, actual_allocation_size, { "from": dot_account })
    dot.transferFrom(dot_account, sender, actual_allocation_size, { "from": sender })

    dot.approve(locker, actual_allocation_size, { "from": sender })

    whitelist.add(sender, max_allocation_size, { "from": multisig })

    with pytest.raises(VirtualMachineError):
        locker.lock(actual_allocation_size, { "from": sender })

def test_lock_when_sender_is_not_in_whitelist(dot, locker, plpd, sender):
    owner = get_account()

    actual_allocation_size = 5

    locker.setPlpdContractAddress(plpd, { "from": owner })

    dot_account = accounts.at(config["addresses"]["dot_owner"], force=True)

    dot.mint(100, { "from": dot_account })
    dot.approve(sender, actual_allocation_size, { "from": dot_account })
    dot.transferFrom(dot_account, sender, actual_allocation_size, { "from": sender })

    dot.approve(locker, actual_allocation_size, { "from": sender })

    with pytest.raises(VirtualMachineError):
        locker.lock(actual_allocation_size, { "from": sender })