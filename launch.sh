control_c() {
    kill "$PID"
    exit
}

term() {
    kill -SIGTERM "$PID"
    exit
}

trap control_c SIGINT
trap term SIGTERM


if [ ! -d "venv" ]; then
    python3.11 -m venv venv
    pip install -Ur requirements.txt
fi

if [ ! "$STT_API_KEYS" ]; then
    echo "STT_API_KEYS environment variable not set"
    exit 1
fi

source venv/bin/activate

python launcher_STT.py &
PID=$!
echo "Started STT launcher with PID $PID"

uvicorn api:app --port 5464 --host 0.0.0.0 --workers 4

