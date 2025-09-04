import json

# Girdi ve çıktı dosya yolları
INPUT_FILE = "input.json"
OUTPUT_FILE = "output.json"

def filter_addresses(input_file, output_file):
    # JSON dosyasını oku
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Sadece address alanlarını al
    filtered = [{"address": item["address"]} for item in data]

    # Yeni JSON dosyasını yaz
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(filtered, f, indent=4)

if __name__ == "__main__":
    filter_addresses(INPUT_FILE, OUTPUT_FILE)
    print(f"Adresler '{OUTPUT_FILE}' dosyasına kaydedildi.")