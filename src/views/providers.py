from utils import center_window
from database.sqlite_handler import get_session
from database.models import Provider
from tkinter import messagebox
from sqlalchemy import func
from custom_widgets.table import CustomTable
from custom_widgets.toplevel import CustomTopLvel
import tkinter as tk
import tkinter.ttk as ttk
from config import logger


class ProviderListView(CustomTopLvel):
    """A view for the provider."""

    def __init__(self, parent: tk.Toplevel | tk.Tk):
        super().__init__(parent, title="Providers")
        
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
        self.bind("<<NewProviderAdded>>", self.update_table)
        self.bind("<<ProviderDeleted>>", self.update_table)
        self.bind("<<ProviderEdited>>", self.update_table)
        
        self.bind('<Delete>', self.btn_delete_provider)
        self.bind('<F2>', self.btn_edit_prodivder)
        self.bind('<Double-1>', self.btn_edit_prodivder)
        self.bind('<Return>', self.btn_edit_prodivder)

    def get_buttons_frame(self, parent):
        """Create the buttons frame."""

        buttons_frame = ttk.Frame(parent, padding=10)
        ttk.Button(buttons_frame, text='New Provider', command=self.btn_new_provider).grid(column=0, row=0)
        ttk.Button(buttons_frame, text='Edit', command=self.btn_edit_prodivder).grid(column=1, row=0)
        ttk.Button(buttons_frame, text='Delete', command=self.btn_delete_provider).grid(column=2, row=0)
        return buttons_frame

    def get_providers_from_db(self):
        """Get the providers from the database."""

        with get_session() as session:
            providers = session.query(Provider).order_by(func.lower(Provider.name)).all()
            return [
                {
                    'id': provider.id,
                    'name': provider.name,
                    'description': provider.description,
                }
                for provider in providers
            ]
    

    def update_table(self, event):
        """Update the table with the latest data from the database."""
        data=self.get_providers_from_db()
        self.table.update_table(data=data)
        logger.debug("Provider Table updated")

    def get_treeview_frame(self, parent):
        """Create the treeview frame."""
        treeview_frame = ttk.Frame(parent)
        data = self.get_providers_from_db()

        self.table = CustomTable(parent=treeview_frame, data=data)
        self.table.add_column(column='id', dtype=int, anchor=tk.E, minwidth=50, width=50)
        self.table.add_column(column='name', dtype=str, minwidth=75, width=200, is_sorted_asc=True)
        self.table.add_column(column='description', dtype=str, anchor=tk.W, minwidth=10, width=200)
        self.table.update_table()
        self.table.grid(column=0, row=0, sticky="ew")

        return treeview_frame


    def get_close_frame(self, parent):
        """Create the close frame."""
        close_frame = ttk.Frame(parent, padding=5)
        ttk.Button(close_frame, text='Cerrar', command=self.destroy).grid(column=0, row=0)
        return close_frame

    def btn_new_provider(self):
        """Open the new provider view."""
        ProviderNewView(parent=self)

    def btn_edit_prodivder(self, event=None):
        """Open the edit provider view."""

        if selected_items:=self.table.get_items_data(selected_only=True):
            provider_id = selected_items[0]['id']
            ProviderEditView(parent=self, provider_id=provider_id)

    def btn_delete_provider(self, event=None):
        """Delete the selected provider."""
        
        if (selected_items:=self.table.get_items_data(selected_only=True)) \
            and messagebox.askyesno("Delete confirmation","Are you sure you want to delete the selected providers?"):
            try:
                provider_ids = [item['id'] for item in selected_items]                
                
                with get_session() as session:
                    session.query(Provider).filter(Provider.id.in_(provider_ids)).delete(synchronize_session=False)
                    session.commit()
                messagebox.showinfo("Success", "Providers Deleted successfully!")
                self.event_generate("<<ProviderDeleted>>")
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
        
        self.name_var = tk.StringVar()
        self.desc_var = tk.StringVar()

        input_frame = ttk.Frame(parent, padding=10)

        ttk.Label(input_frame, text='Name').grid(column=0, row=0, padx=5, sticky="w")
        ttk.Entry(input_frame, takefocus=True, textvariable=self.name_var, width=30).grid(column=1, row=0, sticky="w")
        ttk.Label(input_frame, text='Descripcion').grid(column=0, row=1, padx=5, pady=5, sticky="w")
        ttk.Entry(input_frame, textvariable=self.desc_var, width=30).grid(column=1, row=1, sticky="w")

        return input_frame


    def get_buttons_frame(self, parent):
        """Create the buttons frame."""
        
        buttons_frame = ttk.Frame(parent)
        
        ttk.Button(buttons_frame, text='Accept', command=self.btn_accept).grid(column=0, row=2)
        ttk.Frame(buttons_frame, width=50).grid(column=1, row=2) # spacer
        ttk.Button(buttons_frame, text='Cancel', command=self.destroy).grid(column=2, row=2)
        
        return buttons_frame


class ProviderNewView(_ChangeTemplate):
    """A view for creating a new provider."""

    def __init__(self, parent: tk.Toplevel | tk.Tk):
        super().__init__(parent, title="New Provider")
        

    def btn_accept(self, event=None):
        try:
            assert self.name_var.get(), "Name is required"
            with get_session() as session:
                session.add(Provider(
                    name=self.name_var.get(),
                    description=self.desc_var.get())
                )
                session.commit()

            messagebox.showinfo("Success", "Provider created successfully!")
            self.parent.event_generate("<<NewProviderAdded>>")
            self.parent.focus()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.focus()
        

class ProviderEditView(_ChangeTemplate):
    """A view for editing a provider."""

    def __init__(self, parent: tk.Toplevel | tk.Tk, provider_id: int):
        self.provider_id = provider_id
        super().__init__(parent, title="Edit Provider")

        self.load_data()

    def load_data(self):
        try:
            
            with get_session() as session:
                provider = session.query(Provider).filter(Provider.id == self.provider_id).first()
            
            assert provider, f"Provider {self.provider_id} not found"
            self.provider = provider
            self.name_var.set(self.provider.name)
            self.desc_var.set(self.provider.description)
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.parent.focus()
            self.destroy()
        

    def btn_accept(self, event=None):
        """Edit the provider."""

        try:
            assert self.name_var.get(), "Name is required"
            with get_session() as session:
                self.provider.name = self.name_var.get()
                self.provider.description = self.desc_var.get()
                
                session.add(self.provider)
                session.commit()
                
            messagebox.showinfo("Success", "Provider Edited successfully!")
            self.parent.event_generate("<<ProviderEdited>>")
            self.parent.focus()
            self.destroy()        
        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == '__main__':
    from utils import test_toplevel_class
    test_toplevel_class(ProviderListView)

