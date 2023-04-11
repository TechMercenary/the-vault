import tkinter as tk
import pendulum
from tkinter import messagebox
from config import LOCAL_TIME_ZONE

# TODO: Deprecarate
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
        
        if str_value:=super().get():
            try:
                return pendulum.parse(str_value).format(self._format)
            except Exception as e:
                messagebox.showerror("Error", f"Datetime `{str_value}` could not be parsed to {self._format}")
        return None
    
    
class PendulumVar(tk.StringVar):
    """ A custom tkinter variable that uses pendulum to validate the data. """
    
    def __init__(self, master = None) -> None:
        super().__init__(master)

    def get(self) -> str | None:
        return pendulum.parse(super().get(), tz=LOCAL_TIME_ZONE)



class DecimalVar(tk.StringVar):
    def __init__(self, master = None, decimal: int = 2, value=None) -> None:
        self._decimals = decimal
        if value:
            super().__init__(master, value=value)    
        else:
            super().__init__(master)

    def get(self) -> float | None:
        """ 
            Returns the value of the variable in the format specified in the constructor,
            or None if the value couldn't be parsed
        """
        
        str_value = super().get()
        if str_value != '':
            try:
                return f"{float(str_value):.{self._decimals}f}"
            except Exception as e:
                messagebox.showerror("Error", f"Decimal `{str_value}` could not be parsed to float")
        return None

   