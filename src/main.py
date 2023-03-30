from tkinter import ttk
from menu import AppMenu
from utils import center_window
from config import logger
import tkinter as tk

# import pathlib;
# PROJECT_PATH = pathlib.Path(__file__).parent

class App(tk.Tk):
    """A financial accounting application."""

    def __init__(self) -> None:
        super().__init__()
        self.option_add('*tearOff', False)
        self.title("The Vault")
        self.geometry("1000x600")
        self.create_widgets()

    def create_widgets(self) -> None:
        self.create_menu()

    def create_menu(self) -> None:
        self.menu = AppMenu(self)
        self.config(menu=self.menu)

    def run(self):
        center_window(window=self, context_window=None)
        self.mainloop()

if __name__ == '__main__':
    try:
        app = App()
        app.run()
    except Exception as e:
        logger.exception(e)

