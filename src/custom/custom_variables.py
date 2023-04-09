import tkinter as tk
import pendulum
from tkinter import messagebox


class DateTimeVar(tk.StringVar):
    """ A custom tkinter variable that uses pendulum to validate the data. """
    
    def __init__(self, master = None, format='YYYY-MM-DD HH:mm:ss') -> None:
        super().__init__(master)
        self._format = format

    def get(self) -> str | None:
        """ 
            Returns the value of the variable in the format specified in the constructor,
            or None if the value couldn't be parsed by pendulum.
        """
        
        str_value = super().get()
        if str_value != '':
            try:
                return pendulum.parse(str_value).format(self._format)
            except Exception as e:
                messagebox.showerror("Error", f"Datetime `{str_value}` could not be parsed to {self._format}")
        return None
