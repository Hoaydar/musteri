from web3 import Web3
import json
import time

# === 1. Sepolia testnet bağlantısı ===
INFURA_PROJECT_ID = "03f1998d577f4857b2175863920ee677"
w3 = Web3(Web3.HTTPProvider(f"https://sepolia.infura.io/v3/03f1998d577f4857b2175863920ee677"))

if not w3.is_connected():
    raise Exception("Sepolia ağına bağlanılamadı!")

print("✅ Sepolia ağına bağlandı.")

# === 2. Tek gönderen cüzdan ===
sender_address = Web3.to_checksum_address("0x4A6713E8461E90eC56E98dC24A0Ff8fa1959FbD9")  # faucetten aldığın ETH burada
sender_private_key = "0x7adb4051e4f79a5a74be32ead912606e2cbec919afc1637c4f95a0b4cc62645e"

# === 3. Alıcılar ===
with open("wallets.json") as f:
    wallets = json.load(f)

# === 4. Her adrese ETH gönder ===
amount_in_eth = 0.001  # Her adrese gönderilecek ETH

nonce = w3.eth.get_transaction_count(sender_address)

for i, wallet in enumerate(wallets):
    recipient_address = Web3.to_checksum_address(wallet["address"])

    tx = {
        'from': sender_address,
        'to': recipient_address,
        'value': w3.to_wei(amount_in_eth, 'ether'),
        'gas': 21000,
        'gasPrice': w3.to_wei('10', 'gwei'),
        'nonce': nonce
    }

    signed_tx = w3.eth.account.sign_transaction(tx, sender_private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

    print(f"[{i}] {amount_in_eth} ETH gönderildi → {recipient_address} | Tx hash: {tx_hash.hex()}")

    nonce += 1
    time.sleep(1.5)  # ağı yormamak için

print("✅ ETH dağıtımı tamamlandı.")