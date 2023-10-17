from pathlib import Path
import json
from multiprocessing import Lock
from time import sleep

from new.STT import STTManager

# Only for reference
results_dir = "results"
to_process_dir = "to_process"
processing = "processing.json"
done = "done.json"


def main(folder: Path, lock: Lock):
    stt_manager = STTManager()

    results_dir = folder / "results"
    to_process_dir = folder / "to_process"
    processing = folder / "processing.json"
    done = folder / "done.json"

    old_processing_set = set()
    while True:
        print("Checking for new files")
        lock.acquire()
        if processing.exists():
            with processing.open(mode="r", encoding="utf-8") as f:
                processing_list = json.load(f)
        else:
            processing_list = []

        processing_set = set(processing_list)
        processing_set -= old_processing_set

        lock.release()

        for audio in processing_set:
            audio_file = to_process_dir / f"{audio}.wav"
            result_file = results_dir / f"{audio}.json"

            audio_file = audio_file.resolve()
            try:
                result = stt_manager.process_file(audio_file)
            except Exception as e:
                print(f"Error processing {audio_file}")
                print(e)
                continue

            lock.acquire()
            with result_file.open(mode="w", encoding="utf-8") as f:
                json.dump(result, f)
            lock.release()

        old_processing_set = set(processing_list)


if __name__ == "__main__":
    main(Path("data"), Lock())
