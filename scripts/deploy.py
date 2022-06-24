from brownie import accounts, network, config, Locker, PolkapadERC20, Whitelist

def deploy_whitelist():
    owner_account = get_account()
    multisig_account = accounts[1]

    contract = Whitelist.deploy(multisig_account, 60, { "from": owner_account })

    return contract

def deploy_plpd(locker_contract):
    owner_account = get_account()

    contract = PolkapadERC20.deploy(
    "Polkapad", 
    "PLPD", 
    locker_contract, 
    { "from": owner_account })

    return contract

def deploy_locker(whitelist_contract):
    owner_account = get_account()
    multisig_account = accounts[1]

    contract = Locker.deploy(
        multisig_account,
        config["addresses"]["dot"], 
        config["addresses"]["feed"],
        whitelist_contract,
        { "from": owner_account })

    return contract

def get_account(): 
    if network.show_active() == "development":
        return accounts[0]
    else:
        return accounts.add(config["addresses"]["private_key"])

def deploy():
    print("Deploying is started...")

    owner_account = get_account()

    whitelist = deploy_whitelist()
    locker = deploy_locker(whitelist)
    plpd = deploy_plpd(locker)

    locker.setPlpdContractAddress(plpd, { "from": owner_account })
    
    print("Contracts has deployed")