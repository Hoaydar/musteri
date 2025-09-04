import random
from web3 import Web3
import json
import time

w3 = Web3(Web3.HTTPProvider("https://sepolia.infura.io/v3/03f1998d577f4857b2175863920ee677"))

token_address = Web3.to_checksum_address("0x8d2e0d94d504d832790afbbd8fb678a392192d2b")
with open("erc20_abi.json") as f:
    abi = json.load(f)

token = w3.eth.contract(address=token_address, abi=abi)

with open("walletss.json") as f:
    wallets = json.load(f)

# Her biri rastgele birine token göndersin
for sender in wallets:
    recipient = random.choice(wallets)
    if sender["address"] == recipient["address"]:
        continue

    sender_address = Web3.to_checksum_address(sender["address"])
    sender_key = sender["private_key"]
    recipient_address = Web3.to_checksum_address(recipient["address"])

    try:
        nonce = w3.eth.get_transaction_count(sender_address)
        tx = token.functions.transfer(recipient_address, 10**17).build_transaction({
            'from': sender_address,
            'nonce': nonce,
            'gas': 100000,
            'gasPrice': w3.to_wei('20', 'gwei')
        })

        signed_tx = w3.eth.account.sign_transaction(tx, sender_key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

        print(f"{sender_address[:10]}... => {recipient_address[:10]}...: {tx_hash.hex()}")
        time.sleep(1.5)
    except Exception as e:
        print(f"❌ Hata: {e}")