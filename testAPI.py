from time import sleep

import requests
from io import BytesIO

audio = "7206340881052372229.wav"

url = "https://whisper.marceau-h.fr/"
# url = "http://localhost:8000/"
# url = "http://localhost:5464/"

headers = {
    "content-type": "audio/wav",
    "X-API-Key": "test"
}


def test():
    with open(audio, 'rb') as f:
        r = requests.post(url, headers=headers, data=BytesIO(f.read()))
        print(r.text)
    hash_audio = r.json()["hash"]
    status = r.json()["status"]
    launched = r.json()["launched"]

    if not launched:
        print(f"Already launched: {hash_audio}, {status}")

    del headers["content-type"]

    if status != "done":
        while True:
            r = requests.get(url + f"status/{hash_audio}", headers=headers)
            print(r.text)
            if r.json()["status"] == "done":
                break

            sleep(20)

    r = requests.get(url + f"result/{hash_audio}", headers=headers)

    data = r.json()

    segments = [e["text"] for e in data["result"]["segments"]]
    span = [(int(e['start']), int(e['end'])) for e in data["result"]["segments"]]

    res = [
        {
            "span": s,
            "text": t
        }
        for s, t in zip(span, segments)
    ]

    return res


if __name__ == "__main__":
    print(test())
