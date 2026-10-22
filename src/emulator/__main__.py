"""Точка входа: python -m emulator."""

import sys

from emulator.gui import EmulatorWindow
from emulator.shell import Shell

DEFAULT_VFS_NAME = "vfs"


def main():
    """Запустить эмулятор в интерактивном режиме."""
    shell = Shell(DEFAULT_VFS_NAME)
    window = EmulatorWindow(shell)
    window.mainloop()
    return shell.exit_code


if __name__ == "__main__":
    sys.exit(main())
