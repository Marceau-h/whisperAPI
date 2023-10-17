from multiprocessing import Process

def errormaker():
    return 1

def main():
    p = Process(target=errormaker)
    p.start()

    p.join()
    print(p.is_alive())
    print(p.exitcode)
    print(p.pid)
    print(p)

if __name__ == "__main__":
    main()
