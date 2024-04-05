#!/usr/bin/env bash

set -efaoux pipefail

source .env_whisper > /dev/null 2>&1

set +a

set +ue
if [ "$STT_API_KEYS" ]
then
    echo "STT_API_KEYS is set to '$STT_API_KEYS'"
else
    echo "STT_API_KEYS is not set"
    echo "Aborting"
    exit 1
fi
set -ue

cd "${FOLDER:=`pwd`/}"

# Ensure pwd has worked
if [ -z "${FOLDER%/*}" ]
then
    echo "The pwd command failed, leading to cd to $FOLDER"
    exit 1
fi

if [ ! -d "venv" ]
then
    python3.11 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
fi

source "$FOLDER""/venv/bin/activate"

# Ensure that we have everything we need
for package in `cat requirements.txt`
do
    if $(echo $package | grep -q '@https')
    then
        echo "Skipping $package"
        continue
    fi
    if ! pip show $package > /dev/null
    then
        echo "Missing $package, trying to install it..."
        pip install $package
    fi
done

COMMAND="source $FOLDER/venv/bin/activate; python -m uvicorn api:app --host ${WHISPER_HOST:-'0.0.0.0'} --port ${WHISPER_PORT:-'5464'} --root-path ${ROOT_PATH:-'/'} --workers 4 --timeout-keep-alive 1000 --log-config log.conf"

printf "Starting whisper with command:\n"
echo "$COMMAND"

set +ue
IS_RUNNING=$(ps -aux | grep uvicorn | grep whisper_api)
if [ -z "$IS_RUNNING" ]
then
    set -ue
    echo "whisper service currently not running, starting gunicorn..."
    screen -S Whisper -dm bash -c "$COMMAND"
else
    set -ue
    echo "whisper already running, restarting..."
    screen -S Whisper -X quit
    screen -S Whisper -dm bash -c "$COMMAND"
fi

COMMAND="source $FOLDER/venv/bin/activate; python launcher_STT.py"

printf "Starting STT launcher with command:\n"
echo "$COMMAND"

set +ue
IS_RUNNING=$(ps -aux | grep launcher_STT.py)
if [ -z "$IS_RUNNING" ]
then
    set -ue
    echo "STT launcher service currently not running, starting..."
    screen -S STT -dm bash -c "$COMMAND"
else
    set -ue
    echo "STT launcher already running, restarting..."
    screen -S STT -X quit
    screen -S STT -dm bash -c "$COMMAND"
fi

cd -
