from time import sleep

import requests
from io import BytesIO
audio = "7206340881052372229.wav"

# url = "https://whisper.marceau-h.fr/"
url = "http://localhost:8000/"
url = "http://localhost:5464/"

headers = {
    'content-type': 'audio/wav',
    "X-API-Key": "test"
}


def test():
    with open(audio, 'rb') as f:
        r = requests.post(url, headers=headers, data=BytesIO(f.read()))
        print(r.text)
    hash_audio = r.json()["hash"]


    # pid = r.json()["pid"]
    # auth_key = r.json()["auth_key"]
    # process_id = "27696dd8-c078-4728-9536-649103074a5d"
    hash_audio = "c4c4b41235d7e13c1b03149b8d5888de9ab499f7e0da1b6925a4094321b23775"

    while True:
        r = requests.get(url + f"status/{hash_audio}", headers=headers)
        print(r.text)
        if r.json()["status"] == "done":
            break

        sleep(20)


    r = requests.get(url + f"result/{hash_audio}", headers=headers)

    print(r.text)

test()





