import hashlib
import json
import os
from pathlib import Path

from fastapi import FastAPI, Request, Security
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader


app = FastAPI()

main_dir = Path(__file__).parent

api_key_header = APIKeyHeader(name="X-API-Key")

api_keys = os.getenv("STT_API_KEYS", "test").split(",")
api_keys = [e.strip() for e in api_keys]

results = Path("data/results")
to_process = Path("data/to_process")


def get_audio_hash(audio):
    return hashlib.sha256(audio).hexdigest()


@app.post("/", response_class=JSONResponse, status_code=200)
async def write_upload(request: Request, api_key: str = Security(api_key_header)):
    print(f"Connnection from {request.client.host}")

    if api_key not in api_keys:
        print("Wrong API Key")
        return {"error": "Wrong API Key", "status": "error"}

    audio = await request.body()

    hash_audio = get_audio_hash(audio)

    audiofile = to_process / f"{hash_audio}.wav"
    if audiofile.exists():
        print("Already exists")

        json_file = results / f"{hash_audio}.json"
        if json_file.exists():
            print("Already processed")
            with json_file.open(mode="r", encoding="utf-8") as f:
                return {"launched": False, "hash": hash_audio, "status": "done", "result": json.load(f)}

        return {"launched": False, "hash": hash_audio, "status": "processing"}


    with open(to_process / f"{hash_audio}.wav", "wb") as f:
        f.write(audio)

    return {"launched": True, "hash": hash_audio, "status": "new"}


@app.get("/status/{hash_audio}", response_class=JSONResponse, status_code=200)
async def get_status(hash_audio: str, api_key: str = Security(api_key_header)):
    if api_key not in api_keys:
        return {"error": "Wrong API Key", "status": "error"}

    jsonfile = results / f"{hash_audio}.json"
    audiofile = to_process / f"{hash_audio}.wav"

    if jsonfile.exists():
        return {"status": "done"}

    if audiofile.exists():
        return {"status": "processing"}

    return {"status": "not found"}

@app.get("/result/{hash_audio}", response_class=JSONResponse, status_code=200)
async def get_result(hash_audio: str, api_key: str = Security(api_key_header)):
    if api_key not in api_keys:
        return {"error": "Wrong API Key", "status": "error"}

    jsonfile = results / f"{hash_audio}.json"

    if not jsonfile.exists():
        return {"status": "not found"}

    with jsonfile.open(mode="r", encoding="utf-8") as f:
        return {"status": "done", "result": json.load(f)}

@app.get("/result/{hash_audio}/text", response_class=JSONResponse, status_code=200)
async def get_result_text(hash_audio: str, api_key: str = Security(api_key_header)):
    result = await get_result(hash_audio, api_key)

    if result["status"] != "done":
        return result

    return {"status": "done", "result": result["result"]["text"]}

@app.get("/result/{hash_audio}/segments", response_class=JSONResponse, status_code=200)
async def get_result_segments(hash_audio: str, api_key: str = Security(api_key_header)):
    result = await get_result(hash_audio, api_key)

    if result["status"] != "done":
        return result

    segments = [e["text"] for e in result["result"]["segments"]]
    span = [(int(e['start']), int(e['end'])) for e in result["result"]["segments"]]
    confidence = [e["confidence"] for e in result["result"]["segments"]]

    res = [
        {
            "span": s,
            "text": t,
            "confidence": c
        }
        for s, t, c in zip(span, segments, confidence)
    ]

    return {"status": "done", "result": res}

@app.get("/result/{hash_audio}/words", response_class=JSONResponse, status_code=200)
async def get_result_words(hash_audio: str, api_key: str = Security(api_key_header)):
    result = await get_result(hash_audio, api_key)

    if result["status"] != "done":
        return result

    words = [e["text"] for segment in result["result"]["segments"] for e in segment["words"]]
    span = [(int(e['start']), int(e['end'])) for segment in result["result"]["segments"] for e in segment["words"]]
    confidence = [e["confidence"] for segment in result["result"]["segments"] for e in segment["words"]]

    res = [
        {
            "span": s,
            "text": t,
            "confidence": c
        }
        for s, t, c in zip(span, words, confidence)
    ]

    return {"status": "done", "result": res}



def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5464)

if __name__ == "__main__":
    main()
