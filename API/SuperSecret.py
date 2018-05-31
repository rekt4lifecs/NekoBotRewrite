from config import updatehook
from time import gmtime, strftime
import requests

webhook_id = updatehook["id"]
webhook_token = updatehook["token"]

webhook_url = "https://discordapp.com/api/webhooks/{0}/{1}".format(webhook_id, webhook_token)

inputdata = input("Update: ")

payload = {
    "embeds": [
        {
            "color": 0xDEADBF,
            "title": "OwO Whats This",
            "description": f"```\n{inputdata}\n```",
            "footer": {
                "text": f"Time: {strftime('%H:%M', gmtime())}"
            }
        }
    ]
}

requests.post(webhook_url, json=payload)
print("Posted.")