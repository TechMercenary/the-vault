import tkinter as tk
import pendulum
from tkinter import messagebox


class PendulumVar(tk.StringVar):
    def __init__(self, master = None, format='YYYY-MM-DD HH:mm:ss') -> None:
        super().__init__(master)
        self._format = format

    def get(self):
        str_value = super().get()
        if str_value != '':
            try:
                return pendulum.parse(str_value).format(self._format)
            except Exception as e:
                messagebox.showerror("Error", f"Datetime `{str_value}` could not be parsed to {self.format}")
        return None
