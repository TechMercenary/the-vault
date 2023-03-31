from typing import Callable
from utils import center_window, handle_db_errors
from database.sqlite_handler import DB
from tkinter import messagebox
from functools import partial
from custom_widgets.table import CustomTable
from custom_widgets.toplevel import CustomTopLvel
import tkinter as tk
import tkinter.ttk as ttk
from config import logger


class CurrencyListView(CustomTopLvel):
    """A view for the currencies."""

    def __init__(self, parent: tk.Toplevel | tk.Tk):
        super().__init__(parent, title="Monedas")
        
        buttons_frame = self.get_buttons_frame(parent=self.main_frame)
        buttons_frame.grid(column=0, row=1, sticky="ew")
        buttons_frame.grid_anchor("center")
        buttons_frame.columnconfigure("all", pad=15)
        
        treeview_frame = self.get_treeview_frame(parent=self.main_frame)
        treeview_frame.grid(column=0, row=2, sticky="ew")
        
        close_frame = self.get_close_frame(parent=self.main_frame)
        close_frame.grid(column=0, row=3, sticky="ew")
        close_frame.grid_anchor("center")
        
        center_window(window=self, context_window=self.parent)
        self.bind("<<NewCurrencyAdded>>", self.update_table)
        self.bind("<<CurrencyDeleted>>", self.update_table)
        self.bind("<<CurrencyEdited>>", self.update_table)
        
        self.bind('<Delete>', self.btn_delete_currency)
        self.bind('<F2>', self.btn_edit_currency)
        self.bind('<Double-1>', self.btn_edit_currency)
        self.bind('<Return>', self.btn_edit_currency)

    def get_buttons_frame(self, parent):
        """Create the buttons frame."""

        buttons_frame = ttk.Frame(parent, padding=10)
        ttk.Button(buttons_frame, text='Nueva Moneda', command=self.btn_new_currency).grid(column=0, row=0)
        ttk.Button(buttons_frame, text='Editar', command=self.btn_edit_currency).grid(column=1, row=0)
        ttk.Button(buttons_frame, text='Borrar', command=self.btn_delete_currency).grid(column=2, row=0)
        return buttons_frame

    def get_currencies_from_db(self):
        """Get the currencies from the database."""

        return DB.get_currencies()['result']

    def update_table(self, event):
        """Update the table with the latest data from the database."""
        data=self.get_currencies_from_db()
        self.table.update_table(data=data)
        logger.debug("Currency Table updated")

    def get_treeview_frame(self, parent):
        """Create the treeview frame."""
        treeview_frame = ttk.Frame(parent)
        data = self.get_currencies_from_db()

        self.table = CustomTable(parent=treeview_frame, data=data)
        self.table.add_column(column='id', dtype=int, anchor=tk.E, minwidth=50, width=50)
        self.table.add_column(column='code', dtype=str, minwidth=75, width=75, is_sorted_asc=True)
        self.table.add_column(column='description', dtype=str, anchor=tk.W, minwidth=10, width=200)
        self.table.update_table()
        self.table.grid(column=0, row=0, sticky="ew")

        return treeview_frame


    def get_close_frame(self, parent):
        """Create the close frame."""
        close_frame = ttk.Frame(parent, padding=5)
        ttk.Button(close_frame, text='Cerrar', command=self.destroy).grid(column=0, row=0)
        return close_frame

    def btn_new_currency(self):
        """Open the new currency view."""
        CurrencyNewView(parent=self)

    def btn_edit_currency(self, event=None):
        """Open the edit currency view."""

        if data := self.table.get_items_data(selected_only=True):
            currency_id = data[0]['id']
            CurrencyEditView(parent=self, currency_id=currency_id)

    def btn_delete_currency(self, event=None):
        """Delete the selected currency."""

        if messagebox.askyesno("Delete confirmation", "Are you sure you want to delete the selected currencies?"):
            currency_ids = [
                items_data['id']
                for items_data in self.table.get_items_data(selected_only=True)
            ]
            if handle_db_errors(func=lambda: DB.delete_currencies(ids=currency_ids))():
                messagebox.showinfo("Success", "Currencies Deleted successfully!")
                self.event_generate("<<CurrencyDeleted>>")



