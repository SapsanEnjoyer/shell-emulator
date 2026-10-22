"""Графический интерфейс эмулятора на tkinter."""

import tkinter as tk
from tkinter import scrolledtext

from emulator.shell import ShellError

FONT = ("Menlo", 13)
WINDOW_SIZE = "860x520"
EXIT_DELAY_MS = 600
BACKGROUND = "#1e1e1e"
FOREGROUND = "#d4d4d4"
ERROR_COLOR = "#f48771"


class EmulatorWindow:
    """Окно эмулятора: область вывода и строка ввода команд."""

    def __init__(self, shell):
        """Построить окно для оболочки shell."""
        self.shell = shell
        self.root = tk.Tk()
        self.root.title(f"Эмулятор оболочки - [{shell.vfs_name}]")
        self.root.geometry(WINDOW_SIZE)
        self.output = scrolledtext.ScrolledText(
            self.root, font=FONT, wrap=tk.WORD, state=tk.DISABLED,
            bg=BACKGROUND, fg=FOREGROUND,
        )
        self.output.tag_configure("error", foreground=ERROR_COLOR)
        self.output.pack(fill=tk.BOTH, expand=True)
        frame = tk.Frame(self.root, bg=BACKGROUND)
        frame.pack(fill=tk.X)
        self.prompt_label = tk.Label(
            frame, text=shell.prompt(), font=FONT,
            bg=BACKGROUND, fg=FOREGROUND,
        )
        self.prompt_label.pack(side=tk.LEFT)
        self.entry = tk.Entry(
            frame, font=FONT, bg=BACKGROUND, fg=FOREGROUND,
            insertbackground=FOREGROUND,
        )
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry.bind("<Return>", self._on_enter)
        self.entry.focus_set()

    def write(self, text, tag=None):
        """Добавить строку текста в область вывода."""
        self.output.configure(state=tk.NORMAL)
        self.output.insert(tk.END, text + "\n", tag)
        self.output.configure(state=tk.DISABLED)
        self.output.see(tk.END)

    def write_error(self, text):
        """Вывести сообщение об ошибке."""
        self.write(text, "error")

    def run_line(self, line):
        """Выполнить команду с эхом ввода; вернуть False при ошибке."""
        self.write(self.shell.prompt() + line)
        try:
            result = self.shell.execute(line)
        except ShellError as error:
            self.write_error(f"Ошибка: {error}")
            return False
        if result:
            self.write(result)
        self.prompt_label.configure(text=self.shell.prompt())
        if not self.shell.running:
            self.entry.configure(state=tk.DISABLED)
            self.root.after(EXIT_DELAY_MS, self.root.destroy)
        return True

    def _on_enter(self, _event):
        """Обработать нажатие Enter в строке ввода."""
        line = self.entry.get()
        self.entry.delete(0, tk.END)
        self.run_line(line)

    def mainloop(self):
        """Запустить цикл обработки событий окна."""
        self.root.mainloop()
