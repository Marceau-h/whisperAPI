from multiprocessing import Process, Lock
from pathlib import Path
from time import sleep

from new.queue_manager import main as queue_main
from new.launcher_STT import main as launcher_main
from new.api import main as api_main

if __name__ == "__main__":
    lock = Lock()

    datafolder = Path("data")

    queue_process = Process(target=queue_main, args=(datafolder, lock))
    queue_process.daemon = True
    queue_process.start()

    sleep(5)

    launcher_process = Process(target=launcher_main, args=(datafolder, lock))
    launcher_process.daemon = True
    launcher_process.start()

    sleep(5)

    api_process = Process(target=api_main)
    api_process.daemon = True
    api_process.start()


    while True:
        sleep(1)
        for p in [queue_process, launcher_process, api_process]:
            if not p.is_alive():
                print(f"{p.name} is dead")
                break

