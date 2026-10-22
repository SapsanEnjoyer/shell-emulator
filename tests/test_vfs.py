"""Тесты виртуальной файловой системы."""

import importlib
import os
import sys
import tempfile
import unittest

from emulator.shell import Shell, ShellError
from emulator.vfs import BASE64, TEXT, VfsError, VirtualFileSystem

TOOLS = os.path.join(os.path.dirname(__file__), "..", "tools")
sys.path.insert(0, TOOLS)
make_vfs = importlib.import_module("make_vfs")


class VfsTest(unittest.TestCase):
    """Загрузка VFS из сгенерированных архивов."""

    @classmethod
    def setUpClass(cls):
        """Создать тестовые архивы во временном каталоге."""
        cls.tmp = tempfile.TemporaryDirectory()
        make_vfs.main(["make_vfs", cls.tmp.name])

    @classmethod
    def tearDownClass(cls):
        """Удалить временный каталог."""
        cls.tmp.cleanup()

    def load(self, name):
        """Загрузить архив по имени."""
        path = os.path.join(self.tmp.name, name)
        return VirtualFileSystem.from_zip(path, name)

    def test_minimal(self):
        """Минимальная VFS содержит один файл."""
        self.assertEqual(self.load("minimal.zip").stats()[:2], (0, 1))

    def test_empty(self):
        """Пустой архив даёт пустую VFS."""
        self.assertEqual(self.load("empty.zip").stats(), (0, 0, 0))

    def test_files_binary(self):
        """Двоичный файл представляется в base64, текст - как есть."""
        vfs = self.load("files.zip")
        self.assertEqual(vfs.resolve("/image.png").encoding, BASE64)
        self.assertEqual(vfs.resolve("notes.txt").encoding, TEXT)

    def test_b64_entry_decoded(self):
        """Файл *.b64 из архива декодируется."""
        node = self.load("files.zip").resolve("logo.bin")
        self.assertEqual(node.content, make_vfs.BINARY_BLOB[:16])

    def test_deep(self):
        """Глубокая VFS: вложенность и пустые каталоги."""
        vfs = self.load("deep.zip")
        node = vfs.resolve("home/user/docs/2026/october/plan.txt")
        self.assertEqual(node.text(), "план на октябрь\n")
        self.assertTrue(vfs.resolve("/tmp").is_dir)
        self.assertTrue(vfs.resolve("docs/../docs", "/home/user").is_dir)

    def test_not_found(self):
        """Несуществующий путь - ошибка."""
        with self.assertRaises(VfsError):
            self.load("deep.zip").resolve("/nope")

    def test_file_as_dir(self):
        """Файл нельзя использовать как каталог."""
        with self.assertRaises(VfsError):
            self.load("deep.zip").resolve("/etc/hostname/x")

    def test_broken(self):
        """Повреждённый архив - ошибка."""
        with self.assertRaisesRegex(VfsError, "не является ZIP"):
            self.load("broken.zip")

    def test_missing(self):
        """Отсутствующий архив - ошибка."""
        with self.assertRaises(VfsError):
            self.load("missing.zip")

    def test_source_unchanged(self):
        """Загрузка не изменяет файл архива."""
        path = os.path.join(self.tmp.name, "deep.zip")
        before = os.path.getmtime(path), os.path.getsize(path)
        VirtualFileSystem.from_zip(path, "deep")
        self.assertEqual(before, (os.path.getmtime(path),
                                  os.path.getsize(path)))

    def test_vfs_commands(self):
        """Служебная команда vfs: info, tree, cat и ошибки."""
        shell = Shell(self.load("deep.zip"))
        self.assertIn("каталогов: 12, файлов: 7", shell.execute("vfs info"))
        self.assertIn("            october/", shell.execute("vfs tree"))
        self.assertEqual(shell.execute("vfs cat /etc/hostname"),
                         "emulator\n")
        binary = shell.execute("vfs cat home/user/docs/2026/october/data.bin")
        self.assertTrue(binary.startswith("[base64] iVBORw0KGgo"))
        for bad in ("vfs", "vfs foo", "vfs cat /etc", "vfs cat /nope"):
            with self.assertRaises(ShellError):
                shell.execute(bad)


if __name__ == "__main__":
    unittest.main()
