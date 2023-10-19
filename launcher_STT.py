from pathlib import Path
import json
from time import sleep

from STT import STTManager


def main(folder: Path):
    stt_manager = STTManager()

    results_dir = folder / "results"
    to_process_dir = folder / "to_process"
    results_dir.mkdir(exist_ok=True, parents=True)
    to_process_dir.mkdir(exist_ok=True)

    previous_empty = 0
    while True:
        all_audios = to_process_dir.iterdir()
        all_audios = {e.stem: e for e in all_audios}

        to_process = {
            e.stem for e in to_process_dir.glob("*.[wmoa][apgc][v3gc]")
        }
        results = {e.stem for e in results_dir.glob("*.json")}
        processing_set = to_process - results

        if not processing_set:
            previous_empty += 1
            # print(f"No new files since {previous_empty} iterations")
            if previous_empty == 10:
                print("INFO : No new files for 10 iterations")
            sleep(10)  # Wait a bit before checking again, up to 1 minute
            continue
        else:
            previous_empty = 0

        print(f"Found {len(processing_set)} new files")

        for audio in processing_set:
            audio_file = all_audios[audio]
            result_file = results_dir / f"{audio}.json"

            audio_file = audio_file.resolve()
            print(f"Processing {audio_file}")

            try:
                result = stt_manager.process_file(audio_file)
            except Exception as e:
                print(f"Error processing {audio_file}")
                print(e)
                continue

            with result_file.open(mode="w", encoding="utf-8") as f:
                json.dump(result, f)


if __name__ == "__main__":
    main(Path("data"))
