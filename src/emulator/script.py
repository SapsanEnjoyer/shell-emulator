"""Чтение стартовых скриптов эмулятора."""

COMMENT = "#"


class ScriptError(Exception):
    """Ошибка чтения стартового скрипта."""


def load_script(path):
    """Прочитать скрипт и вернуть список пар (номер строки, команда).

    Пустые строки и строки-комментарии (начинаются с #) пропускаются.
    """
    try:
        with open(path, encoding="utf-8") as file:
            lines = file.read().splitlines()
    except OSError as error:
        raise ScriptError(
            f"не удалось прочитать скрипт {path}: {error.strerror}"
        ) from error
    except UnicodeDecodeError as error:
        raise ScriptError(f"скрипт {path} не в кодировке UTF-8") from error
    commands = []
    for number, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped and not stripped.startswith(COMMENT):
            commands.append((number, stripped))
    return commands
