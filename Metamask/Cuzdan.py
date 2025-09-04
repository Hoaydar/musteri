from eth_account import Account
import json

Account.enable_unaudited_hdwallet_features()

wallets = []

for i in range(1500):
    acct = Account.create()
    wallets.append({
        "address": acct.address,
        "private_key": acct.key.hex()
    })

# JSON olarak kaydet
with open("wallets.json", "w") as f:
    json.dump(wallets, f, indent=4)

print("[+] 1500 cüzdan başarıyla oluşturuldu ve kaydedildi.")