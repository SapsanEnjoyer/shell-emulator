"""Тесты разбора командной строки."""

import unittest

from emulator.parser import ParseError, split_command


class SplitCommandTest(unittest.TestCase):
    """Проверки функции split_command."""

    def test_simple(self):
        """Аргументы разделяются пробелами."""
        self.assertEqual(split_command("ls -l  /home"), ["ls", "-l", "/home"])

    def test_empty(self):
        """Пустая строка даёт пустой список."""
        self.assertEqual(split_command("   "), [])

    def test_double_quotes(self):
        """Двойные кавычки объединяют слова."""
        self.assertEqual(split_command('cd "my dir"'), ["cd", "my dir"])

    def test_single_quotes(self):
        """В одинарных кавычках обратная черта не экранирует."""
        self.assertEqual(split_command(r"ls 'a\b c'"), ["ls", r"a\b c"])

    def test_escape_in_double_quotes(self):
        """Экранированная кавычка внутри двойных кавычек."""
        self.assertEqual(split_command(r'ls "a \"b\""'), ["ls", 'a "b"'])

    def test_glued_quotes(self):
        """Кавычки, примыкающие к тексту, склеиваются в один аргумент."""
        self.assertEqual(split_command('ls a"b c"d'), ["ls", "ab cd"])

    def test_empty_quotes(self):
        """Пустые кавычки дают пустой аргумент."""
        self.assertEqual(split_command("cd ''"), ["cd", ""])

    def test_backslash_space(self):
        """Экранированный пробел не разделяет аргументы."""
        self.assertEqual(split_command(r"cd my\ dir"), ["cd", "my dir"])

    def test_unclosed_quote(self):
        """Незакрытая кавычка - ошибка."""
        with self.assertRaises(ParseError):
            split_command('ls "abc')

    def test_trailing_backslash(self):
        """Обратная черта в конце строки - ошибка."""
        with self.assertRaises(ParseError):
            split_command("ls abc\\")


if __name__ == "__main__":
    unittest.main()
