#!/bin/sh
# VFS из минимального архива (один файл)
cd "$(dirname "$0")/.." || exit 1
python3 tools/make_vfs.py
./run.sh --vfs vfs/minimal.zip --script scripts/startup/vfs_minimal.txt
