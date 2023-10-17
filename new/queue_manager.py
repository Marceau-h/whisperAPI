from pathlib import Path
import json
from multiprocessing import Lock
from time import sleep

# Only for reference
results_dir = "results"
to_process_dir = "to_process"
processing = "processing.json"
done = "done.json"

def main(folder: Path, lock: Lock):

    results_dir = folder / "results"
    to_process_dir = folder / "to_process"

    results_dir.mkdir(exist_ok=True, parents=True)
    to_process_dir.mkdir(exist_ok=True)

    processing = folder / "processing.json"
    done = folder / "done.json"

    lock.acquire()
    with processing.open(mode="w", encoding="utf-8") as f:
        json.dump([], f)
        process_list = []

    if done.exists():
        with done.open(mode="r", encoding="utf-8") as f:
            done_list = json.load(f)
    else:
        done_list = []

    lock.release()


    while True:
        if True:
            to_process = {e.stem for e in to_process_dir.glob("*.wav")}
            new_process = to_process - set(process_list)

            if not new_process:
                print("No more files to process, goin eepy")
                sleep(30)
            else:
                print(f"Processing {len(new_process)} files")

                lock.acquire()
                with processing.open(mode="r", encoding="utf-8") as f:
                    process_list = json.load(f)

                process_list.extend(new_process)

                with processing.open(mode="w", encoding="utf-8") as f:
                    json.dump(process_list, f)

                lock.release()

        results = {e.stem for e in results_dir.glob("*.json")}
        new_results = results - set(done_list)

        if not new_results:
            print("No new results, sleeping")
            sleep(30)
            continue

        lock.acquire()
        with done.open(mode="r", encoding="utf-8") as f:
            done_list = json.load(f)

        done_list.extend(new_results)

        with done.open(mode="w", encoding="utf-8") as f:
            json.dump(done_list, f)

        with processing.open(mode="r", encoding="utf-8") as f:
            process_list = json.load(f)

        process_list = [e for e in process_list if e not in done_list] # A little safer than new_results

        with processing.open(mode="w", encoding="utf-8") as f:
            json.dump(process_list, f)


        for e in new_results:
            print(f"New result: {e}")
            to_process_dir.joinpath(f"{e}.wav").unlink()

        lock.release()



if __name__ == "__main__":
    lock = Lock()
    main(Path("data"), lock)













