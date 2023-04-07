from database.sqlite_handler import get_session
from database.models import Provider
from tkinter import messagebox
from sqlalchemy import func
from custom.custom_table import CustomTable
from custom.templates_view import TemplateListView, TemplateNewEdit, FrameInput

import tkinter as tk


class ProviderNewView(TemplateNewEdit):
    """A view for creating a new provider."""

    def __init__(self, parent: tk.Toplevel | tk.Tk):
        super().__init__(parent, title="New Provider")

    def set_inputs(self, input_frame: FrameInput):
        input_frame.add_input_entry(key="name", width=30)
        input_frame.add_input_entry(key="description", width=30)

    def get_validated_values(self, input_values: dict) -> dict:
        if not input_values["name"]:
            raise ValueError("Name is required")
        return input_values

    def on_accept(self, values: list[dict]):
        with get_session() as session:
            session.add(Provider(
                name=values['name'],
                description=values['description']
            ))
            session.commit()
        

class ProviderEditView(TemplateNewEdit):
    """A view for editing a provider."""

    def __init__(self, parent: tk.Toplevel | tk.Tk, provider_id: int):
        
        with get_session() as session:
            if not (provider:=session.query(Provider).filter(Provider.id == provider_id).first()):
                messagebox.showerror("Error", f"Provider {provider_id} not found")
                self.parent.focus()
                self.destroy()   
        
        super().__init__(parent, title="Edit Provider")

        self.provider = provider
        self.input_frame.set_values({
            "name": self.provider.name,
            "description": self.provider.description
        })

    def set_inputs(self, input_frame: FrameInput):
        input_frame.add_input_entry(key="name", width=5)
        input_frame.add_input_entry(key="description", width=30)
    
    def get_validated_values(self, input_values: dict) -> dict:
        if not input_values["name"]:
            raise ValueError("Name is required")
        return input_values
        
    def on_accept(self, values: list[dict]):
        with get_session() as session:
            self.provider.name = values['name']
            self.provider.description = values['description']
            session.add(self.provider)
            session.commit()


class ProviderListView(TemplateListView):
    """A view for the provider."""

    __model__ = Provider
    __edit_view__ = ProviderEditView
    __new_view__ = ProviderNewView

    def __init__(self, parent: tk.Toplevel | tk.Tk):
        super().__init__(parent, title="Providers")
  
  
    def get_data(self):
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
    
    def add_columns(self, table: CustomTable):
        table.add_column(column='id', dtype=int, anchor=tk.E, minwidth=50, width=50)
        table.add_column(column='name', dtype=str, anchor=tk.W, minwidth=75, width=200, is_sorted_asc=True)
        table.add_column(column='description', dtype=str, anchor=tk.W, minwidth=10, width=200)


if __name__ == '__main__':
    from utils import test_toplevel_class
    test_toplevel_class(ProviderListView)

