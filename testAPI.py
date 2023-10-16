from time import sleep

import requests
from io import BytesIO
audio = "7206340881052372229.wav"

# url = "https://whisper.marceau-h.fr/"
url = "http://localhost:8000/"
# url = "http://localhost:5464/"

headers = {
    'content-type': 'audio/wav',
    "X-API-Key": "test"
}


def test():
    with open(audio, 'rb') as f:
        r = requests.post(url, headers=headers, data=BytesIO(f.read()))
        print(r.text)

    # pid = r.json()["pid"]
    process_id = r.json()["process_id"]
    auth_key = r.json()["auth_key"]
    # process_id = "27696dd8-c078-4728-9536-649103074a5d"

    while True:
        r = requests.get(url + f"status/{process_id}", headers=headers)
        print(r.text)
        if r.json()["status"] == "done":
            break

        sleep(20)

    headers["X-Auth-Key"] = auth_key


    r = requests.get(url + f"result/{process_id}", headers=headers)

    print(r.text)

test()





