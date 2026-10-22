"""Тесты ядра оболочки."""

import unittest

from emulator.shell import Shell, ShellError


class ShellTest(unittest.TestCase):
    """Проверки выполнения команд."""

    def setUp(self):
        """Создать оболочку для каждого теста."""
        self.shell = Shell("test")

    def test_ls_stub(self):
        """ls выводит имя и аргументы."""
        out = self.shell.execute('ls -l "my dir"')
        self.assertEqual(out, "команда: ls, аргументы: ['-l', 'my dir']")

    def test_cd_stub(self):
        """cd выводит имя и аргументы."""
        self.assertEqual(
            self.shell.execute("cd /tmp"),
            "команда: cd, аргументы: ['/tmp']",
        )

    def test_empty_line(self):
        """Пустая строка ничего не выводит."""
        self.assertEqual(self.shell.execute(""), "")

    def test_unknown_command(self):
        """Неизвестная команда - ошибка."""
        with self.assertRaisesRegex(ShellError, "команда не найдена"):
            self.shell.execute("foo")

    def test_parse_error(self):
        """Синтаксическая ошибка передаётся как ShellError."""
        with self.assertRaisesRegex(ShellError, "синтаксическая"):
            self.shell.execute('ls "abc')

    def test_exit(self):
        """exit останавливает оболочку."""
        self.shell.execute("exit 3")
        self.assertFalse(self.shell.running)
        self.assertEqual(self.shell.exit_code, 3)

    def test_exit_bad_code(self):
        """exit с нечисловым аргументом - ошибка."""
        with self.assertRaisesRegex(ShellError, "числовой"):
            self.shell.execute("exit abc")
        self.assertTrue(self.shell.running)

    def test_exit_too_many(self):
        """exit с лишними аргументами - ошибка."""
        with self.assertRaisesRegex(ShellError, "слишком много"):
            self.shell.execute("exit 1 2")

    def test_prompt(self):
        """Приглашение содержит имя VFS."""
        self.assertEqual(self.shell.prompt(), "user@test:/$ ")


if __name__ == "__main__":
    unittest.main()
