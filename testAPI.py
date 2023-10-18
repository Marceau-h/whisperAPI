from time import sleep

import requests
from io import BytesIO

audio = "7206340881052372229.wav"

url = "https://whisper.marceau-h.fr/"
# url = "http://localhost:8000/"
url = "http://localhost:5464/"
# url = "http://192.168.2.2:5464/"

headers = {
    "X-API-Key": "test",
}


def test():
    with open(audio, 'rb') as f:
        data = f.read()

    # formdata = {
    #     # "Content-Type": "audio/wav",
    #     "data": BytesIO(data),
    #     "Content-Disposition": "form-data; name=file; filename=7206340881052372229.wav"
    # }

    files = {'file': ('7206340881052372229.wav', open('7206340881052372229.wav', 'rb'), 'audio/wav')}

    r = requests.post(url, headers=headers, files=files)
    print(r.text)
    hash_audio = r.json()["hash"]
    status = r.json()["status"]
    launched = r.json()["launched"]

    if not launched:
        print(f"Already launched: {hash_audio}, {status}")


    if status != "done":
        while True:
            r = requests.get(url + f"status/{hash_audio}", headers=headers)
            print(r.text)
            if r.json()["status"] == "done":
                break

            sleep(20)

    r = requests.get(url + f"result/{hash_audio}/segments", headers=headers)

    data = r.json()

    return data


if __name__ == "__main__":
    res = test()

    print("\n\n\n\n")
    print(res)
