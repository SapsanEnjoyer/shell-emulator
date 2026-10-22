#!/bin/sh
# Оба параметра; скрипт с ошибкой останавливается на ней
cd "$(dirname "$0")/.." || exit 1
python3 tools/make_vfs.py
./run.sh --vfs vfs/deep.zip --script scripts/startup/error.txt
