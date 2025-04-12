import os
import json
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

RPC_URL = os.getenv("RPC_URL")
MTK_CONTRACT_ADDRESS = os.getenv("MTK_CONTRACT_ADDRESS")

w3 = Web3(Web3.HTTPProvider(RPC_URL))

# Read ABI file
with open("./abi/erc20_abi.json", "r") as file:
    ERC20_ABI = json.load(file)

token_contract = w3.eth.contract(address=MTK_CONTRACT_ADDRESS, abi=ERC20_ABI)

def get_token_balance(wallet_address: str):
    # Special case for frontend requesting a new backend key without providing a real wallet
    if wallet_address == 'request_new_backend_key':
        print("Special case: request_new_backend_key detected. Returning 0 balance.")
        return 0  # Return 0 balance for this special case
    
    if not wallet_address or not isinstance(wallet_address, str):
        print(f"Invalid wallet address provided: {wallet_address}")
        return 0
    
    try:
        checksum_address = w3.to_checksum_address(wallet_address)
        token_balance = token_contract.functions.balanceOf(checksum_address).call()
        decimals = token_contract.functions.decimals().call()
        balance_token = token_balance / (10 ** decimals)
        return balance_token
    except ValueError as e:
        print(f"Invalid wallet address format: {wallet_address}. Error: {str(e)}")
        raise ValueError(f"Invalid wallet address format: {wallet_address}. Error: {str(e)}")
    except Exception as e:
        print(f"Error checking token balance: {str(e)}")
        raise Exception(f"Error checking token balance: {str(e)}")
