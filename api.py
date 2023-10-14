import os
from pathlib import Path

from fastapi import FastAPI, Request, Security
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader

from manager import STTManager

app = FastAPI()

main_dir = Path(__file__).parent

stt_manager = STTManager()
api_key_header = APIKeyHeader(name="X-API-Key")

api_keys = os.getenv("STT_API_KEYS", "test").split(",")

@app.post("/", response_class=JSONResponse, status_code=200)
async def write_upload(request: Request, api_key: str = Security(api_key_header)):
    if api_key not in api_keys:
        return "Wrong API Key"

    audio = await request.body()

    with open("../temp.wav", "wb") as f:
        f.write(audio)

    res = stt_manager.process_file("../temp.wav")


    return res



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5464)
