from starlette.requests import Request
from starlette.responses import Response

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import List

from multiprocessing import Process, Pipe
import os

from fastapi import FastAPI
from starlette.requests import Request

app = FastAPI()


@app.post("/files/")
async def create_file(request: Request):
    print(request)
    body = b''
    with open("test.wav", "wb") as f:
        async for chunk in request.stream():
            print(chunk)
            body += chunk
            f.write(chunk)
    response = Response(body, media_type=request.headers["Content-Type"])

    return response


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0")
