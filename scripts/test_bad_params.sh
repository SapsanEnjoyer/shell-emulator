#!/bin/sh
# Ошибки параметров: несуществующий скрипт, неизвестный ключ
cd "$(dirname "$0")/.." || exit 1
./run.sh --vfs vfs/demo.zip --script scripts/startup/missing.txt
./run.sh --unknown-option
echo "код возврата: $?"
