#!/bin/sh
# Только параметр --vfs: имя VFS попадает в заголовок окна
cd "$(dirname "$0")/.." || exit 1
python3 tools/make_vfs.py
./run.sh --vfs vfs/files.zip
