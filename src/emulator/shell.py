"""Ядро эмулятора: выполнение команд без привязки к интерфейсу."""

from emulator.parser import ParseError, split_command

MAX_EXIT_ARGS = 1


class ShellError(Exception):
    """Ошибка выполнения команды эмулятора."""


class Shell:
    """Интерпретатор команд эмулятора оболочки."""

    def __init__(self, vfs_name):
        """Создать оболочку, работающую с VFS по имени vfs_name."""
        self.vfs_name = vfs_name
        self.cwd = "/"
        self.running = True
        self.exit_code = 0
        self.commands = {
            "ls": self._cmd_ls,
            "cd": self._cmd_cd,
            "exit": self._cmd_exit,
        }

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
