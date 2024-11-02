import re
import requests
from telethon import TelegramClient, errors
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone
import asyncio
import hashlib
import json
import tempfile
import os

api_id = '25380560'
api_hash = '6e554fabcb17b2072f2b1242dfb7bdc6'
phone_number = '+905432240619'
client = TelegramClient('session_name', api_id, api_hash)

target_groups = {
    "indirimlisinerede",
    "firsatz",
    "indirimleralevaldi",
    "FIRSATLAR",
    "yurticifirsat",
    "yenifirsatlar",
    "Cuzdown",
    "ozelfirsat",
    "tasarrufluharca",
    "dhsicak_firsatlar",
    "indirimtakipciniz",
    "linkledinn",
    "indirimfirsathaber",
    "firsatdolu",
    "firsatcik",
    "albitir"
}
destination_group = 'denemeliksahmara' #Mesajların atılacağı grubun adını yazmanız gerekiyor


sent_message_hashes = set()
try:
    with open("sent_message_hashes.json", "r") as f:
        sent_message_hashes = set(json.load(f))
except FileNotFoundError:
    sent_message_hashes = set()

def get_message_hash(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def fetch_amazon_product_data(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    title = soup.find("span", {"id": "productTitle"}).get_text(strip=True) if soup.find("span", {
        "id": "productTitle"}) else "Ürün başlığı bulunamadı"
    price_whole = soup.find("span", class_="a-price-whole")
    price_fraction = soup.find("span", class_="a-price-fraction")
    price = f"{price_whole.get_text(strip=True)}.{price_fraction.get_text(strip=True)}" if price_whole and price_fraction else "Fiyat bulunamadı"

    img_tag = soup.find("img", {"id": "landingImage"})
    if img_tag:
        dynamic_image_data = img_tag.get("data-a-dynamic-image")
        image_url = list(json.loads(dynamic_image_data).keys())[0] if dynamic_image_data else img_tag.get("src")
    else:
        image_url = None

    return title, price, image_url


def update_amazon_links(text):
    def replace_tag(match):
        url = match.group(0)

        # 'tag' parametresini güncelleme veya ekleme
        if "tag=" in url:
            url = re.sub(r'tag=[^&]+', 'tag=indirimalarmitr_4895-21', url)
        else:
            separator = "&" if "?" in url else "?"
            url = f"{url}{separator}tag=indirimalarmitr_4895-21"
        
        # 'smid', 'th', ve 'psc' parametrelerini kaldırma
        url = re.sub(r'(&|\?)smid=[^&]+', '', url)
        url = re.sub(r'(&|\?)th=[^&]+', '', url)
        url = re.sub(r'(&|\?)psc=[^&]+', '', url)
        url = re.sub(r'(&|\?)creative=[^&]+', '', url)
        # Art arda gelen '&' karakterlerini düzenleme
        url = re.sub(r'&{2,}', '&', url).replace('?&', '?')
        return url
    
    return re.sub(r'https?://(www\.)?amazon\.[\w\.]+/[^\s]+', replace_tag, text)
    


def remove_stock_messages(text):
    return re.sub(r'(?i)^[^:]*stok:.*\n?', '', text, flags=re.MULTILINE).strip()


async def send_message_or_image(destination_group, message, image_url=None):
    if image_url:
        image_data = requests.get(image_url).content
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as img_file:
            img_file.write(image_data)
            img_file_path = img_file.name
        await client.send_file(destination_group, img_file_path, caption=message.strip())
        os.unlink(img_file_path)  # Geçici dosyayı silin
    else:
        await client.send_message(destination_group, message.strip())


async def process_group_messages(target_group):
    one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
    print(f"Processing group: {target_group}")

    async for message in client.iter_messages(target_group):
        if message.date < one_hour_ago:
            continue

        # Mesajda Amazon linki varsa işle
        amazon_link_match = re.search(r'https?://(www\.)?amazon\.[\w\.]+/[^\s]+', message.text)
        if not amazon_link_match:
            continue  # Amazon linki yoksa bu mesajı atla

        # Amazon linkini al ve güncelle
        amazon_link = amazon_link_match.group(0)
        modified_text = update_amazon_links(amazon_link)

        # Mesajın hash'ini al
        message_hash = get_message_hash(modified_text)
        if message_hash in sent_message_hashes:
            print(f"Mesaj daha önce gönderilmiş: {modified_text.strip()}")
            continue

        try:
            # Amazon ürün bilgilerini getir ve mesajı oluştur
            title, price, image_url = fetch_amazon_product_data(modified_text)
            message_to_send = f"{title}\n\nFiyat: {price}\n\nLink: {modified_text} \n \n #işbirliği"
            await send_message_or_image(destination_group, message_to_send, image_url)
            print(f"{target_group} grubundan mesaj gönderildi: {message_to_send.strip()}")

            # Mesajın hash'ini kaydet
            sent_message_hashes.add(message_hash)

        except errors.ChatWriteForbiddenError as e:
            print(f"Yazma yasağı: {e}, mesaj gönderilemedi.")
        except Exception as e:
            print(f"Mesaj gönderimi sırasında hata: {e}")

    # Gönderilen mesaj hash'lerini kaydet
    with open("sent_message_hashes.json", "w") as f:
        json.dump(list(sent_message_hashes), f)


async def main():
    await client.start(phone=phone_number)
    while True:
        tasks = [process_group_messages(group) for group in target_groups]
        await asyncio.gather(*tasks)
        await asyncio.sleep(3600)


try:
    with client:
        client.loop.run_until_complete(main())
except asyncio.CancelledError:
    print("Kod tamamlandı.")
