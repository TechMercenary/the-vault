from utils import center_window
from database.sqlite_handler import get_session
from database.models import Currency
from tkinter import messagebox
from sqlalchemy import func
from custom_widgets.table import CustomTable
from custom_widgets.toplevel import CustomTopLvel
import tkinter as tk
import tkinter.ttk as ttk
from config import logger


class CurrencyListView(CustomTopLvel):
    """A view for the currencies."""

    def __init__(self, parent: tk.Toplevel | tk.Tk):
        super().__init__(parent, title="Currencies")
        
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
        ttk.Button(buttons_frame, text='New Currency', command=self.btn_new_currency).grid(column=0, row=0)
        ttk.Button(buttons_frame, text='Edit', command=self.btn_edit_currency).grid(column=1, row=0)
        ttk.Button(buttons_frame, text='Delete', command=self.btn_delete_currency).grid(column=2, row=0)
        return buttons_frame

    def get_currencies_from_db(self):
        """Get the currencies from the database."""

        with get_session() as session:
            currencies = session.query(Currency).order_by(func.lower(Currency.code)).all()
            return [
                {
                    'id': currency.id,
                    'code': currency.code,
                    'description': currency.description,
                }
                for currency in currencies
            ]
    

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

        if selected_items:=self.table.get_items_data(selected_only=True):
            currency_id = selected_items[0]['id']
            CurrencyEditView(parent=self, currency_id=currency_id)

    def btn_delete_currency(self, event=None):
        """Delete the selected currency."""
        
        if (selected_items:=self.table.get_items_data(selected_only=True)) \
            and messagebox.askyesno("Delete confirmation","Are you sure you want to delete the selected currencies?"):
            try:
                currency_ids = [item['id'] for item in selected_items]                
                
                with get_session() as session:
                    session.query(Currency).filter(Currency.id.in_(currency_ids)).delete(synchronize_session=False)
                    session.commit()
                messagebox.showinfo("Success", "Currencies Deleted successfully!")
                self.event_generate("<<CurrencyDeleted>>")
            except Exception as e:
                messagebox.showerror("Error", str(e))


class _ChangeTemplate(CustomTopLvel):

    def __init__(self, parent: tk.Toplevel | tk.Tk, title: str):
        super().__init__(parent, title=title, resizable=False)

        self.input_frame = self.get_input_frame(parent=self.main_frame)
        self.input_frame.grid(column=0, row=0)

        self.buttons_frame = self.get_buttons_frame(parent=self.main_frame)
        self.buttons_frame.grid(column=0, row=2, sticky="ew")
        self.buttons_frame.grid_anchor("center")

        center_window(window=self, context_window=self.parent)
        self.bind("<Return>", self.btn_accept)
    
    
    def btn_accept(self, event=None):
        """Accept the changes."""
        raise NotImplementedError


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


class CurrencyNewView(_ChangeTemplate):
    """A view for creating a new currency."""

    def __init__(self, parent: tk.Toplevel | tk.Tk):
        super().__init__(parent, title="Nueva Moneda")
        

    def btn_accept(self, event=None):
        try:
            assert self.code_var.get(), "Code is required"
            with get_session() as session:
                session.add(Currency(
                    code=self.code_var.get(),
                    description=self.desc_var.get())
                )
                session.commit()

            messagebox.showinfo("Success", "Currency created successfully!")
            self.parent.event_generate("<<NewCurrencyAdded>>")
            self.parent.focus()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.focus()
        


class CurrencyEditView(_ChangeTemplate):
    """A view for editing a currency."""

    def __init__(self, parent: tk.Toplevel | tk.Tk, currency_id: int):
        self.currency_id = currency_id
        super().__init__(parent, title="Edit Currency")

        self.load_data()

    def load_data(self):
        try:
            
            with get_session() as session:
                currency = session.query(Currency).filter(Currency.id == self.currency_id).first()
            
            assert currency, f"Currency {self.currency_id} not found"
            self.currency = currency
            self.code_var.set(self.currency.code)
            self.desc_var.set(self.currency.description)
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.parent.focus()
            self.destroy()
        

    def btn_accept(self, event=None):
        """Edit the currency."""

        try:
            assert self.code_var.get(), "Code is required"
            with get_session() as session:
                self.currency.code = self.code_var.get()
                self.currency.description = self.desc_var.get()
                
                session.add(self.currency)
                session.commit()
                
            messagebox.showinfo("Success", "Currency Edited successfully!")
            self.parent.event_generate("<<CurrencyEdited>>")
            self.parent.focus()
            self.destroy()        
        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == '__main__':
    from utils import test_toplevel_class
    test_toplevel_class(CurrencyListView)

