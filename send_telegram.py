import os
import requests
from dotenv import load_dotenv

load_dotenv('/home/codespace/OpenMontage/.env')

token = os.environ.get("TELEGRAM_BOT_TOKEN")
chat_id = os.environ.get("TELEGRAM_CHAT_ID")

if not token or not chat_id:
    print("Telegram token or chat id missing!")
    exit(1)

url = f"https://api.telegram.org/bot{token}/sendPhoto"
photo_path = "/home/codespace/OpenMontage/projects/_experiments/narrator-test/step3_0e_2x3.png"

with open(photo_path, "rb") as f:
    files = {"photo": f}
    data = {"chat_id": chat_id, "caption": "Test 0e Contact Sheet (6 images: 3 scenes x 2 wordings)"}
    res = requests.post(url, data=data, files=files)
    print("Telegram sendPhoto response:", res.status_code, res.text[:200])
