from abc import abstractmethod
from database.sqlite_handler import get_session
from database.models import AccountOverdraft
from tkinter import messagebox
from custom.custom_table import CustomTable
from custom.templates_view import TemplateListView, TemplateChange, FrameInput
from database.common_queries import get_accounts_values
from utils import get_datetime_from_db, get_datetime_to_db
from views.config_views import VIEW_WIDGET_WIDTH, TABLE_COLUMN_WIDTH
import tkinter as tk


class AccountOverdraftChangeView(TemplateChange):
    def __init__(self, parent: tk.Toplevel | tk.Tk, title: str, account_overdraft_id: int = None) -> None:
        super().__init__(parent, title=title)
        self.account_overdraft_id = account_overdraft_id

    def set_inputs(self, input_frame: FrameInput):
        if self.account_overdraft_id:
            input_frame.add_input_label(key="id", text="Id", width=VIEW_WIDGET_WIDTH['ID'])
        input_frame.add_input_combobox(key="account", func_get_values=get_accounts_values, width=VIEW_WIDGET_WIDTH['ACCOUNT_ALIAS'])
        input_frame.add_input_decimal(key="limit", text="Limit ($)", width=VIEW_WIDGET_WIDTH['OVERDRAFT_LIMIT'])
        input_frame.add_input_pendulum(key="started_at", default_now=True)
        if self.account_overdraft_id:
            input_frame.add_input_pendulum(key="ended_at")
        
    def get_validated_values(self, input_values: dict) -> dict:
        if not input_values["limit"] or float(input_values["limit"]) <= 0:
            raise ValueError("Limit must be greater than 0")

        if not input_values["started_at"]:
            raise ValueError("Started At must be set")

        if input_values["ended_at"] and input_values["ended_at"] < input_values["started_at"]:
            raise ValueError("Ended At must be greater than Started At")

        return {
            "account_id": input_values["account"]["key"],
            "limit": input_values["limit"],
            "started_at": get_datetime_to_db(str(input_values['started_at'])),
            "ended_at": get_datetime_to_db(str(input_values['ended_at'])) if input_values['ended_at'] else None,
        }

    @abstractmethod
    def on_accept(self, event=None) -> None:
        raise NotImplementedError


class AccountOverdraftNewView(AccountOverdraftChangeView):
    """A view for creating a new account overdraft."""

    def __init__(self, parent: tk.Toplevel | tk.Tk) -> None:
        super().__init__(parent, title="New Account Overdraft")

    def on_accept(self, values: list[dict]):
        with get_session() as session:
            session.add(AccountOverdraft(
                    account_id=values['account_id'],
                    limit=values['limit'],
                    started_at=values['started_at'],
                ))
            session.commit()


class AccountOverdraftEditView(AccountOverdraftChangeView):
    """A view for creating and editing an account overdraft."""

    def __init__(self, parent: tk.Toplevel | tk.Tk, account_overdraft_id: int=None):
        super().__init__(parent, title="Edit Account Overdraft")
        
        with get_session() as session:
            if not (account_overdraft:=session.query(AccountOverdraft).filter(AccountOverdraft.id == account_overdraft_id).first()):
                messagebox.showerror("Error", f"Account Overdraft {account_overdraft_id} not found")
                self.parent.focus()
                self.destroy()
            self.account_overdraft = account_overdraft

            self.input_frame.set_values({
                "id": self.account_overdraft.id,
                "account": self.account_overdraft.account.alias,
                "limit": f"{self.account_overdraft.limit:.2f}",
                "started_at": get_datetime_from_db(str(self.account_overdraft.started_at)),
                "ended_at": get_datetime_from_db(str(self.account_overdraft.ended_at)) if self.account_overdraft.ended_at else '',
            })


    def on_accept(self, values: list[dict]):
        with get_session() as session:
            if getattr(self, 'account_overdraft', None):
                self.account_overdraft.limit = values['limit']
                self.account_overdraft.started_at = values['started_at']
                self.account_overdraft.ended_at = values['ended_at']
                account_overdraft = self.account_overdraft
            else:
                account_overdraft = AccountOverdraft(
                    account_id=values['account_id'],
                    limit=values['limit'],
                    started_at=values['started_at'],
                    ended_at=values['ended_at']
                )
            session.add(account_overdraft)
            session.commit()


class AccountOverdraftListView(TemplateListView):
    __model__ = AccountOverdraft
    __edit_view__ = AccountOverdraftEditView
    __new_view__ = AccountOverdraftNewView
    
    def __init__(self, parent: tk.Toplevel | tk.Tk):
        super().__init__(parent, title='Account Overdrafts')


    def get_data(self):
        """Get the account overdraft from the database."""

        with get_session() as session:
            account_overdrafts = session.query(AccountOverdraft).all()
            data = [{
                    "id": account_overdraft.id,
                    "account": account_overdraft.account.alias,
                    "limit": f"$ {account_overdraft.limit:.2f}",
                    "started_at": get_datetime_from_db(str(account_overdraft.started_at)),
                    "ended_at": get_datetime_from_db(str(account_overdraft.ended_at)) if account_overdraft.ended_at else '',
                } for account_overdraft in account_overdrafts]

            def _func_sort(x):
                return (x['account'].lower(), x['started_at'])

            return sorted(data, key=_func_sort)


    def add_columns(self, table: CustomTable):
        """Set the columns of the table"""
        table.add_column(column='id', dtype=int, anchor=tk.E, width=TABLE_COLUMN_WIDTH['ID'])
        table.add_column(column='account', dtype=str, anchor=tk.W, width=TABLE_COLUMN_WIDTH['ACCOUNT_NAME'], is_sorted_asc=True)
        table.add_column(column='limit', dtype=str, anchor=tk.E, width=TABLE_COLUMN_WIDTH['MONEY'])
        table.add_column(column='started_at', dtype=str, anchor=tk.CENTER, width=TABLE_COLUMN_WIDTH['TIMESTAMP'])
        table.add_column(column='ended_at', dtype=str, anchor=tk.CENTER, width=TABLE_COLUMN_WIDTH['TIMESTAMP'])


if __name__ == '__main__':
    from utils import test_toplevel_class
    test_toplevel_class(AccountOverdraftListView)

