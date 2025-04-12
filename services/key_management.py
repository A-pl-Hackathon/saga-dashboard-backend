from web3 import Web3

def create_eth_keypair():
    account = Web3().eth.account.create()
    private_key = account.key.hex()
    public_address = account.address
    return private_key, public_address
