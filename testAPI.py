import requests
from io import BytesIO
audio = "7206340881052372229.wav"

url = "https://whisper.marceau-h.fr/"

headers = {
    'content-type': 'audio/wav',
    "X-API-Key": "test"
}


def test():
    with open(audio, 'rb') as f:
        r = requests.post(url, headers=headers, data=BytesIO(f.read()))
        print(r.text)

test()





