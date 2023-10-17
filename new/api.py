import hashlib
import json
import os
import uuid
from pathlib import Path
from multiprocessing import Process, Pipe

from fastapi import FastAPI, Request, Security
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader

from ProcessManager import ResultManager
from manager import STTManager

app = FastAPI()

main_dir = Path(__file__).parent

api_key_header = APIKeyHeader(name="X-API-Key")
auth_key_header = APIKeyHeader(name="X-Auth-Key")

api_keys = os.getenv("STT_API_KEYS", "test").split(",")

# result_manager = ResultManager(main_dir / "results")

results = Path("data/results")
to_process = Path("data/to_process")


def get_audio_hash(audio):
    return hashlib.sha256(audio).hexdigest()


@app.post("/", response_class=JSONResponse, status_code=200)
async def write_upload(request: Request, api_key: str = Security(api_key_header)):
    print(f"Connnection from {request.client.host}")

    if api_key not in api_keys:
        return "Wrong API Key"

    audio = await request.body()

    with open("../temp.wav", "wb") as f:
        f.write(audio)

    hash_audio = get_audio_hash(audio)

    with open(to_process / f"{hash_audio}.wav", "wb") as f:
        f.write(audio)

    return {"launched": True, "hash": hash_audio}


@app.get("/status/{hash_audio}", response_class=JSONResponse, status_code=200)
async def get_status(request: Request, hash_audio: str, api_key: str = Security(api_key_header)):
    if api_key not in api_keys:
        return "Wrong API Key"

    jsonfile = results / f"{hash_audio}.json"
    audiofile = results / f"{hash_audio}.wav"

    if audiofile.exists():
        return {"status": "done"}

    if jsonfile.exists():
        return {"status": "processing"}

    return {"status": "not found"}

@app.get("/result/{hash_audio}", response_class=JSONResponse, status_code=200)
async def get_result(hash_audio: str, api_key: str = Security(api_key_header),
                     auth_key: str = Security(api_key_header)
                     ):
    if api_key not in api_keys:
        return "Wrong API Key"

    jsonfile = results / f"{hash_audio}.json"

    if not jsonfile.exists():
        return {"status": "not found"}

    with jsonfile.open(mode="r", encoding="utf-8") as f:
        return json.load(f)



def main():
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5464)

if __name__ == "__main__":
    main()
