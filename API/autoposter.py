import requests, time, random
from config import webhook_id, webhook_token

webhook_url = "https://discordapp.com/api/webhooks/{0}/{1}".format(webhook_id, webhook_token)

def get_img():
    img_type = random.choice(["lewdneko", "lewdkitsune", "hentai", "neko", "hentai_anal"])
    img = requests.get("https://nekobot.xyz/api/image?type={0}".format(img_type)).json()
    img = img["message"]
    payload = {
        "embeds": [
            {
                "color": 0xDEADBF,
                "image": {
                    "url": img
                }
            }
        ]
    }
    return payload

def post_hook():
    requests.post(webhook_url, json=get_img())

while True:
    print("Posting Neko!")
    post_hook()
    time.sleep(3600)