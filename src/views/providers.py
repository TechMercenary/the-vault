from database.sqlite_handler import get_session
from database.models import Provider
from tkinter import messagebox
from sqlalchemy import func
from custom.custom_table import CustomTable
from custom.templates_view import TemplateListView, TemplateNewEdit, FrameInput
from views.config_views import VIEW_WIDGET_WIDTH, TABLE_COLUMN_WIDTH
import tkinter as tk


class ProviderChangeView(TemplateNewEdit):
    """A view for creating and editing a provider."""

    def __init__(self, parent: tk.Toplevel | tk.Tk, provider_id: int = None):
        
        if provider_id:
            with get_session() as session:
                if not (provider:=session.query(Provider).filter(Provider.id == provider_id).first()):
                    messagebox.showerror("Error", f"Provider {provider_id} not found")
                    self.parent.focus()
                    self.destroy()   
            self.provider = provider
        
            super().__init__(parent, title="Edit Provider")

            self.input_frame.set_values({
                "id": self.provider.id,
                "name": self.provider.name,
                "description": self.provider.description
            })
        else:
            super().__init__(parent, title="New Provider")

    def set_inputs(self, input_frame: FrameInput):
        if getattr(self, 'provider', None):
            input_frame.add_input_label(key="id", text='Id', width=VIEW_WIDGET_WIDTH['ID'])
        input_frame.add_input_entry(key="name", width=VIEW_WIDGET_WIDTH['PROVIDER_NAME'])
        input_frame.add_input_entry(key="description", width=VIEW_WIDGET_WIDTH['DESCRIPTION'])
    
    def get_validated_values(self, input_values: dict) -> dict:
        if not input_values["name"]:
            raise ValueError("Name is required")
        return input_values
        
    def on_accept(self, values: list[dict]):
        with get_session() as session:
            if getattr(self, 'provider', None):
                self.provider.name = values['name']
                self.provider.description = values['description']
                provider = self.provider
            else:
                provider = Provider(
                    name=values['name'],
                    description=values['description']
                )
            session.add(provider)
            session.commit()


class ProviderListView(TemplateListView):
    """A view for the provider."""

    __model__ = Provider
    __edit_view__ = ProviderChangeView
    __new_view__ = ProviderChangeView

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
        table.add_column(column='id', dtype=int, anchor=tk.E, width=TABLE_COLUMN_WIDTH['ID'])
        table.add_column(column='name', dtype=str, anchor=tk.W, width=TABLE_COLUMN_WIDTH['PROVIDER_NAME'], is_sorted_asc=True)
        table.add_column(column='description', dtype=str, anchor=tk.W, width=TABLE_COLUMN_WIDTH['DESCRIPTION'])


if __name__ == '__main__':
    from utils import test_toplevel_class
    test_toplevel_class(ProviderListView)

