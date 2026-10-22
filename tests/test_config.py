"""Тесты параметров командной строки и загрузки скриптов."""

import os
import tempfile
import unittest

from emulator.config import DEFAULT_VFS_NAME, parse_args
from emulator.script import ScriptError, load_script


class ConfigTest(unittest.TestCase):
    """Проверки разбора параметров."""

    def test_defaults(self):
        """Без параметров используются значения по умолчанию."""
        config = parse_args([])
        self.assertIsNone(config.vfs_path)
        self.assertIsNone(config.script_path)
        self.assertEqual(config.vfs_name, DEFAULT_VFS_NAME)

    def test_all_params(self):
        """Оба параметра сохраняются, имя VFS берётся из файла."""
        config = parse_args(["--vfs", "data/disk.zip", "--script", "s.txt"])
        self.assertEqual(config.vfs_path, "data/disk.zip")
        self.assertEqual(config.script_path, "s.txt")
        self.assertEqual(config.vfs_name, "disk")

    def test_describe(self):
        """Отладочный вывод содержит все параметры."""
        text = "\n".join(parse_args(["--vfs", "a.zip"]).describe())
        self.assertIn("vfs_path    = 'a.zip'", text)
        self.assertIn("script_path = None", text)

    def test_unknown_option(self):
        """Неизвестный параметр приводит к ошибке."""
        with self.assertRaises(SystemExit):
            parse_args(["--bad"])


class LoadScriptTest(unittest.TestCase):
    """Проверки чтения стартового скрипта."""

    def test_skips_comments(self):
        """Комментарии и пустые строки пропускаются с учётом номеров."""
        with tempfile.NamedTemporaryFile(
            "w", suffix=".txt", delete=False, encoding="utf-8"
        ) as file:
            file.write("# c\n\nls a\n  cd b  \n")
        self.addCleanup(os.remove, file.name)
        self.assertEqual(load_script(file.name), [(3, "ls a"), (4, "cd b")])

    def test_missing(self):
        """Отсутствующий файл - ошибка."""
        with self.assertRaises(ScriptError):
            load_script("/no/such/script.txt")


if __name__ == "__main__":
    unittest.main()
