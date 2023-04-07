import tkinter as tk
import pendulum

class PendulumVar(tk.StringVar):
    def __init__(self, master = None, format='YYYY-MM-DD HH:mm:ss') -> None:
        super().__init__(master)
        self._format = format

    def get(self):
        return pendulum.parse(super().get()).format(self._format)
