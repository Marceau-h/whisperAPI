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

uvicorn api:app --port 5464 --host 0.0.0.0 --workers 4
