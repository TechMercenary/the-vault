from abc import abstractmethod
from utils import center_window, get_datetime_from_db
from database.sqlite_handler import get_session
from database.models import Account, Transaction
from tkinter import messagebox
from custom.custom_table import CustomTable
from custom.templates_view import TemplateListView, CustomTopLevel
from custom.custom_widgets import PendulumEntry
from custom.custom_variables import PendulumVar
from views.config_views import VIEW_WIDGET_WIDTH, TABLE_COLUMN_WIDTH
from decimal import Decimal
import tkinter as tk
import tkinter.ttk as ttk


class TransactionChangeTemplate(CustomTopLevel):
    def __init__(self, parent: tk.Toplevel | tk.Tk, title: str):
        
        super().__init__(
            parent=parent,
            title=title,
            footer_buttons_config={
                "Accept": self.on_accept,
                "Cancel": self.destroy
            })
        
        self.create_variables_input()
        self.create_variables_ui()
        self.load_account_aliases()
        self.set_body()


    def load_account_aliases(self) -> None:
        with get_session() as session:
            accounts = session.query(Account).all()
            self.cbox_account_map = {account.alias: account.id for account in accounts}
    
    def get_account_aliases(self) -> list[str]:
            return sorted(self.cbox_account_map.keys())

    def create_variables_input(self) -> None:
        self.variables_input = {
            "timestamp": PendulumVar(),
            "description": tk.StringVar(),
            "installment_number": tk.IntVar(value=1),
            "installment_total": tk.IntVar(value=1),
            "debit_reference": tk.StringVar(),
            "debit_account_alias": tk.StringVar(),
            "debit_amount": tk.DoubleVar(value=0.0),
            "credit_reference": tk.StringVar(),
            "credit_account_alias": tk.StringVar(),
            "credit_amount": tk.DoubleVar(value=0.0),
            "is_reconciled": tk.BooleanVar(value=False),
        }
        
    def create_variables_ui(self) -> None:
        self.variables_ui = {
            "debit_change_icon": tk.StringVar(value="▼"),
            "debit_currency_code": tk.StringVar(value="ARS"),
            "credit_change_icon": tk.StringVar(value="▲"),
            "credit_currency_code": tk.StringVar(value="ARS"),
        }


    def _get_heading_frame(self, parent: ttk.Frame) -> ttk.LabelFrame:
        def get_installments(parent: ttk.Frame) -> ttk.Frame:
            main_frame = ttk.Frame(parent)
            ttk.Spinbox(main_frame, from_=1, to=99, width=5, textvariable=self.variables_input['installment_number']) \
                .grid(row=0, column=0, sticky="w", padx=(10,0))
            ttk.Label(main_frame, text=" of ") \
                .grid(row=0, column=1, sticky="w")
            ttk.Spinbox(main_frame, from_=1, to=99, width=5, textvariable=self.variables_input['installment_total']) \
                .grid(row=0, column=2, sticky="w")
            return main_frame
        
        heading_frame = ttk.LabelFrame(parent, text="Heading")
        
        # ID
        if getattr(self, 'transaction_id', None):
            ttk.Label(heading_frame, text="Id").grid(row=0, column=0, sticky="w", padx=(15,10), pady=(10,5))
            ttk.Label(heading_frame, text=self.transaction_id).grid(row=0, column=1, sticky="w", pady=(10,5))
            
        
        # Timestamp
        ttk.Label(heading_frame, text="Timestamp").grid(row=1, column=0, sticky="w", padx=(15,10), pady=(10,5))
        PendulumEntry(heading_frame, textvariable=self.variables_input["timestamp"], default_now=True, width=VIEW_WIDGET_WIDTH['TIMESTAMP']) \
            .grid(row=1, column=1, sticky="w", pady=(10,5))
        
        # Description
        ttk.Label(heading_frame, text="Description").grid(row=2, column=0, sticky="w", padx=(15,10), pady=(10,5))
        ttk.Entry(heading_frame, textvariable=self.variables_input["description"]).grid(row=2, column=1, sticky="we", padx=(0,15), pady=(10,5))
        
        # Installments
        ttk.Label(heading_frame, text="Installments").grid(row=3, column=0, sticky="w", padx=(15,10), pady=(5,10))
        get_installments(parent=heading_frame).grid(row=3, column=1, sticky="w", pady=(5,10))

        # Reconciled
        if getattr(self, 'transaction_id', None):
            ttk.Checkbutton(heading_frame, text="Reconciled", variable=self.variables_input['is_reconciled']) \
                .grid(row=4, column=0, sticky="w", padx=(15,10), pady=(5,10))


        heading_frame.columnconfigure(1, weight=1)
        return heading_frame


    def _get_double_entry(self, parent: ttk.LabelFrame) -> ttk.Frame:
        def _update_amounts(event, variable_key: str) -> None:

            try:
                amount = self.variables_input[variable_key].get()
            except Exception as e:
                messagebox.showerror(title="Error", message=f"Could not get {variable_key} amount: {e}")
                return None

            if variable_key == 'debit_amount':
                self.variables_input['credit_amount'].set(amount)
            else:
                self.variables_input['debit_amount'].set(amount)


        def get_amount_frame(parent: ttk.Frame, variable_key: str) -> ttk.Frame:
            amount_frame = tk.Frame(parent)

            if 'debit' in variable_key:
                variable_icon = self.variables_ui['debit_change_icon']
                variable_code = self.variables_ui['debit_currency_code']
            else:
                variable_icon = self.variables_ui['credit_change_icon']
                variable_code = self.variables_ui['credit_currency_code']

            ttk.Label(amount_frame, textvariable=variable_icon).grid(row=0, column=0, sticky="w", padx=(0,5))
            ttk.Label(amount_frame, textvariable=variable_code).grid(row=0, column=1, sticky="w", padx=(0,10))

            amount_entry = ttk.Entry(amount_frame, textvariable=self.variables_input[variable_key], justify="right")
            amount_entry.grid(row=0, column=2, sticky="news")
            from functools import partial
            amount_entry.bind("<KeyRelease>", partial(_update_amounts, variable_key=variable_key))

            amount_frame.columnconfigure(2, weight=1)

            return amount_frame

        def get_account_cbox(variable_key: str) -> ttk.Combobox:
            def _update_labels(event, variable_key: str) -> None:
                with get_session() as session:
                    account_alias = self.variables_input[variable_key].get()
                    account_id = self.cbox_account_map[account_alias]
                    account = session.query(Account).filter_by(id=account_id).first()

                    code = account.currency.code
                    change_icon = "▲" if account.account_type.normal_side.lower() in variable_key.lower() else "▼"
                    
                if 'debit' in variable_key:
                    variable_icon = self.variables_ui['debit_change_icon']
                    variable_code = self.variables_ui['debit_currency_code']
                else:
                    variable_icon = self.variables_ui['credit_change_icon']
                    variable_code = self.variables_ui['credit_currency_code']

                variable_code.set(code)
                variable_icon.set(change_icon)

            cbox = ttk.Combobox(
                double_entry_frame,
                textvariable=self.variables_input[variable_key],
                width=VIEW_WIDGET_WIDTH['ACCOUNT_ALIAS'],
                values=self.get_account_aliases(),
                state="readonly"
            )
            cbox.bind("<<ComboboxSelected>>", lambda event: _update_labels(event, variable_key))

            return cbox

        double_entry_frame = ttk.LabelFrame(parent, text="Double-Entry")

        # Row 0: Titles
        ttk.Label(double_entry_frame, text="DEBIT", anchor=tk.CENTER).grid(row=0, column=1, sticky="we", padx=(0,15), pady=(10,5))
        ttk.Label(double_entry_frame, text="CREDIT", anchor=tk.CENTER).grid(row=0, column=2, sticky="we", padx=(0,15), pady=(10,5))
        
        # Row 1: References
        ttk.Label(double_entry_frame, text="Reference").grid(row=1, column=0, sticky="w", padx=(15,10), pady=(0,5))
        ttk.Entry(double_entry_frame, textvariable=self.variables_input["debit_reference"], width=VIEW_WIDGET_WIDTH['DESCRIPTION']).grid(row=1, column=1, sticky="we", padx=(0,15), pady=(0,5))
        ttk.Entry(double_entry_frame, textvariable=self.variables_input["credit_reference"], width=VIEW_WIDGET_WIDTH['DESCRIPTION']).grid(row=1, column=2, sticky="we", padx=(0,15), pady=(0,5))
        
        # Row 2: Accounts
        ttk.Label(double_entry_frame, text="Account").grid(row=2, column=0, sticky="w", padx=(15,10), pady=(0,5))
        get_account_cbox(variable_key="debit_account_alias").grid(row=2, column=1, sticky="we", padx=(0,15), pady=(0,5))
        get_account_cbox(variable_key="credit_account_alias").grid(row=2, column=2, sticky="we", padx=(0,15), pady=(0,5))
        
        # Row 3: Amounts
        ttk.Label(double_entry_frame, text="Amount").grid(row=3, column=0, sticky="we", padx=(15,10), pady=(0,10))
        get_amount_frame(parent=double_entry_frame, variable_key="debit_amount").grid(row=3, column=1, sticky="we", padx=(0,15), pady=(0,10))
        get_amount_frame(parent=double_entry_frame, variable_key="credit_amount").grid(row=3, column=2, sticky="we", padx=(0,15), pady=(0,10))


        double_entry_frame.columnconfigure(1, weight=1)
        return double_entry_frame
        

    def set_body(self) -> None:
        self._get_heading_frame(parent=self.body_frame).grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self._get_double_entry(parent=self.body_frame).grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        

    def _get_validated_input_values(self) -> dict:
        # Installments
        try:
            installment_number = self.variables_input['installment_number'].get()
        except Exception as e:
            messagebox.showerror(title="Error", message=f"Could not get Installment Number: {e}")
            return None

        try:
            installment_total = self.variables_input['installment_total'].get()
        except Exception as e:
            messagebox.showerror(title="Error", message=f"Could not get Installment Total: {e}")
            return None

        try:
            assert installment_number <= installment_total, "Installment number must be less or equal than installment total"
        except Exception as e:
            messagebox.showerror(title="Error", message=e)
            return None

        # Timestamp

        try:
            timestamp = self.variables_input['timestamp'].get()
        except Exception as e:
            messagebox.showerror(title="Error", message=f"Could not parse the timestamp: {e}")
            return None
        
        # Accounts
        
        try:
            debit_account_alias = self.variables_input['debit_account_alias'].get()
            credit_account_alias = self.variables_input['credit_account_alias'].get()
            assert debit_account_alias != credit_account_alias, "Debit and credit accounts must be different"
        except Exception as e:
            messagebox.showerror(title="Error", message=e)
            return None
        
        try:
            assert debit_account_alias in self.cbox_account_map, f"Debit account alias '{debit_account_alias}' not found in account map"
            debit_account_id = self.cbox_account_map[debit_account_alias]
        except Exception as e:
            messagebox.showerror(title="Error", message=e)
            return None

        try:
            assert credit_account_alias in self.cbox_account_map, f"Credit account alias '{credit_account_alias}' not found in account map"
            credit_account_id = self.cbox_account_map[credit_account_alias]
        except Exception as e:
            messagebox.showerror(title="Error", message=e)
            return None

        # Amounts
        
        try:
            debit_amount = self.variables_input['debit_amount'].get()
        except Exception as e:
            messagebox.showerror(title="Error", message=f"Could not get debit amount: {e}")
            return None
        
        try:
            credit_amount = self.variables_input['credit_amount'].get()
        except Exception as e:
            messagebox.showerror(title="Error", message=f"Could not get credit amount: {e}")
            return None

        try:
            assert debit_amount == credit_amount, "Debit and credit amounts must be equal"
            assert debit_amount > 0 and credit_amount > 0, "Debit and credit amounts must be greater than zero"
        except Exception as e:
            messagebox.showerror(title="Error", message=e)
            return None
        
        return {
                "timestamp": timestamp,
                "installment_number": installment_number,
                "installment_total": installment_total,
                "description": self.variables_input["description"].get(),
                "debit_reference": self.variables_input["debit_reference"].get(),
                "debit_account_id": debit_account_id,
                "debit_amount": debit_amount,
                "credit_reference": self.variables_input["credit_reference"].get(),
                "credit_account_id": credit_account_id,
                "credit_amount": credit_amount,
                "is_reconciled": self.variables_input["is_reconciled"].get(),
            }


    @abstractmethod
    def on_accept(self, event=None) -> None:
        raise NotImplementedError()


