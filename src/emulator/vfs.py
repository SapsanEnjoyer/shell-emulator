"""Виртуальная файловая система, загружаемая из ZIP-архива в память."""

import base64
import binascii
import io
import posixpath
import zipfile

ROOT = "/"
SEPARATOR = "/"
TEXT = "text"
BASE64 = "base64"
BASE64_SUFFIX = ".b64"
SKIPPED_PARTS = ("", ".")


class VfsError(Exception):
    """Ошибка работы с виртуальной файловой системой."""


class VfsNode:
    """Узел VFS: каталог или файл."""

    def __init__(self, name, is_dir, content=b""):
        """Создать узел; content - байты файла (для каталога пусто)."""
        self.name = name
        self.is_dir = is_dir
        self.content = content
        self.children = {}

    @property
    def size(self):
        """Размер файла в байтах (для каталога 0)."""
        return len(self.content)

    @property
    def encoding(self):
        """Представление содержимого: text или base64 для двоичных."""
        try:
            self.content.decode("utf-8")
        except UnicodeDecodeError:
            return BASE64
        return TEXT

    def text(self):
        """Содержимое файла как текст; двоичные данные - в base64."""
        if self.encoding == TEXT:
            return self.content.decode("utf-8")
        return base64.b64encode(self.content).decode("ascii")


def _split(path):
    """Разбить путь на значимые компоненты."""
    return [part for part in path.split(SEPARATOR)
            if part not in SKIPPED_PARTS]


def _decode_entry(name, data):
    """Вернуть имя и байты файла; *.b64 декодируются из base64."""
    if not name.endswith(BASE64_SUFFIX):
        return name, data
    try:
        return name[:-len(BASE64_SUFFIX)], base64.b64decode(
            data, validate=True)
    except (binascii.Error, ValueError) as error:
        raise VfsError(f"{name}: некорректные данные base64") from error


class VirtualFileSystem:
    """Дерево файлов и каталогов, полностью находящееся в памяти."""

    def __init__(self, name, source=None):
        """Создать пустую VFS с именем name."""
        self.name = name
        self.source = source
        self.root = VfsNode(ROOT, True)

    @classmethod
    def from_zip(cls, path, name):
        """Загрузить VFS из ZIP-архива, не распаковывая его на диск."""
        try:
            with open(path, "rb") as file:
                data = file.read()
        except OSError as error:
            raise VfsError(
                f"не удалось открыть VFS {path}: {error.strerror}"
            ) from error
        vfs = cls(name, path)
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as archive:
                for info in archive.infolist():
                    vfs._add_entry(archive, info)
        except zipfile.BadZipFile as error:
            raise VfsError(f"{path}: файл не является ZIP-архивом") from error
        return vfs

    def _add_entry(self, archive, info):
        """Добавить в дерево запись архива."""
        parts = _split(info.filename)
        if not parts:
            return
        if ".." in parts:
            raise VfsError(f"недопустимый путь в архиве: {info.filename}")
        parent = self._make_dirs(parts[:-1])
        if info.is_dir():
            self._make_dirs(parts)
            return
        name, content = _decode_entry(parts[-1], archive.read(info))
        if name in parent.children:
            raise VfsError(f"дублирующийся путь в архиве: {info.filename}")
        parent.children[name] = VfsNode(name, False, content)

    def _make_dirs(self, parts):
        """Создать (при необходимости) цепочку каталогов, вернуть последний."""
        node = self.root
        for part in parts:
            child = node.children.get(part)
            if child is None:
                child = VfsNode(part, True)
                node.children[part] = child
            elif not child.is_dir:
                raise VfsError(f"{part}: файл и каталог с одним именем")
            node = child
        return node

    def resolve(self, path, cwd=ROOT):
        """Найти узел по абсолютному или относительному пути."""
        full = posixpath.normpath(posixpath.join(cwd, path))
        node = self.root
        for part in _split(full):
            if not node.is_dir:
                raise VfsError(f"{path}: не является каталогом")
            node = node.children.get(part)
            if node is None:
                raise VfsError(f"{path}: нет такого файла или каталога")
        return node

    def walk(self, node=None, path=ROOT):
        """Обойти дерево, возвращая пары (путь, узел) в порядке имён."""
        node = node or self.root
        yield path, node
        for name in sorted(node.children):
            child = node.children[name]
            yield from self.walk(child, posixpath.join(path, name))

    def stats(self):
        """Вернуть (число каталогов без корня, число файлов, байт)."""
        nodes = [node for _, node in self.walk()][1:]
        dirs = sum(1 for node in nodes if node.is_dir)
        files = [node for node in nodes if not node.is_dir]
        return dirs, len(files), sum(node.size for node in files)
