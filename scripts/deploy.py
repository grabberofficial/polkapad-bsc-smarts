from brownie import accounts, network, config, Locker, PolkapadERC20, Whitelist

DEPLOYER = (0, "deployer_pk")
MULTISIG = config["addresses"]["multisig"]
BURNER = config["addresses"]["burner"]

def deploy_whitelist(deployer, multisig, default_max_allocation_size):
    contract = Whitelist.deploy(
        multisig,
        { "from": deployer })

    return contract

def deploy_plpd(deployer, multisig):
    contract = PolkapadERC20.deploy(
        "Polkapad", 
        "PLPD", 
        multisig, 
        { "from": deployer })

    return contract

def deploy_locker(deployer, multisig, burner, polkapad, whitelist):
    contract = Locker.deploy(
        multisig,
        burner,
        config["addresses"]["dot"], 
        config["addresses"]["feed"],
        polkapad,
        whitelist,
        { "from": deployer })

    return contract

def get_account(account):
    dev_index = account[0]
    private_key = account[1]
    
    if network.show_active() == "development":
        return accounts[dev_index]
    else:
        return accounts.add(config["addresses"][private_key])

def deploy(deployer, multisig, burner):
    default_max_allocation_size = 100 * 1e18

    whitelist = deploy_whitelist(deployer, multisig, default_max_allocation_size)
    plpd = deploy_plpd(deployer, multisig)
    locker = deploy_locker(deployer, multisig, burner, plpd, whitelist)

def main():
    deployer = get_account(DEPLOYER)
    deploy(deployer, MULTISIG, BURNER)