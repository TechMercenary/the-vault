import contextlib
import tkinter as tk
from tkinter import ttk
import pendulum


class TimestampEntry(ttk.Entry):
    def __init__(self, parent, format: str ='YYYY-MM-DD HH:mm:ss', local_tz: str = 'local', ignore_tz: bool = False, value: str = None, default_now: bool = False,  **kwargs):
        super().__init__(master=parent, **kwargs)
        self._format = format
        self._local_tz = local_tz
        self._ignore_tz = ignore_tz
        self.local_timestamp = None
        self.utc_timestamp = None
        
        if value:=value or (pendulum.now() if default_now else None):
            self.insert(tk.END, value)

        self.bind('<FocusOut>', self.parse_input)
        self.parse_input()

    def parse_input(self, event=None):
        input_str = self.get().strip()

        self.local_timestamp = ''
        self.utc_timestamp = ''

        with contextlib.suppress(ValueError):
            dt = pendulum.parse(input_str, tz=self._local_tz)
            self.local_timestamp = dt.format(self._format)
            self.utc_timestamp = self.local_timestamp if self._ignore_tz else dt.in_timezone('UTC').format(self._format)
            self.delete(0, tk.END)
            self.insert(tk.END, self.local_timestamp)

