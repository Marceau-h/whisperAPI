import whisper_timestamped as whisper
import torch

from pathlib import Path



class STTManager:
    def __init__(self):
        torch.cuda.empty_cache()

        self.model, self.device = modelloader()

    def process_file(self, audio_file: str | Path) -> dict:
        return process_file(audio_file, self.model)

    def process_folder(self, folder: str | Path) -> dict:
        folder = Path(folder)
        results = {}
        for audio in folder.glob("*.wav"):
            results[audio.name] = self.process_file(audio)
        return results

    def __del__(self):
        torch.cuda.empty_cache()
        print("Emptied cache")

def process_file(audio_file: str | Path, model=None) -> dict:
    if model is None:
        model, _ = modelloader()

    audio = whisper.load_audio(audio_file)
    try:
        result = whisper.transcribe(model, audio, language="fr")
        # print(result)
    except:
        pass  # For breakpoint
        raise
    return result


def modelloader(uri: str = "bofenghuang/whisper-large-v2-french"):
    model = whisper.load_model(uri)
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print(f"{device = }")
    try:
        model.to(device)
    except:
        print(f"Unable to load model on {device}")
        device = torch.device("cpu")
        model.to(device)

    return model, device
