from web3 import Web3
import json
import time

# === 1. Sepolia testnet'e bağlan ===
INFURA_PROJECT_ID = "03f1998d577f4857b2175863920ee677"
w3 = Web3(Web3.HTTPProvider(f"https://sepolia.infura.io/v3/03f1998d577f4857b2175863920ee677"))

if not w3.is_connected():
    raise Exception("Sepolia ağına bağlanılamadı!")

# === 2. Gönderici cüzdan bilgileri ===
sender_address = Web3.to_checksum_address("0x4A6713E8461E90eC56E98dC24A0Ff8fa1959FbD9")
sender_private_key = "0x7adb4051e4f79a5a74be32ead912606e2cbec919afc1637c4f95a0b4cc62645e"  # ⚠️ Bu bilgiyi gizli tut

# === 3. Sepolia üzerinde deploy edilen ERC-20 token adresi ve ABI ===
token_address = Web3.to_checksum_address("0x8d2e0d94d504d832790afbbd8fb678a392192d2b")

# ERC-20 ABI dosyasını yükle
with open("erc20_abi.json", "r") as f:
    abi = json.load(f)

# Token kontrat nesnesini oluştur
token = w3.eth.contract(address=token_address, abi=abi)

# === 4. Alıcı cüzdanlar (wallets.json) ===
with open("wallets.json", "r") as f:
    wallets = json.load(f)

# === 5. Token dağıtımı ===
nonce = w3.eth.get_transaction_count(sender_address)

for i, wallet in enumerate(wallets):
    to = Web3.to_checksum_address(wallet["address"])

    # Token miktarı (örneğin: 1 token = 10**18 wei)
    amount = 10**18

    # İşlem oluştur
    tx = token.functions.transfer(to, amount).build_transaction({
        'from': sender_address,
        'nonce': nonce,
        'gas': 100000,
        'gasPrice': w3.to_wei('10', 'gwei')  # Sepolia için yeterli
    })

    # İşlemi imzala ve gönder
    signed_tx = w3.eth.account.sign_transaction(tx, sender_private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

    print(f"[{i}] Token gönderildi → {to} | İşlem hash: {tx_hash.hex()}")

    nonce += 1
    time.sleep(1.5)  # Ağı yormamak için gecikme