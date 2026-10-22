#!/bin/sh
# Ошибки VFS: пустой архив, повреждённый архив, отсутствующий файл
cd "$(dirname "$0")/.." || exit 1
python3 tools/make_vfs.py
./run.sh --vfs vfs/empty.zip --script scripts/startup/vfs_errors.txt
./run.sh --vfs vfs/broken.zip --script scripts/startup/basic.txt
./run.sh --vfs vfs/missing.zip
