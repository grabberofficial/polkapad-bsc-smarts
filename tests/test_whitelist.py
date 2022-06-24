from brownie import accounts
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

    actual = whitelist.isWhitelisted(participiant)
    expected = True

    assert actual == expected