class TransactionNewView(TransactionChangeTemplate):
    def __init__(self, parent: tk.Toplevel | tk.Tk):
        super().__init__(parent, title='New Transaction')
        center_window(window=self, context_window=parent)

    def on_accept(self, event=None) -> None:
        if input_values:=self._get_validated_input_values():
            try:
                input_values.update({
                    "timestamp": input_values['timestamp'].in_timezone('UTC').to_datetime_string(),
                })
            
                with get_session() as session:
                    session.add(Transaction(**input_values))
                    session.commit()

            except Exception as e:
                messagebox.showerror(title="Error", message=f"Could not create transaction: {e}")
        
            self.destroy()


class TransactionEditView(TransactionChangeTemplate):
    def __init__(self, parent: tk.Toplevel | tk.Tk, transaction_id: int):
        self.transaction_id = transaction_id
        super().__init__(parent, title='Edit Transaction')
        self.load_data(transaction_id)
        center_window(window=self, context_window=parent)
        
        
    def load_data(self, transaction_id: int) -> None:
        
        with get_session() as session:
            self.transaction = session.query(Transaction).filter(Transaction.id == transaction_id).first()

            self.variables_input['timestamp'].set(get_datetime_from_db(self.transaction.timestamp))
            self.variables_input['description'].set(self.transaction.description)
            self.variables_input['installment_number'].set(self.transaction.installment_number)
            self.variables_input['installment_total'].set(self.transaction.installment_total)
            self.variables_input['debit_reference'].set(self.transaction.debit_reference)
            self.variables_input['debit_account_alias'].set(self.transaction.debit_account.alias)
            self.variables_input['debit_amount'].set(self.transaction.debit_amount.quantize(Decimal('0.01')))
            self.variables_input['credit_reference'].set(self.transaction.credit_reference)
            self.variables_input['credit_account_alias'].set(self.transaction.credit_account.alias)
            self.variables_input['credit_amount'].set(self.transaction.credit_amount.quantize(Decimal('0.01')))
            self.variables_input['is_reconciled'].set(self.transaction.is_reconciled)

            self.variables_ui['debit_change_icon'].set("▲" if self.transaction.debit_account.account_type.normal_side == 'DEBIT' else "▼")
            self.variables_ui['debit_currency_code'].set(self.transaction.debit_account.currency.code)
            
            self.variables_ui['credit_change_icon'].set("▲" if self.transaction.credit_account.account_type.normal_side == 'CREDIT' else "▼")
            self.variables_ui['credit_currency_code'].set(self.transaction.credit_account.currency.code)


    def on_accept(self, event=None) -> None:
        if input_values:=self._get_validated_input_values():
            try:
                input_values.update({
                    "timestamp": input_values['timestamp'].in_timezone('UTC').to_datetime_string(),
                })
            
                with get_session() as session:
                    for key in input_values:
                        setattr(self.transaction, key, input_values[key])
                    session.add(self.transaction)
                    session.commit()

            except Exception as e:
                messagebox.showerror(title="Error", message=f"Could not edit transaction: {e}")
        
            self.destroy()    



