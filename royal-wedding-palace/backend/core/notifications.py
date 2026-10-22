import json
import logging
import os
from urllib.request import Request, urlopen

log = logging.getLogger(__name__)

def send_booking_alert(message):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not (token and chat_id):
        return
    try:
        data = json.dumps({"chat_id": chat_id, "text": message}).encode()
        request = Request("https://api.telegram.org/bot" + token + "/sendMessage",
                          data=data, headers={"Content-Type": "application/json"})
        with urlopen(request, timeout=3) as response:
            response.read()
    except Exception:
        log.exception("Telegram alert was not delivered; booking remains saved")
