import whisper_timestamped as whisper
import torch

from pathlib import Path



class STTManager:
    def __init__(self):
        torch.cuda.empty_cache()

        model = whisper.load_model("bofenghuang/whisper-large-v2-french")
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        try:
            model.to(device)
        except:
            print(f"Unable to load model on {device}")
            model.to(torch.device("cpu"))

        self.model = model

    def process_file(self, audio_file: str | Path) -> dict:
        return process_file(audio_file, self.model)

    def process_folder(self, folder: str | Path) -> dict:
        folder = Path(folder)
        results = {}
        for audio in folder.glob("*.wav"):
            results[audio.name] = self.process_file(audio)
        return results

def process_file(audio_file: str | Path, model=None) -> dict:
    if model is None:
        model = whisper.load_model("bofenghuang/whisper-large-v2-french")
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        try:
            model.to(device)
        except:
            print(f"Unable to load model on {device}")
            model.to(torch.device("cpu"))

    audio = whisper.load_audio(audio_file)
    try:
        result = whisper.transcribe(model, audio, language="fr")
        print(result)
    except:
        pass
        raise
    return result
