"""Параметры командной строки эмулятора."""

import argparse
import os
from dataclasses import dataclass
from typing import Optional

DEFAULT_VFS_NAME = "vfs"


@dataclass
class Config:
    """Настройки запуска эмулятора."""

    vfs_path: Optional[str] = None
    script_path: Optional[str] = None

    @property
    def vfs_name(self):
        """Имя VFS: имя файла без расширения либо имя по умолчанию."""
        if not self.vfs_path:
            return DEFAULT_VFS_NAME
        base = os.path.basename(os.path.normpath(self.vfs_path))
        return os.path.splitext(base)[0] or DEFAULT_VFS_NAME

    def describe(self):
        """Вернуть строки отладочного вывода всех параметров."""
        return [
            "[debug] параметры запуска:",
            f"[debug]   vfs_path    = {self.vfs_path!r}",
            f"[debug]   vfs_name    = {self.vfs_name!r}",
            f"[debug]   script_path = {self.script_path!r}",
        ]


def build_parser():
    """Создать парсер аргументов командной строки."""
    parser = argparse.ArgumentParser(
        prog="emulator",
        description="Эмулятор командной оболочки UNIX с GUI",
    )
    parser.add_argument(
        "--vfs", dest="vfs_path", metavar="PATH",
        help="путь к физическому расположению VFS",
    )
    parser.add_argument(
        "--script", dest="script_path", metavar="PATH",
        help="путь к стартовому скрипту эмулятора",
    )
    return parser


def parse_args(argv=None):
    """Разобрать аргументы командной строки и вернуть Config."""
    namespace = build_parser().parse_args(argv)
    return Config(namespace.vfs_path, namespace.script_path)
