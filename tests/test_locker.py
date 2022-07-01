from brownie import accounts, config, Contract
from brownie.exceptions import VirtualMachineError
from scripts.deploy import *

import pytest
import json

@pytest.fixture
def dot():
    return _get_contract_from_abi(
        "abi/dot.json", 
        "Polkadot", 
        "dot")

@pytest.fixture
def dot_feed():
    return _get_contract_from_abi(
        "abi/dot_feed.json", 
        "Chainlink: DOT/USDT Price Feed", 
        "feed")

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

def test_lock_5_dots(dot, dot_feed, whitelist, locker, plpd, multisig, sender):
    max_allocation_size = 60 * pow(10, dot_feed.decimals())
    actual_allocation_size = 5

    plpd.setLockerContractAddress(locker, { "from": multisig })

    dot_account = accounts.at(config["addresses"]["dot_owner"], force=True)

    dot.mint(100, { "from": dot_account })
    dot.approve(sender, actual_allocation_size, { "from": dot_account })
    dot.transferFrom(dot_account, sender, actual_allocation_size, { "from": sender })

    dot.approve(locker, actual_allocation_size, { "from": sender })

    whitelist.add(sender, max_allocation_size, { "from": multisig })

    locker.lock(actual_allocation_size, { "from": sender })
    actual_amount = locker._locks(sender)
    actual_plpd_balance = plpd.balanceOf(sender)
    plpd_sender_balance = 5 * locker.getLatestPrice() * 3 / 10

    expected_amount = actual_allocation_size

    assert actual_amount == expected_amount
    assert actual_plpd_balance == plpd_sender_balance

def test_lock_more_than_max_allocation_size(dot, dot_feed, whitelist, locker, plpd, multisig, sender):
    max_allocation_size = 60 * pow(10, dot_feed.decimals())
    actual_allocation_size = 61

    plpd.setLockerContractAddress(locker, { "from": multisig })
    dot_account = accounts.at(config["addresses"]["dot_owner"], force=True)
    dot.mint(100, { "from": dot_account })
    dot.approve(sender, actual_allocation_size, { "from": dot_account })
    dot.transferFrom(dot_account, sender, actual_allocation_size, { "from": sender })

    dot.approve(locker, actual_allocation_size, { "from": sender })

    whitelist.add(sender, max_allocation_size, { "from": multisig })

    with pytest.raises(VirtualMachineError):
        locker.lock(actual_allocation_size, { "from": sender })

def test_lock_when_sender_is_not_in_whitelist(dot, locker, plpd, sender, multisig):
    actual_allocation_size = 5

    plpd.setLockerContractAddress(locker, { "from": multisig })

    dot_account = accounts.at(config["addresses"]["dot_owner"], force=True)

    dot.mint(100, { "from": dot_account })
    dot.approve(sender, actual_allocation_size, { "from": dot_account })
    dot.transferFrom(dot_account, sender, actual_allocation_size, { "from": sender })

    dot.approve(locker, actual_allocation_size, { "from": sender })

    with pytest.raises(VirtualMachineError):
        locker.lock(actual_allocation_size, { "from": sender })

def test_lock_more_than_dots_on_account(dot, dot_feed, whitelist, locker, plpd, multisig, sender):
    max_allocation_size = 200 * pow(10, dot_feed.decimals())
    actual_allocation_size = 5
    actual_dots_amount = 1

    plpd.setLockerContractAddress(locker, { "from": multisig })
    dot_account = accounts.at(config["addresses"]["dot_owner"], force=True)
    dot.mint(actual_dots_amount, { "from": dot_account })
    dot.approve(sender, actual_dots_amount, { "from": dot_account })
    dot.transferFrom(dot_account, sender, actual_dots_amount, { "from": sender })

    dot.approve(locker, actual_dots_amount, { "from": sender })

    whitelist.add(sender, max_allocation_size, { "from": multisig })

    with pytest.raises(VirtualMachineError):
        locker.lock(actual_allocation_size, { "from": sender })

def _get_contract_from_abi(path, name, address):
    with open(path, "r") as file:
        abi = json.load(file)
        return Contract.from_abi(name, config["addresses"][address], abi)