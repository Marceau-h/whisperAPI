source ./venv/bin/activate

python launcher_STT.py &

uvicorn api:app --port 5464
