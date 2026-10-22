#!/bin/sh
# Ошибки параметров: несуществующий скрипт, неизвестный ключ
cd "$(dirname "$0")/.." || exit 1
python3 tools/make_vfs.py
./run.sh --vfs vfs/deep.zip --script scripts/startup/missing.txt
./run.sh --unknown-option
echo "код возврата: $?"
