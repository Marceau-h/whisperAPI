import qsync
import whisper_timestamped as whisper
import torch
from pathlib import Path
import json


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
    result = whisper.transcribe(model, audio, language="fr")
    return result


if __name__ == "__main__":
    audio = "7206340881052372229.wav"

    result = process_file(audio)
    print(json.dumps(result, indent=2, ensure_ascii=False))