class TransactionListView(TemplateListView):
    __model__ = Transaction
    __edit_view__ = TransactionEditView
    __new_view__ = TransactionNewView
    
    def __init__(self, parent: tk.Toplevel | tk.Tk):
        super().__init__(parent, title="Transactions")
        
    def get_data(self):
        
        with get_session() as session:
            transactions = session.query(Transaction).order_by(Transaction.timestamp.desc()).all()
            return [
                {
                    'id': transaction.id,
                    'timestamp': get_datetime_from_db(transaction.timestamp),
                    'description': transaction.description,
                    'cuotas': f"{transaction.installment_number:02d}/{transaction.installment_total:02d}",
                    'debit_account': transaction.debit_account.alias,
                    'debit_currency': transaction.debit_account.currency.code,
                    'debit_amount': transaction.debit_amount.quantize(Decimal('0.01')),
                    'credit_account': transaction.credit_account.alias,
                    'credit_currency': transaction.credit_account.currency.code,
                    'credit_amount': transaction.credit_amount.quantize(Decimal('0.01')),
                }
                for transaction in transactions
            ]
        
    def add_columns(self, table: CustomTable):
        def add_account_columns(side: str):
            table.add_column(column=f"{side}_account", dtype=str, anchor=tk.W, width=TABLE_COLUMN_WIDTH['ACCOUNT_ALIAS'])
            table.add_column(column=f"{side}_currency", text='Code', dtype=str, anchor=tk.CENTER, width=TABLE_COLUMN_WIDTH['CURRENCY_CODE'])
            table.add_column( column=f"{side}_amount", text='Amount', dtype=str, anchor=tk.CENTER, width=TABLE_COLUMN_WIDTH['MONEY'])

        """Set the columns of the table"""
        table.add_column(column='id', dtype=int, anchor=tk.E, width=TABLE_COLUMN_WIDTH['ID'])
        table.add_column(column='timestamp', dtype=str, anchor=tk.W, width=TABLE_COLUMN_WIDTH['TIMESTAMP'])
        table.add_column(column='description', dtype=str, anchor=tk.W, width=TABLE_COLUMN_WIDTH['DESCRIPTION'])
        table.add_column(column='cuotas', dtype=str, anchor=tk.CENTER, width=50)
        add_account_columns(side='debit')
        add_account_columns(side='credit')


if __name__ == '__main__':
    from utils import toplevel_set_active
    
    root = tk.Tk()
    
    # toplevel = TransactionEditView(root, 1)
    # toplevel = TransactionNewView(root)
    toplevel = TransactionListView(root)
    
    center_window(window=root, context_window=None)
    toplevel_set_active(window=toplevel)
    center_window(window=toplevel, context_window=root)
    root.mainloop()