class CurrencyNewView(CustomTopLvel):
    """A view for creating a new currency."""

    def __init__(self, parent: tk.Toplevel | tk.Tk):
        super().__init__(parent, title="Nueva Moneda")
        
        self.input_frame = self.get_input_frame(parent=self.main_frame)
        self.input_frame.grid(column=0, row=0)

        self.buttons_frame = self.get_buttons_frame(parent=self.main_frame)
        self.buttons_frame.grid(column=0, row=2, sticky="ew")
        self.buttons_frame.grid_anchor("center")

        center_window(window=self, context_window=self.parent)
        self.bind("<Return>", self.btn_accept)


    def get_input_frame(self, parent):
        """Create the input frame."""
        
        self.code_var = tk.StringVar()
        self.desc_var = tk.StringVar()

        input_frame = ttk.Frame(parent, padding=10)

        ttk.Label(input_frame, text='Codigo').grid(column=0, row=0, padx=5, sticky="w")
        ttk.Entry(input_frame, takefocus=True, textvariable=self.code_var, width=5).grid(column=1, row=0, sticky="w")
        ttk.Label(input_frame, text='Descripcion').grid(column=0, row=1, padx=5, pady=5, sticky="w")
        ttk.Entry(input_frame, textvariable=self.desc_var, width=30).grid(column=1, row=1, sticky="w")

        return input_frame


    def get_buttons_frame(self, parent):
        """Create the buttons frame."""
        
        buttons_frame = ttk.Frame(parent)
        
        ttk.Button(buttons_frame, text='Aceptar', command=self.btn_accept).grid(column=0, row=2)
        ttk.Frame(buttons_frame, width=50).grid(column=1, row=2) # spacer
        ttk.Button(buttons_frame, text='Cancelar', command=self.destroy).grid(column=2, row=2)
        
        return buttons_frame


    def btn_accept(self, event=None):
        if handle_db_errors(func=lambda: DB.new_currency(code=self.code_var.get(), description=self.desc_var.get()))():
            messagebox.showinfo("Success", "Currency created successfully!")
            self.parent.event_generate("<<NewCurrencyAdded>>")
            self.parent.focus()
            self.destroy()
        else:
            self.focus()


class CurrencyEditView(CustomTopLvel):
    """A view for editing a currency."""

    def __init__(self, parent: tk.Toplevel | tk.Tk, currency_id: int):
        super().__init__(parent, title="Editar Moneda")
        self.currency_id = currency_id
        
        self.input_frame = self.get_input_frame(parent=self.main_frame)
        self.input_frame.grid(column=0, row=0)

        self.buttons_frame = self.get_buttons_frame(parent=self.main_frame)
        self.buttons_frame.grid(column=0, row=2, sticky="ew")
        self.buttons_frame.grid_anchor("center")

        self.load_data()
        center_window(window=self, context_window=self.parent)
        self.bind("<Return>", self.btn_accept)

    def load_data(self):
        if result := handle_db_errors(
            func=lambda: DB.get_currencies(ids=self.currency_id)
        )():
            self.code_var.set(result[0]['code'])
            self.desc_var.set(result[0]['description'])
            

    def get_input_frame(self, parent):
        """Create the input frame."""
        
        self.code_var = tk.StringVar()
        self.desc_var = tk.StringVar()

        input_frame = ttk.Frame(parent, padding=10)

        # id
        ttk.Label(input_frame, text='Id')\
            .grid(column=0, row=0, padx=5, sticky="w")
        ttk.Label(input_frame, text=str(self.currency_id))\
            .grid(column=1, row=0, sticky="w")
        # code
        ttk.Label(input_frame, text='Codigo')\
            .grid(column=0, row=1, padx=5, sticky="w")
        ttk.Entry(input_frame, takefocus=True, textvariable=self.code_var, width=5)\
            .grid(column=1, row=1, sticky="w")
        # description
        ttk.Label(input_frame, text='Descripcion')\
            .grid(column=0, row=2, padx=5, pady=5, sticky="w")
        ttk.Entry(input_frame, textvariable=self.desc_var, width=30)\
            .grid(column=1, row=2, sticky="w")

        return input_frame


    def get_buttons_frame(self, parent):
        """Create the buttons frame."""
        
        buttons_frame = ttk.Frame(parent)
        
        ttk.Button(buttons_frame, text='Aceptar', command=self.btn_accept).grid(column=0, row=2)
        ttk.Frame(buttons_frame, width=50).grid(column=1, row=2) # spacer
        ttk.Button(buttons_frame, text='Cancelar', command=self.destroy).grid(column=2, row=2)
        
        return buttons_frame


    def btn_accept(self, event=None):
        """Edit the currency."""
        
        result = DB.edit_currency(currency_id=self.currency_id, code=self.code_var.get(), description=self.desc_var.get())
        if result['error']:
            messagebox.showerror("Error", result['error'])
            self.focus()
        else:
            messagebox.showinfo("Success", "Currency Edited successfully!")
            self.parent.event_generate("<<CurrencyEdited>>")
            self.parent.focus()
            self.destroy()


if __name__ == '__main__':
    from utils import test_toplevel_class
    test_toplevel_class(CurrencyListView)

