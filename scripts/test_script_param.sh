#!/bin/sh
# Только параметр --script: выполняется стартовый скрипт
cd "$(dirname "$0")/.." || exit 1
./run.sh --script scripts/startup/basic.txt
