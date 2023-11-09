import whisper_timestamped as whisper
import torch

from pathlib import Path


class STTManager:
    def __init__(self):
        torch.cuda.empty_cache()  # A bit slow but only done once
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
        result = whisper.transcribe(
            model,
            audio,
            language="fr",
            beam_size=15,
            best_of=15,
            temperature=(0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1, 5, 10, 20, 50, 100),
            detect_disfluencies=True,
            vad=True,
        )
        # print(result)
    except:
        pass  # For breakpoint
        raise
    return result


def modelloader(uri: str = "openai/whisper-medium"):  # "large" | "medium" | "small" | "tiny" | "openai/whisper-medium" ...
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model = whisper.load_model(uri, device=device)
    print(f"Cuda detected : {torch.cuda.is_available()}\n{device = }")
    return model, device


if __name__ == "__main__":
    modelloader()
