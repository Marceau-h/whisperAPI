import hashlib
import json
import os
from pathlib import Path
from urllib import parse

from fastapi import FastAPI, Request, Security, UploadFile
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
from starlette.responses import StreamingResponse

app = FastAPI()

main_dir = Path(__file__).parent

api_key_header = APIKeyHeader(name="X-API-Key")

api_keys = os.getenv("STT_API_KEYS", "test").split(",")
api_keys = [e.strip() for e in api_keys]

results = Path("data/results")
to_process = Path("data/to_process")

possible_suffixes = [".wav", ".mp3", ".ogg", ".flac", ".m4a"]


def key_validation(api_key: str = Security(api_key_header)) -> bool:
    api_key = parse.unquote(api_key)
    return api_key in api_keys


def get_audio_hash(audio):
    return hashlib.sha256(audio).hexdigest()


@app.get("/healthcheck", response_class=JSONResponse, status_code=200)
async def healthcheck(api_key: str = Security(api_key_header)):
    if not key_validation(api_key):
        return JSONResponse({"error": "Wrong API Key", "status": "error"}, status_code=401)

    return {"status": "ok"}


@app.post("/", response_class=JSONResponse, status_code=200)
async def write_upload(
        # file: UploadFile,
        request: Request,
        api_key: str = Security(api_key_header),
):
    # print(f"Connnection from {request.client.host}, {api_key = }, {file.filename = }, {file.content_type = }")
    #
    if not key_validation(api_key):
        print("Wrong API Key")
        return JSONResponse({"error": "Wrong API Key", "status": "error"}, status_code=401)
    #
    # if not file.content_type.startswith("audio/"):
    #     print("Wrong content type")
    #     return JSONResponse({"error": "Wrong content type", "status": "error"}, status_code=400)
    #
    # extension = file.filename.split(".")[-1]
    # if extension != file.content_type.split("/")[-1]:
    #     print(f"mismatch between extension ({extension}) and content type ({file.content_type})")

    # audio = await file.read()

    # audio = b''
    # async for chunk in request.stream():
    #     audio += chunk

    audio = StreamingResponse(request.stream())
    audio = await audio.body()

    hash_audio = get_audio_hash(audio)

    # audiofile = to_process / f"{hash_audio}.{extension}"
    audiofile = to_process / f"{hash_audio}.wav"
    if audiofile.exists():
        print("Already exists")

        json_file = results / f"{hash_audio}.json"
        if json_file.exists():
            print("Already processed")
            with json_file.open(mode="r", encoding="utf-8") as f:
                return JSONResponse(
                    {"launched": False, "hash": hash_audio, "status": "done", "result": json.load(f)},
                    status_code=302,
                )

        return JSONResponse(
            {"launched": False, "hash": hash_audio, "status": "processing"},
            status_code=425,
        )

    with open(to_process / f"{hash_audio}.wav", "wb") as f:
        f.write(audio)

    return JSONResponse(
        {"launched": True, "hash": hash_audio, "status": "new"},
        status_code=202,
        headers={"Location": f"/status/{hash_audio}"},
    )


@app.get("/status/{hash_audio}", response_class=JSONResponse, status_code=200)
async def get_status(hash_audio: str, api_key: str = Security(api_key_header)):
    if not key_validation(api_key):
        return JSONResponse({"error": "Wrong API Key", "status": "error"}, status_code=401)

    jsonfile = results / f"{hash_audio}.json"
    audiofile = to_process / f"{hash_audio}.wav"

    if jsonfile.exists():
        return JSONResponse(
            {"status": "done", "hash": hash_audio},
            status_code=201,
            headers={"Location": f"/result/{hash_audio}"},
        )

    if audiofile.exists():
        return {"status": "processing", "hash": hash_audio}
    else:
        print(f"Not found as {audiofile.name}")
        for audiofile in to_process.glob(f"{hash_audio}.*"):
            if audiofile.suffix in possible_suffixes:
                print(f"Found as {audiofile.name}")
                return {"status": "processing", "hash": hash_audio}

    return JSONResponse({"status": "not found", "hash": None}, status_code=404)


@app.get("/result/{hash_audio}", response_class=JSONResponse, status_code=200)
async def get_result(hash_audio: str, api_key: str = Security(api_key_header)):
    if not key_validation(api_key):
        return JSONResponse({"error": "Wrong API Key", "status": "error"}, status_code=401)

    jsonfile = results / f"{hash_audio}.json"

    if not jsonfile.exists():
        return JSONResponse({"status": "not found"}, status_code=404)

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

    segments = [e["text"].strip() for e in result["result"]["segments"]]
    span = [(e['start'], e['end']) for e in result["result"]["segments"]]
    confidence = [e["confidence"] for e in result["result"]["segments"]]

    res = [
        {
            "span": s,
            "confidence": c,
            "text": t,
        }
        for s, t, c in zip(span, segments, confidence)
    ]

    return {"status": "done", "result": res}


@app.get("/result/{hash_audio}/words", response_class=JSONResponse, status_code=200)
async def get_result_words(hash_audio: str, api_key: str = Security(api_key_header)):
    result = await get_result(hash_audio, api_key)

    if result["status"] != "done":
        return result

    words = [e["text"].strip() for segment in result["result"]["segments"] for e in segment["words"]]
    span = [(e['start'], e['end']) for segment in result["result"]["segments"] for e in segment["words"]]
    confidence = [e["confidence"] for segment in result["result"]["segments"] for e in segment["words"]]

    res = [
        {
            "span": s,
            "confidence": c,
            "text": t,
        }
        for s, t, c in zip(span, words, confidence)
    ]

    return {"status": "done", "result": res}


def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5464)


if __name__ == "__main__":
    main()
