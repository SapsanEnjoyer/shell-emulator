"""Разбор командной строки на аргументы с учётом кавычек."""

SINGLE_QUOTE = "'"
DOUBLE_QUOTE = '"'
ESCAPE = "\\"
QUOTES = (SINGLE_QUOTE, DOUBLE_QUOTE)
ESCAPABLE_IN_DOUBLE = (DOUBLE_QUOTE, ESCAPE, "$", "`")


class ParseError(Exception):
    """Ошибка синтаксиса командной строки."""


def _peek(line, pos):
    """Вернуть символ строки в позиции pos или пустую строку."""
    return line[pos] if pos < len(line) else ""


def _read_escape(line, pos, current):
    """Обработать экранирование вне кавычек, вернуть новую позицию."""
    char = _peek(line, pos + 1)
    if not char:
        raise ParseError("строка оканчивается символом '\\'")
    current.append(char)
    return pos + 2


def _read_quoted(line, start, current):
    """Прочитать содержимое в кавычках, вернуть позицию после них."""
    quote = line[start]
    pos = start + 1
    while pos < len(line):
        char = line[pos]
        if char == quote:
            return pos + 1
        next_char = _peek(line, pos + 1)
        escaped = (quote == DOUBLE_QUOTE and char == ESCAPE
                   and next_char in ESCAPABLE_IN_DOUBLE)
        if escaped:
            current.append(next_char)
            pos += 2
        else:
            current.append(char)
            pos += 1
    raise ParseError(f"незакрытая кавычка {quote}")


def split_command(line):
    """Разбить строку на аргументы как это делает UNIX-оболочка.

    Поддерживаются одинарные кавычки (без экранирования внутри),
    двойные кавычки (с экранированием \\" \\\\ \\$ \\`) и экранирование
    символов обратной косой чертой. Кавычки, примыкающие к тексту,
    склеиваются с ним в один аргумент: a"b c"d -> ['ab cd'].
    """
    tokens = []
    current = []
    in_token = False
    pos = 0
    while pos < len(line):
        char = line[pos]
        if char.isspace():
            if in_token:
                tokens.append("".join(current))
                current, in_token = [], False
            pos += 1
            continue
        in_token = True
        if char in QUOTES:
            pos = _read_quoted(line, pos, current)
        elif char == ESCAPE:
            pos = _read_escape(line, pos, current)
        else:
            current.append(char)
            pos += 1
    if in_token:
        tokens.append("".join(current))
    return tokens
