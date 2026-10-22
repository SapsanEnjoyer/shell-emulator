"""Точка входа: python -m emulator [--vfs PATH] [--script PATH]."""

import sys

from emulator.config import parse_args
from emulator.gui import EmulatorWindow
from emulator.shell import Shell
from emulator.vfs import VfsError, VirtualFileSystem


def load_vfs(config):
    """Загрузить VFS из архива; вернуть (vfs, сообщение об ошибке)."""
    if not config.vfs_path:
        return VirtualFileSystem(config.vfs_name), None
    try:
        return VirtualFileSystem.from_zip(
            config.vfs_path, config.vfs_name), None
    except VfsError as error:
        return VirtualFileSystem(config.vfs_name), str(error)


def main(argv=None):
    """Запустить эмулятор с параметрами командной строки."""
    config = parse_args(argv)
    vfs, vfs_error = load_vfs(config)
    shell = Shell(vfs)
    window = EmulatorWindow(shell)
    for line in config.describe():
        print(line, flush=True)
        window.write(line)
    if vfs_error:
        print(f"Ошибка VFS: {vfs_error}", file=sys.stderr)
        window.write_error(f"Ошибка VFS: {vfs_error}")
        window.write_error("Используется пустая VFS, скрипт не выполняется")
    elif config.script_path:
        window.root.after_idle(window.run_script, config.script_path)
    window.mainloop()
    return shell.exit_code


if __name__ == "__main__":
    sys.exit(main())
