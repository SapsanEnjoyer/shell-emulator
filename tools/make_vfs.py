"""Генерация тестовых ZIP-архивов VFS в каталог vfs/.

Архивы не хранятся в репозитории, а создаются этим скриптом:
python3 tools/make_vfs.py [КАТАЛОГ]
"""

import base64
import os
import sys
import zipfile

DEFAULT_DIR = "vfs"
PNG_HEADER = bytes([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A])
BINARY_BLOB = PNG_HEADER + bytes(range(256))

MINIMAL = {
    "readme.txt": "Минимальная VFS: один файл.\n",
}

FILES = {
    "readme.txt": "VFS с несколькими файлами.\n",
    "notes.txt": "первая строка\nвторая строка\nтретья строка\n",
    "my file.txt": "файл с пробелом в имени\n",
    "image.png": BINARY_BLOB,
    "logo.bin.b64": base64.b64encode(BINARY_BLOB[:16]).decode("ascii"),
}

DEEP = {
    "etc/hostname": "emulator\n",
    "etc/config/app.conf": "debug=true\nlevel=3\n",
    "home/user/readme.txt": "домашний каталог пользователя\n",
    "home/user/docs/report.txt": "отчёт\n",
    "home/user/docs/2026/october/plan.txt": "план на октябрь\n",
    "home/user/docs/2026/october/data.bin": BINARY_BLOB,
    "home/guest/": None,
    "var/log/app/today.log": "INFO start\nINFO stop\n",
    "tmp/": None,
}

ARCHIVES = {
    "minimal.zip": MINIMAL,
    "files.zip": FILES,
    "deep.zip": DEEP,
    "empty.zip": {},
}


def write_archive(path, entries):
    """Записать ZIP-архив; None означает пустой каталог."""
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, content in entries.items():
            if content is None:
                archive.writestr(zipfile.ZipInfo(name), b"")
            elif isinstance(content, str):
                archive.writestr(name, content.encode("utf-8"))
            else:
                archive.writestr(name, content)


def main(argv):
    """Создать все тестовые архивы и один повреждённый файл."""
    target = argv[1] if argv[1:] else DEFAULT_DIR
    os.makedirs(target, exist_ok=True)
    for name, entries in ARCHIVES.items():
        write_archive(os.path.join(target, name), entries)
    with open(os.path.join(target, "broken.zip"), "w") as file:
        file.write("это не zip-архив\n")
    print(f"тестовые VFS созданы в {target}/")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
