from brownie import accounts, reverts, config, Contract
from brownie.exceptions import VirtualMachineError
from scripts.deploy import *

import pytest

@pytest.fixture
def whitelist():
    return deploy_whitelist()

@pytest.fixture
def locker(plpd, whitelist):
    return deploy_locker(plpd, whitelist)

@pytest.fixture
def plpd():
    return deploy_plpd(accounts[1])

@pytest.fixture
def multisig():
    return accounts[1]

@pytest.fixture
def sender():
    return accounts[2]

def test_revert_transfer(plpd, sender):
    amount = 100

    with reverts():
        plpd.transfer(sender, amount)

def test_revert_transferFrom(plpd, sender):
    amount = 100
    from_ = accounts[3]

    with reverts():
        plpd.transferFrom(from_, sender, amount)

def test_mint(plpd, sender, locker, multisig):
    amount = 100
    plpd.setLockerContractAddress(locker, { "from": multisig })

    plpd.mint(sender, amount, { "from": locker })
    actual_balance = plpd.balanceOf(sender)

    assert actual_balance == amount

def test_mint_from_not_locker_address(plpd, sender, locker, multisig):
    amount = 100
    not_locker = accounts[3]
    plpd.setLockerContractAddress(locker, { "from": multisig })

    with pytest.raises(VirtualMachineError):
        plpd.mint(sender, amount, { "from": not_locker })

def test_burn(plpd, sender, locker, multisig):
    amount = 100
    plpd.setLockerContractAddress(locker, { "from": multisig })

    plpd.mint(sender, amount, { "from": locker })
    actual_balance = plpd.balanceOf(sender)
    assert actual_balance == amount

    plpd.burn(sender, amount, { "from": locker })
    actual_balance = plpd.balanceOf(sender)
    expected_balance = 0

    assert actual_balance == expected_balance

def test_burn_from_not_locker_address(plpd, sender, locker, multisig):
    amount = 100
    not_locker = accounts[3]
    plpd.setLockerContractAddress(locker, { "from": multisig })

    plpd.mint(sender, amount, { "from": locker })
    actual_balance = plpd.balanceOf(sender)
    assert actual_balance == amount

    with pytest.raises(VirtualMachineError):
        plpd.burn(sender, amount, { "from": not_locker })


def test_set_locker_address(plpd, locker, multisig):
    plpd.setLockerContractAddress(locker, { "from": multisig })

    actual_locker_address = plpd._locker()
    expected_locker_address = locker

    assert actual_locker_address == expected_locker_address

def test_set_locker_address_from_not_multisig(plpd, locker):
    not_multisig = accounts[3]

    with pytest.raises(VirtualMachineError):
        plpd.setLockerContractAddress(locker, { "from": not_multisig })