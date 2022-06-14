from brownie import accounts, network, config, Locker

def deploy_locker():
    account = get_account()
    Locker.deploy(
        config["addresses"]["plpd"], 
        config["addresses"]["dot"], 
        config["addresses"]["aggregator"],
        config["addresses"]["target_wallet"],
        { "from": account })

def get_account(): 
    if network.show_active() == "development":
        return accounts[0]
    else:
        return accounts.load("locker-account")

def main():
    print("Locker contract deploying is started...")

    deploy_locker()
    
    print("Locker contract has deployed")