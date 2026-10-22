#!/bin/sh
# Только параметр --vfs: имя VFS попадает в заголовок окна
cd "$(dirname "$0")/.." || exit 1
./run.sh --vfs vfs/my_disk.zip
