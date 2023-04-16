import tkinter as tk
import pendulum
from tkinter import messagebox
from config import LOCAL_TIME_ZONE
from decimal import Decimal

# TODO: Deprecar
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


# TODO: Deprecar
class PendulumVar(tk.StringVar):
    """ A custom tkinter variable that uses pendulum to validate the data. """

    def __init__(self, master = None, format: str ='YYYY-MM-DD HH:mm:ss', tz: str = LOCAL_TIME_ZONE) -> None:
        super().__init__(master)
        self._format = format
        self._tz = tz

    def get(self) -> str:
        return pendulum.parse(super().get(), tz=LOCAL_TIME_ZONE)

    def set(self, value: str) -> None:
        super().set(pendulum.parse(value, tz=self._tz).format(self._format))

# TODO: Deprecar
class DecimalVar(tk.StringVar):
    def __init__(self, master = None, format: str = '0.01', **args) -> None:
        self._format = format
        super().__init__(master, **args)

    def get(self) -> Decimal:
        return Decimal(super().get()).quantize(Decimal(self._format))

    def set(self, value: int|str|float|Decimal) -> None:
        super().set(Decimal(value).quantize(Decimal(self._format)))
