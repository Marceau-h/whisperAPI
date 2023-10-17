source ./venv/bin/activate

python launcher_STT.py &

uvicorn api:app --port 5464 --host 0.0.0.0 --workers 4
