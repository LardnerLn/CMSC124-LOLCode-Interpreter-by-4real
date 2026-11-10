# Console panel 
import threading
import tkinter as tk
from rounded_panel import RoundedPanel

TITLE = "Console"
HEADER_COLOR = "#FF6B2C"
TITLE_COLOR = "#000000"
BODY_COLOR = "#DFD6BB"
TEXT_COLOR = "#2B2B2B"
FONT = ("Courier", 10)


class ConsolePanel(RoundedPanel):
    def __init__(self, parent):
        super().__init__(parent, TITLE, HEADER_COLOR, title_color=TITLE_COLOR,
                         title_size=13, header_h=36, height=210)
        self.text = tk.Text(self.body, bg=BODY_COLOR, fg=TEXT_COLOR, relief="flat",
                            font=FONT, state="disabled", bd=0, padx=6, pady=4)
        self.text.pack(fill="both", expand=True)

        self._input_event = threading.Event()  # Wait signal for input
        self._input_value = "" # Stores entered text
        self._input_start_index = None # Input start index

        self.text.bind("<Return>", self._on_enter)  # Bind Enter key

    def write(self, message):
        self.text.configure(state="normal")
        self.text.insert("end", message)
        self.text.see("end")
        self.text.configure(state="disabled")

    def clear(self):
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        self.text.configure(state="disabled")

    def prompt_inline_input(self, prompt_text):
        self.text.configure(state="normal")
        self.text.insert("end", prompt_text)
        self.text.see("end")

        self._input_start_index = self.text.index("insert") # Mark prompt end
        self._input_event.clear() # Reset wait signal
        self._input_value = "" # Reset value

        self._input_event.wait() # Pause execution thread
        self.text.configure(state="disabled")
        return self._input_value

    def _on_enter(self, event):
        if self._input_start_index is not None:
            self._input_value = self.text.get(self._input_start_index, "end-1c")  # Read typed text
            self._input_start_index = None
            self.text.insert("end", "\n")

            self._input_event.set()  # Resume execution thread
            return "break"           # Prevent extra newline