# LOLCodeUI: main window. Only arranges the panels; each panel has its own file.
import tkinter as tk
import os
from tkinter import ttk
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from button_bar import ButtonBar
from console_panel import ConsolePanel
from file_explorer import FileExplorerPanel
from helpers import BG, FONT, PANEL
from lexemes_panel import LexemesPanel
from symbol_table_panel import SymbolTablePanel
from text_editor import TextEditorPanel
from backend.lexer import tokenize_code, classify

class LOLCodeUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("LOLCode Interpreter")
        self.geometry("1344x820")  # Increased height to accommodate button bar comfortably
        self.minsize(960, 640)     # Increased minimum height
        self.configure(bg=BG)
        ttk.Style(self).theme_use("clam")
        self._build()

    def _build(self):
        # Header frame at top left
        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", padx=16, pady=(10, 4), anchor="w")

        # Load PNG logo using built-in tk.PhotoImage
        self.logo_img = None

        try:
            self.logo_img = tk.PhotoImage(file="../assets/4Real_logo.png")
        except Exception:
            try:
                self.logo_img = tk.PhotoImage(file="assets/4Real_logo.png")
            except Exception:
                self.logo_img = None

        # Automatically scale down large images to fit header height (36px)
        if self.logo_img is not None:
            img_height = self.logo_img.height()
            
            if img_height > 50:
                scale_factor = img_height // 36
            
                if scale_factor > 1:
                    self.logo_img = self.logo_img.subsample(scale_factor, scale_factor)

            logo_label = tk.Label(header, image=self.logo_img, bg=BG)
            logo_label.pack(side="left", padx=(0, 10))

        # Title text stack
        title_frame = tk.Frame(header, bg=BG)
        title_frame.pack(side="left")

        tk.Label(title_frame, text="LOLCode", bg=BG, fg=PANEL,
                 font=(FONT, 16, "bold")).pack(anchor="w")
        
        tk.Label(title_frame, text="Interpreter", bg=BG, fg=PANEL,
                 font=(FONT, 10, "bold")).pack(anchor="w")

        # Pack the ButtonBar at the bottom FIRST so it is pinned and never clipped
        ButtonBar(self, self.on_execute, self.on_clear).pack(
            side="bottom", fill="x", padx=18, pady=(10, 14))

        # Grid of panels packed in the remaining top space
        main = tk.Frame(self, bg=BG)
        main.pack(side="top", fill="both", expand=True, padx=16)
        main.columnconfigure(0, weight=0, minsize=143)
        main.columnconfigure(1, weight=1)
        main.columnconfigure(2, weight=0, minsize=252)
        main.rowconfigure(0, weight=1, minsize=260)

        self.file_explorer = FileExplorerPanel(main)
        self.file_explorer.grid(row=0, column=0, sticky="nsew", padx=(0, 12), pady=(0, 12))

        self.text_editor = TextEditorPanel(main)
        self.text_editor.grid(row=0, column=1, sticky="nsew", padx=(0, 12), pady=(0, 12))

        self.file_explorer.tree.bind("<Double-1>", self._on_file_double_click)

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

    def _on_file_double_click(self, _event):
        path = self.file_explorer.get_selected_path()
        if path and os.path.isfile(path):
            self.text_editor.open_file(path)
            
    def on_execute(self):
            # Get code from the text editor
            code = self.text_editor.get_code()
            if not code.strip():
                self.console.write("Error: Editor is empty.\n")
                return

            # Clear old outputs
            self.console.clear()
            self.lexemes.clear()
            self.symbol_table.clear()

            try:
                # Split code into lines 
                lines = code.splitlines()
                
                # Tokenize using backend function
                tokenized_program = tokenize_code(lines)
                
                total_tokens = 0
                # Iterate through lines and tokens, then add them to the LexemesPanel table
                for line_number, line_tokens in tokenized_program:
                    for token in line_tokens:
                        category, sub_type = classify(token)
                        
                        # Determine display category based on your classifier logic
                        if category == "KEYWORD":
                            display_category = sub_type
                        elif category.startswith("Literal"):
                            display_category = category
                        else:
                            display_category = category

                        # Add row to the LexemesPanel treeview (Lexeme, Category)
                        self.lexemes.add_row(token, display_category)
                        total_tokens += 1

                self.console.write(f"Execution successful. Total tokens found: {total_tokens}\n")
                
            except Exception as e:
                self.console.write(f"Lexer Error: {str(e)}\n")

    def on_clear(self):
        self.console.clear()
        self.lexemes.clear()
        self.symbol_table.clear()
        self.console.write("Outputs cleared.\n")


