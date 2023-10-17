from multiprocessing import Process, Pipe
from pathlib import Path
import json
import uuid
import hashlib

from manager import STTManager


stt_manager = STTManager()

class ResultManager:
    def __init__(self, json_path: str | Path):
        if isinstance(json_path, str):
            json_path = Path(json_path)

        self.json_path = json_path

        self.processes = {}
        self.audios = {}
        self.results = {}

    @classmethod
    def from_json(cls, json_path: str | Path):
        if isinstance(json_path, str):
            json_path = Path(json_path)

        self = cls(json_path)

        with open(json_path / "processes.json", "r", encoding="utf-8") as f:
            self.processes = json.load(f)

        with open(json_path / "audios.json", "r", encoding="utf-8") as f:
            self.audios = json.load(f)

        with open(json_path / "results.json", "r", encoding="utf-8") as f:
            self.results = json.load(f)

        return self

    def add_process(self, audio: str | Path):
        id_ = None

        with open(audio, "rb") as f:
            hash_audio = self.get_audio_hash(f.read())

        while id_ is None or id_ in self.processes:
            id_ = uuid.uuid4()

        if hash_audio in self.audios:
            match self.audios[hash_audio]["status"]:
                case "done":
                    raise ValueError("Audio already processed")
                case "pending":
                    raise ValueError("Audio processing")
                case "error":
                    print("Audio errored, reprocessing")

        self.audios[hash_audio] = {"id": id_, "status": "pending"}

        conn1, conn2 = Pipe()
        process = Process(target=self.wrap_process, args=(audio,), kwargs={"connexion": conn2})
        process.daemon = True
        process.start()

        print(f"Process {id_} started with PID {process.pid}")

        self.processes[id_] = {"process": process, "connexion": conn1}

        return id_

    def get_process_status(self, id_: uuid.UUID, hash_audio: str = None):
        try:
            process = self.processes[id_]["process"]
            alive = process.is_alive()
            if not alive:
                if process.exitcode != 0:
                    print(process.__dict__())

                    self.audios[hash_audio]["status"] = "error"
                    del self.processes[id_]

                    return f'error: {process.exitcode}'

                self.results[id_] = self.processes[id_]["connexion"].recv()

                if hash_audio is None:
                    for hash_, data in self.audios.items():
                        if data["id"] == id_:
                            hash_audio = hash_
                            break

                if hash_audio is not None:
                    self.audios[hash_audio]["status"] = "done"

                return "done"

            else:
                return "pending"
        except:
            print(self.processes)
            raise

    def get_process_result(self, id_: uuid.UUID):
        return self.results[id_]

    def get_process(self, id_: uuid.UUID):
        return self.processes[id_]["process"]

    def get_all_processes(self):
        return self.processes

    def get_auth_key(self, id_: uuid.UUID):
        return self.processes[id_]["process"].authkey

    def get_from_hash_audio(self, hash_audio: str):
        if hash_audio in self.audios:
            res = self.audios[hash_audio]
            if res["status"] == "done":
                return self.results[res["id"]]
            else:
                return res["status"]

    def __repr__(self):
        return f"<ResultManager {len(self.processes)} processes>"

    def __str__(self):
        return self.__repr__()

    def __len__(self):
        return len(self.processes)

    def __getitem__(self, item):
        return self.results[item] if item in self.results else self.processes[item]

    def __iter__(self):
        return iter(self.processes)

    def __contains__(self, item):
        return item in self.processes

    def __delitem__(self, key):
        raise NotImplementedError()

    def __setitem__(self, key, value):
        raise NotImplementedError("Use add_process instead")

    def __del__(self):
        for process in self.processes.values():
            process.terminate()
            process.join()

        with open(self.json_path, "w") as f:
            json.dump(self.processes, f)

        print("All processes terminated")

    @staticmethod
    def wrap_process(*args, connexion: Pipe, **kwargs):
        connexion.send(stt_manager.process_file(*args, **kwargs))
        connexion.close()

    @staticmethod
    def get_audio_hash(audio):
        return hashlib.sha256(audio).hexdigest()

    def get_hash_audio(self, id_: uuid.UUID):
        for hash_, data in self.audios.items():
            if data["id"] == id_:
                return hash_
        return None
