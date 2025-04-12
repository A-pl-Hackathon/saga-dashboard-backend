from web3 import Web3
import json
import os
import random

def create_eth_keypair():
    """Generate a new Ethereum key pair on demand"""
    account = Web3().eth.account.create()
    private_key = account.key.hex()
    public_address = account.address
    return private_key, public_address

def get_random_key_pair(json_file="key_pair.json"):
    """Get a random key pair from the pre-generated pairs in the JSON file"""
    try:
        if not os.path.exists(json_file):
            # Fallback to generating a new pair if file doesn't exist
            return create_eth_keypair()
            
        with open(json_file, 'r') as f:
            key_pairs = json.load(f)
        
        if not key_pairs:
            return create_eth_keypair()
            
        # Select a random key pair
        pair_name = random.choice(list(key_pairs.keys()))
        pair_data = key_pairs[pair_name]
        
        return pair_data["private_key"], pair_data["public_address"]
    except Exception as e:
        print(f"Error loading key pair: {str(e)}")
        # Fallback to generating a new pair
        return create_eth_keypair()

def get_specific_key_pair(pair_id, json_file="key_pair.json"):
    """Get a specific key pair by ID from the pre-generated pairs"""
    try:
        if not os.path.exists(json_file):
            return None, None
            
        with open(json_file, 'r') as f:
            key_pairs = json.load(f)
        
        pair_name = f"KEY_PAIR_{pair_id}"
        if pair_name not in key_pairs:
            return None, None
            
        pair_data = key_pairs[pair_name]
        return pair_data["private_key"], pair_data["public_address"]
    except Exception as e:
        print(f"Error loading specific key pair: {str(e)}")
        return None, None
