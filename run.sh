#!/bin/sh
# Запуск эмулятора: ./run.sh [параметры]
# Предпочитается Python с современным Tk (Homebrew python-tk@3.13):
# системный Tk 8.5 в новых macOS показывает пустое окно.
cd "$(dirname "$0")" || exit 1
PYTHON=${PYTHON:-}
if [ -z "$PYTHON" ]; then
    for candidate in python3.13 python3; do
        if command -v "$candidate" >/dev/null 2>&1; then
            PYTHON=$candidate
            break
        fi
    done
fi
export TK_SILENCE_DEPRECATION=1
PYTHONPATH=src exec "$PYTHON" -m emulator "$@"
