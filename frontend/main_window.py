# LOLCodeUI: main window. Only arranges the panels; each panel has its own file.
import tkinter as tk
from tkinter import ttk

from button_bar import ButtonBar
from console_panel import ConsolePanel
from file_explorer import FileExplorerPanel
from lexemes_panel import LexemesPanel
from symbol_table_panel import SymbolTablePanel
from text_editor import TextEditorPanel
from helpers import BG, FONT, PANEL


class LOLCodeUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("LOLCode Interpreter")
        self.geometry("1344x760")
        self.minsize(960, 540)
        self.configure(bg=BG)
        ttk.Style(self).theme_use("clam")
        self._build()

    def _build(self):
        # Title
        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", padx=137, pady=(10, 4), anchor="w")
        tk.Label(header, text="LOLCode", bg=BG, fg=PANEL,
                 font=(FONT, 16, "bold")).pack(anchor="w")
        tk.Label(header, text="Interpreter", bg=BG, fg=PANEL,
                 font=(FONT, 10, "bold")).pack(anchor="w")

        # Grid of panels
        main = tk.Frame(self, bg=BG)
        main.pack(fill="both", expand=True, padx=16)
        main.columnconfigure(0, weight=0, minsize=143)
        main.columnconfigure(1, weight=1)
        main.columnconfigure(2, weight=0, minsize=252)
        main.rowconfigure(0, weight=1, minsize=260)

        self.file_explorer = FileExplorerPanel(main)
        self.file_explorer.grid(row=0, column=0, sticky="nsew", padx=(0, 12), pady=(0, 12))

        self.text_editor = TextEditorPanel(main)
        self.text_editor.grid(row=0, column=1, sticky="nsew", padx=(0, 12), pady=(0, 12))

        right = tk.Frame(main, bg=BG)
        right.grid(row=0, column=2, sticky="nsew", pady=(0, 12))
        right.columnconfigure(0, weight=1)
        right.rowconfigure(0, weight=5, uniform="r")
        right.rowconfigure(1, weight=4, uniform="r")

        self.lexemes = LexemesPanel(right)
        self.lexemes.grid(row=0, column=0, sticky="nsew", pady=(0, 10))

        self.symbol_table = SymbolTablePanel(right)
        self.symbol_table.grid(row=1, column=0, sticky="nsew")

        self.console = ConsolePanel(main)
        self.console.grid(row=1, column=0, columnspan=3, sticky="nsew")

        ButtonBar(self, self.on_execute, self.on_clear).pack(
            fill="x", padx=18, pady=(10, 14))

    # Placeholders for future functionality
    def on_execute(self):
        pass

    def on_clear(self):
        pass