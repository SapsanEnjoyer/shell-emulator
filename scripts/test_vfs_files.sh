#!/bin/sh
# VFS с несколькими файлами, включая двоичные (base64)
cd "$(dirname "$0")/.." || exit 1
python3 tools/make_vfs.py
./run.sh --vfs vfs/files.zip --script scripts/startup/vfs_files.txt
