"""Точка входа: python -m emulator [--vfs PATH] [--script PATH]."""

import sys

from emulator.config import parse_args
from emulator.gui import EmulatorWindow
from emulator.shell import Shell


def main(argv=None):
    """Запустить эмулятор с параметрами командной строки."""
    config = parse_args(argv)
    shell = Shell(config.vfs_name)
    window = EmulatorWindow(shell)
    for line in config.describe():
        print(line)
        window.write(line)
    if config.script_path:
        window.root.after_idle(window.run_script, config.script_path)
    window.mainloop()
    return shell.exit_code


if __name__ == "__main__":
    sys.exit(main())
