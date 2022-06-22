from brownie import accounts, Locker
from scripts.deploy import *

def test_locking_5_dots():
    owner_account = get_account()
    multisig_account = accounts[1]
    sender_account = accounts[3]

    whitelist = deploy_whitelist()
    locker = deploy_locker(whitelist)
    plpd = deploy_plpd(locker)

    locker.setPlpdContractAddress(plpd, { "from": owner_account })

    whitelist.add(sender_account, 60, { "from": multisig_account })

    locker.lock(5, { "from": sender_account })
    actual = locker.locks(sender_account)[0] # amount

    expected = 5

    assert actual == expected