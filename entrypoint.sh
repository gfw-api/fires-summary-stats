#!/bin/bash
set -e

case "$1" in
    develop)
        echo "Running Development Server"
        exec python main.py
        ;;
    test)
        echo "Test"
        ;;
    start)
        echo "Running Start"
        exec gunicorn -c gunicorn.py fires:app
        ;;
    *)
        exec "$@"
esac
