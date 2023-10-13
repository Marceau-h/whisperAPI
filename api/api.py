import json
import os
from io import StringIO
from typing import List, Tuple
from pathlib import Path

from fastapi import FastAPI, UploadFile, Form, File, Header, Request, Security
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse, HTMLResponse, FileResponse, Response, JSONResponse
from starlette.templating import Jinja2Templates
from fastapi.security import APIKeyHeader

from stt.manager import STTManager

app = FastAPI()

main_dir = Path(__file__).parent

stt_manager = STTManager()
api_key_header = APIKeyHeader(name="X-API-Key")

host = os.getenv("STT_HOST", "")
prefix = os.getenv("STT_PREFIX", "")

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
    uvicorn.run(app, host="0.0.0.0", port=8000)
