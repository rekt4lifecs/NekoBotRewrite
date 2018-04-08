from PIL import Image
import requests
from io import BytesIO

img = Image.open("imagegen.jpg")
url = "https://cdn.discordapp.com/avatars/270133511325876224/a_807f6630050ebdbf4f45d682635f2903.png"
avatar = Image.open(BytesIO(requests.get(url).content)).resize((275, 275))

img.paste(avatar, (260, 75))

img.show()