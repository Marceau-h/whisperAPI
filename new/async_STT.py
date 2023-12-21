import whisper_timestamped as whisper
import torch
import asyncio
from time import time, sleep

from pathlib import Path


class STTManager:
    keep_model_for = 1800  # seconds, so 30 minutes

    def __init__(self):
        self.device = None
        self.model = None
        self._loaded = False
        self._loaded_from = None
        self._unused_from = None
        self.lock = asyncio.Lock()

        asyncio.create_task(self.model_manager())

    async def model_loader(self, uri: str = "medium"):
        with self.lock:
            if self._loaded:
                return

            self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
            self.model = whisper.load_model(uri, device=self.device)
            try:
                self.model = self.model.to(self.device)
            except RuntimeError:
                print("Cuda out of memory, switching to CPU")
                self.device = torch.device("cpu")
                self.model = self.model.to(device=self.device)

            print(f"Cuda detected : {torch.cuda.is_available()}\n{self.device = }")

            self._loaded = True
            self._loaded_from = time()
            self._unused_from = time()

    async def model_unloader(self):
        with self.lock:
            if not self._loaded:
                return

            self._loaded = False
            del self.model, self.device
            self._loaded_from = None

            torch.cuda.empty_cache()

    def __del__(self):
        self.model_unloader()

    async def process_file(self, audio_file: str | Path) -> dict:
        if not self._loaded:
            await self.model_loader()

        audio = whisper.load_audio(audio_file)
        try:
            result = whisper.transcribe(
                self.model,
                audio,
                # language="fr",  # Not sure is it was useful bc of translations
                beam_size=15,
                best_of=15,
                temperature=(0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1, 5, 10, 20, 50, 100),
                detect_disfluencies=True,
                vad=True,
            )
        except:
            pass  # For breakpoint
            raise
        finally:
            self._unused_from = time()

        return result

    async def model_manager(self):
        while True:
            if any((not self._loaded, self._unused_from is None, self._loaded_from is None)):
                await asyncio.sleep(self.keep_model_for)
                continue

            now = time()

            diff = now - self._unused_from

            if diff > self.keep_model_for:
                await self.model_unloader()

            else:
                await asyncio.sleep(self.keep_model_for - diff)


if __name__ == "__main__":
    print("Start")

    sm = STTManager()
    print("Init")

    sm.process_file("../7206340881052372229.wav")
    print("P1")

    sleep(10)
    print("Sleep")

    sm.process_file("../7206340881052372229.wav")
    print("P2")

    del sm
    print("Del")





