import os
import json
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

RPC_URL = os.getenv("RPC_URL")
MTK_CONTRACT_ADDRESS = os.getenv("MTK_CONTRACT_ADDRESS")

w3 = Web3(Web3.HTTPProvider(RPC_URL))

# ABI 파일 읽기
with open("./abi/erc20_abi.json", "r") as file:
    ERC20_ABI = json.load(file)

token_contract = w3.eth.contract(address=MTK_CONTRACT_ADDRESS, abi=ERC20_ABI)

def get_token_balance(wallet_address: str):
    checksum_address = w3.to_checksum_address(wallet_address)
    token_balance = token_contract.functions.balanceOf(checksum_address).call()
    decimals = token_contract.functions.decimals().call()
    balance_token = token_balance / (10 ** decimals)
    return balance_token
