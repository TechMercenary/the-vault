from database.sqlite_handler import get_session
from database.models import Currency
from tkinter import messagebox
from sqlalchemy import func
from custom.custom_table import CustomTable
from custom.templates_view import TemplateListView, TemplateNewEdit, FrameInput

import tkinter as tk


class CurrencyNewView(TemplateNewEdit):
    """A view for creating a new currency."""

    def __init__(self, parent: tk.Toplevel | tk.Tk):
        super().__init__(parent, title="New Currency")
        
    def set_inputs(self, input_frame: FrameInput):
        input_frame.add_input_entry(key="code", width=5)
        input_frame.add_input_entry(key="description", width=30)

    def get_validated_values(self, input_values: dict) -> dict:
        if not input_values["code"]:
            raise ValueError("Code is required")
        return input_values
    
    def on_accept(self, values: list[dict]):
        with get_session() as session:
            session.add(Currency(
                code=values['code'],
                description=values['description']
            ))
            session.commit()


class CurrencyEditView(TemplateNewEdit):
    """A view for editing a currency."""

    def __init__(self, parent: tk.Toplevel | tk.Tk, currency_id: int):
        
        with get_session() as session:
            if not (currency:=session.query(Currency).filter(Currency.id == currency_id).first()):
                messagebox.showerror("Error", f"Currency {currency_id} not found")
                self.parent.focus()
                self.destroy()

        super().__init__(parent, title="Edit Currency") 

        self.currency = currency
        self.input_frame.set_values({
            "code": self.currency.code,
            "description": self.currency.description
        })
        
    def set_inputs(self, input_frame: FrameInput):
        input_frame.add_input_entry(key="code", width=5)
        input_frame.add_input_entry(key="description", width=30)
    
    def get_validated_values(self, input_values: dict) -> dict:
        if not input_values["code"]:
            raise ValueError("Code is required")
        return input_values
        
    def on_accept(self, values: list[dict]):
        with get_session() as session:
            self.currency.code = values['code']
            self.currency.description = values['description']
            session.add(self.currency)
            session.commit()


class CurrencyListView(TemplateListView):
    __model__ = Currency
    __edit_view__ = CurrencyEditView
    __new_view__ = CurrencyNewView
    
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
        table.add_column(column='id', dtype=int, anchor=tk.E, minwidth=50, width=50)
        table.add_column(column='code', dtype=str, minwidth=75, width=75, is_sorted_asc=True)
        table.add_column(column='description', dtype=str, anchor=tk.W, minwidth=10, width=200)


if __name__ == '__main__':
    from utils import test_toplevel_class
    test_toplevel_class(CurrencyListView)

