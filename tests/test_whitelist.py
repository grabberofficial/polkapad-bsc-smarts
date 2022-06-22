from brownie import accounts
from scripts.deploy import deploy_whitelist

def test_added_to_whitelist():
    contract = deploy_whitelist()
    multisig_account = accounts[1]

    participiant = accounts[2]

    contract.add(participiant, 50, { "from": multisig_account })

    actual = contract.participants(participiant)
    expected = (True, 50)

    assert expected == actual