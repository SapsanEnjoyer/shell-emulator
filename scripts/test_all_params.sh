#!/bin/sh
# Оба параметра; скрипт с ошибкой останавливается на ней
cd "$(dirname "$0")/.." || exit 1
./run.sh --vfs vfs/demo.zip --script scripts/startup/error.txt
