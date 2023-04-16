from database.sqlite_handler import get_session
from database.models import Currency
from tkinter import messagebox
from sqlalchemy import func
from custom.custom_table import CustomTable
from custom.templates_view import TemplateListView, TemplateChange, FrameInput
from views.config_views import VIEW_WIDGET_WIDTH, TABLE_COLUMN_WIDTH

import tkinter as tk


class CurrencyChangeView(TemplateChange):
    """A view for creating and editing a currency."""

    def __init__(self, parent: tk.Toplevel | tk.Tk, currency_id: int=None):
        
        if currency_id:
            with get_session() as session:
                if not (currency:=session.query(Currency).filter(Currency.id == currency_id).first()):
                    messagebox.showerror("Error", f"Currency {currency_id} not found")
                    self.parent.focus()
                    self.destroy()
            self.currency = currency

            super().__init__(parent, title="Edit Currency") 
            
            self.input_frame.set_values({
                "id": self.currency.id,
                "code": self.currency.code,
                "description": self.currency.description
            })
            
        else:
            super().__init__(parent, title="New Currency") 

        
    def set_inputs(self, input_frame: FrameInput):
        if getattr(self, 'currency', None):
            input_frame.add_input_label(key="id", text='Id', width=VIEW_WIDGET_WIDTH['ID'])
        input_frame.add_input_entry(key="code", width=VIEW_WIDGET_WIDTH['CURRENCY_CODE'])
        input_frame.add_input_entry(key="description", width=VIEW_WIDGET_WIDTH['DESCRIPTION'])
    
    def get_validated_values(self, input_values: dict) -> dict:
        if not input_values["code"]:
            raise ValueError("Code is required")
        return input_values
        
    def on_accept(self, values: list[dict]):
        with get_session() as session:
            if getattr(self, 'currency', None):
                self.currency.code = values['code']
                self.currency.description = values['description']
                currency = self.currency
            else:
                currency = Currency(
                    code=values['code'],
                    description=values['description']
                )
            session.add(currency)
            session.commit()            



class CurrencyListView(TemplateListView):
    __model__ = Currency
    __edit_view__ = CurrencyChangeView
    __new_view__ = CurrencyChangeView
    
    def __init__(self, parent: tk.Toplevel | tk.Tk):
        super().__init__(parent, title='Currencies')
        
    
    def get_data(self):
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

    def add_columns(self, table: CustomTable):
        """Set the columns of the table"""
        table.add_column(column='id', dtype=int, anchor=tk.E, width=TABLE_COLUMN_WIDTH['ID'])
        table.add_column(column='code', dtype=str, width=TABLE_COLUMN_WIDTH['CURRENCY_CODE'], is_sorted_asc=True)
        table.add_column(column='description', dtype=str, anchor=tk.W, width=TABLE_COLUMN_WIDTH['DESCRIPTION'])


if __name__ == '__main__':
    from utils import test_toplevel_class
    test_toplevel_class(CurrencyListView)

