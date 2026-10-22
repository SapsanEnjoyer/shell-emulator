"""Ядро эмулятора: выполнение команд без привязки к интерфейсу."""

import posixpath

from emulator.parser import ParseError, split_command
from emulator.vfs import TEXT, VfsError

MAX_EXIT_ARGS = 1
CAT_ARGS = 1
INDENT = "    "


class ShellError(Exception):
    """Ошибка выполнения команды эмулятора."""


class Shell:
    """Интерпретатор команд эмулятора оболочки."""

    def __init__(self, vfs):
        """Создать оболочку, работающую с виртуальной ФС vfs."""
        self.vfs = vfs
        self.cwd = "/"
        self.running = True
        self.exit_code = 0
        self.commands = {
            "ls": self._cmd_ls,
            "cd": self._cmd_cd,
            "exit": self._cmd_exit,
            "vfs": self._cmd_vfs,
        }
        self.vfs_commands = {
            "info": self._vfs_info,
            "tree": self._vfs_tree,
            "cat": self._vfs_cat,
        }

    @property
    def vfs_name(self):
        """Имя подключённой VFS."""
        return self.vfs.name

    def prompt(self):
        """Вернуть строку приглашения."""
        return f"user@{self.vfs_name}:{self.cwd}$ "

    def execute(self, line):
        """Выполнить строку команды и вернуть текст вывода.

        При ошибке разбора или выполнения возбуждается ShellError.
        """
        try:
            tokens = split_command(line)
        except ParseError as error:
            raise ShellError(f"синтаксическая ошибка: {error}") from error
        if not tokens:
            return ""
        name, args = tokens[0], tokens[1:]
        handler = self.commands.get(name)
        if handler is None:
            raise ShellError(f"{name}: команда не найдена")
        return handler(args)

    @staticmethod
    def _stub(name, args):
        """Вывод команды-заглушки: имя и полученные аргументы."""
        return f"команда: {name}, аргументы: {args}"

    def _cmd_ls(self, args):
        """Заглушка команды ls."""
        return self._stub("ls", args)

    def _cmd_cd(self, args):
        """Заглушка команды cd."""
        return self._stub("cd", args)

    def _cmd_exit(self, args):
        """Завершить работу эмулятора с необязательным кодом выхода."""
        if len(args) > MAX_EXIT_ARGS:
            raise ShellError("exit: слишком много аргументов")
        code = 0
        if args:
            try:
                code = int(args[0])
            except ValueError as error:
                raise ShellError(
                    f"exit: {args[0]}: требуется числовой аргумент"
                ) from error
        self.running = False
        self.exit_code = code
        return "exit"

    def _cmd_vfs(self, args):
        """Служебная команда: vfs info | vfs tree | vfs cat ПУТЬ."""
        if not args:
            raise ShellError("vfs: укажите подкоманду: info, tree, cat")
        handler = self.vfs_commands.get(args[0])
        if handler is None:
            raise ShellError(f"vfs: неизвестная подкоманда {args[0]}")
        try:
            return handler(args[1:])
        except VfsError as error:
            raise ShellError(f"vfs: {error}") from error

    def _vfs_info(self, args):
        """Сведения о подключённой VFS."""
        self._check_no_args("vfs info", args)
        dirs, files, size = self.vfs.stats()
        return "\n".join([
            f"имя: {self.vfs.name}",
            f"источник: {self.vfs.source or 'нет (пустая VFS в памяти)'}",
            f"каталогов: {dirs}, файлов: {files}, байт: {size}",
        ])

    def _vfs_tree(self, args):
        """Дерево всех файлов и каталогов VFS."""
        self._check_no_args("vfs tree", args)
        lines = []
        for path, node in self.vfs.walk():
            depth = len([part for part in path.split("/") if part])
            name = posixpath.basename(path) or "/"
            suffix = "/" if node.is_dir and path != "/" else ""
            lines.append(f"{INDENT * depth}{name}{suffix}")
        return "\n".join(lines)

    def _vfs_cat(self, args):
        """Содержимое файла VFS (двоичные данные в base64)."""
        if len(args) != CAT_ARGS:
            raise ShellError("vfs cat: требуется ровно один путь")
        node = self.vfs.resolve(args[0], self.cwd)
        if node.is_dir:
            raise ShellError(f"vfs cat: {args[0]}: это каталог")
        prefix = "[base64] " if node.encoding != TEXT else ""
        return prefix + node.text()

    @staticmethod
    def _check_no_args(name, args):
        """Проверить, что подкоманда вызвана без аргументов."""
        if args:
            raise ShellError(f"{name}: лишние аргументы {args}")
