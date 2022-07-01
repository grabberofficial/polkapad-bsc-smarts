from brownie import accounts, network, config, Locker, PolkapadERC20, Whitelist

def deploy_whitelist():
    owner_account = get_account()
    multisig_account = accounts[1]
    default_max_allocation_size = 100 * 10e7

    contract = Whitelist.deploy(
        multisig_account, 
        default_max_allocation_size, 
        { "from": owner_account })

    return contract

def deploy_plpd(multisig_account):
    owner_account = get_account()

    contract = PolkapadERC20.deploy(
    "Polkapad", 
    "PLPD", 
    multisig_account, 
    { "from": owner_account })

    return contract

def deploy_locker(polkapad_contract, whitelist_contract):
    owner_account = get_account()
    multisig_account = accounts[1]


    contract = Locker.deploy(
        multisig_account,
        config["addresses"]["dot"], 
        config["addresses"]["feed"],
        polkapad_contract,
        whitelist_contract,
        { "from": owner_account })

    return contract

def get_account(): 
    if network.show_active() == "development":
        return accounts[0]
    else:
        return accounts.add(config["addresses"]["private_key"])

def main():
    print("Deploying is started...")

    multisig_account = accounts[1]

    whitelist = deploy_whitelist()
    plpd = deploy_plpd(multisig_account)
    locker = deploy_locker(plpd, whitelist)

    plpd.setLockerContractAddress(locker, { "from": multisig_account })

    print("Contracts has deployed")