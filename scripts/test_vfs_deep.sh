#!/bin/sh
# VFS с вложенностью более 3 уровней: все команды этапов 1-3
cd "$(dirname "$0")/.." || exit 1
python3 tools/make_vfs.py
./run.sh --vfs vfs/deep.zip --script scripts/startup/vfs_demo.txt
