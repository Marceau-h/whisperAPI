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





result_manager = ResultManager(main_dir / "results")




def wrap_process(*args, connexion: Pipe, **kwargs):
    connexion.send(stt_manager.process_file(*args, **kwargs))
    connexion.close()



@app.post("/", response_class=JSONResponse, status_code=200)
async def write_upload(request: Request, api_key: str = Security(api_key_header)):
    print(f"Connnection from {request.client.host}")

    if api_key not in api_keys:
        return "Wrong API Key"

    audio = await request.body()

    with open("../temp.wav", "wb") as f:
        f.write(audio)

    # hash_audio = get_audio_hash(audio)
    # res = stt_manager.process_file("../temp.wav")

    # conn1, conn2 = Pipe()
    # process = Process(target=wrap_process, args=("../temp.wav"), kwargs={"connexion": conn2})
    # process.daemon = True

    id_ = result_manager.add_process("../temp.wav")

    auth_key = hash(result_manager.get_auth_key(id_))

    hash_audio = result_manager.get_hash_audio(id_)

    return {"launched": True, "process_id": id_, "auth_key": auth_key, "hash": hash_audio}


@app.get("/status/{process_id}", response_class=JSONResponse, status_code=200)
async def get_status(request: Request, process_id: str, api_key: str = Security(api_key_header)):
    if api_key not in api_keys:
        return "Wrong API Key"

    process_id = uuid.UUID(process_id)

    status = result_manager.get_process_status(process_id)

    return {"status": status}


@app.get("/result/{process_id}", response_class=JSONResponse, status_code=200)
async def get_result(process_id: uuid.UUID, api_key: str = Security(api_key_header),
                     auth_key: str = Security(api_key_header)):
    if api_key not in api_keys:
        return "Wrong API Key"

    process_id = uuid.UUID(process_id)

    if auth_key != hash(result_manager.get_auth_key(process_id)):
        return "Wrong Auth Key"

    result = result_manager.get_process_result(process_id)

    return {"result": result}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5464)
