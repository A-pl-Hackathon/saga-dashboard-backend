from web3 import Web3
import os
import json
from dotenv import load_dotenv, set_key
import sys

def create_eth_keypair():
    account = Web3().eth.account.create()
    private_key = account.key.hex()
    public_address = account.address
    return private_key, public_address

def generate_and_save_key_pairs(count=2, output_file="key_pair.env"):
    key_pairs = {}
    
    for i in range(count):
        private_key, public_address = create_eth_keypair()
        key_pairs[f"KEY_PAIR_{i+1}"] = {
            "private_key": private_key,
            "public_address": public_address
        }
    
    with open(output_file, 'w') as f:
        for pair_name, pair_data in key_pairs.items():
            f.write(f"{pair_name}_PRIVATE_KEY={pair_data['private_key']}\n")
            f.write(f"{pair_name}_PUBLIC_ADDRESS={pair_data['public_address']}\n")
    
    print(f"{count} key pairs have been generated and saved to {output_file}.")
    
    json_file = output_file.replace('.env', '.json')
    with open(json_file, 'w') as f:
        json.dump(key_pairs, f, indent=2)
    
    print(f"Also saved in JSON format to {json_file}.")
    
    return key_pairs

def load_key_pairs(env_file="key_pair.env"):
    load_dotenv(env_file)
    
    key_pairs = {}
    pair_count = 0
    
    i = 1
    while True:
        private_key = os.getenv(f"KEY_PAIR_{i}_PRIVATE_KEY")
        public_address = os.getenv(f"KEY_PAIR_{i}_PUBLIC_ADDRESS")
        
        if not private_key or not public_address:
            break
            
        key_pairs[f"KEY_PAIR_{i}"] = {
            "private_key": private_key,
            "public_address": public_address
        }
        pair_count += 1
        i += 1
    
    print(f"Loaded {pair_count} key pairs from {env_file}.")
    return key_pairs

if __name__ == "__main__":
    count = 10
    output_file = "key_pair.env"
    
    if len(sys.argv) > 1:
        try:
            count = int(sys.argv[1])
        except ValueError:
            print("Error: The number of key pairs to generate must be an integer.")
            sys.exit(1)
    
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    
    key_pairs = generate_and_save_key_pairs(count, output_file)
    
    print("\nGenerated key pairs:")
    for name, data in key_pairs.items():
        print(f"{name}:")
        print(f"  Private Key: {data['private_key']}")
        print(f"  Public Address: {data['public_address']}")
        print() 