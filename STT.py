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
            beam_size=10,
            best_of=10,
            temperature=(0.0, 0.2, 0.4, 0.6, 0.8, 1.0),
            vad=True,  # Voice Activity Detection
            detect_disfluencies=True
        )
        # print(result)
    except:
        pass  # For breakpoint
        raise
    return result


def modelloader(uri: str = "medium"):  # "large" | "medium" | "small" | "tiny" | "openai/whisper-medium" ...
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model = whisper.load_model(uri, device=device)
    print(f"Before {model.device = }")
    # model.load_state_dict(torch.load(uri, map_location=device))
    print(f"Cuda detected : {torch.cuda.is_available()}\n{device = }")
    # try:
    #     # `model =` Seemed useless bc the function is in place but ensures to free up memory upon deletion ?
    #     model = model.to(device)
    #     # model.to("cpu")
    # except:
    #     print(f"Unable to load model on {device}")
    #     # device = torch.device("cpu")
    #     # model.to(device)
    print(f"After {model.device = }")

    return model, device


if __name__ == "__main__":
    modelloader()
