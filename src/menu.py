from config import logger
from functools import partial

from views.about import AboutDialog
from views.currencies import CurrencyListView
from views.chart_of_accounts import ChartOfAccountView
from views.providers import ProviderListView
from views.account_type import AccountTypeListView

import tkinter as tk


class AppMenu(tk.Menu):
    def __init__(self, parent: tk.Tk) -> None:
        super().__init__(parent)
        self.parent = parent

        self.add_cascade(label="File", menu=self.get_file_menu())
        self.add_cascade(label="Edit", menu=self.get_edit_menu())
        self.add_cascade(label="Actions", menu=self.get_actions_menu())
        self.add_cascade(label="Tables", menu=self.get_tables_menu())
        self.add_cascade(label="Reports", menu=self.get_reports_menu())
        self.add_cascade(label="Investments", menu=self.get_investments_menu())
        self.add_cascade(label="Tools", menu=self.get_tools_menu())
        self.add_command(label="About", command=partial(AboutDialog, parent=self.parent))


    def get_file_menu(self) -> tk.Menu:
        def get_import_menu(self) -> tk.Menu:
            import_menu = tk.Menu(self)
            import_menu.add_command(label="Import Santander CreditCard Summary", command=lambda: logger.debug("Selected Menu Import Santander CreditCard Summary"))
            import_menu.add_command(label="Import Santander Account Summary", command=lambda: logger.debug("Selected Menu Import Santander Account Summary"))
            
            return import_menu


        def get_export_menu(self) -> tk.Menu:
            export_menu = tk.Menu(self)
            export_menu.add_command(label="Export Transactions", command=lambda: logger.debug("Selected Menu Export Transactions"))
            return export_menu


        file_menu = tk.Menu(self)
        file_menu.add_cascade(label="Import", menu=get_import_menu(self))
        file_menu.add_cascade(label="Export", menu=get_export_menu(self))
        file_menu.add_separator()
        file_menu.add_cascade(label="Quit", command=self.quit)
        
        return file_menu


    def get_edit_menu(self) -> tk.Menu:
        edit_menu = tk.Menu(self)
        edit_menu.add_cascade(label="Preferences", command=lambda: logger.debug("Selected Menu Preferences"))

        return edit_menu


    def get_investments_menu(self) -> tk.Menu:
        investments_menu = tk.Menu(self)
        investments_menu.add_cascade(label="Cripotocurrencies", command=lambda: logger.debug("Selected Menu Cripotocurrencies"))
        investments_menu.add_cascade(label="Fixed Term Deposits", command=lambda: logger.debug("Selected Menu Fixed Term Deposits"))
        investments_menu.add_cascade(label="Stocks", command=lambda: logger.debug("Selected Menu Stocks"))
        investments_menu.add_cascade(label="Bonds", command=lambda: logger.debug("Selected Menu Bonds"))
        investments_menu.add_cascade(label="Mutual Funds", command=lambda: logger.debug("Selected Menu Mutual Funds"))
        investments_menu.add_cascade(label="ETFs", command=lambda: logger.debug("Selected Menu ETFs"))
        
        return investments_menu


    def get_reports_menu(self) -> tk.Menu:
        def get_financial_statements_menu(self) -> tk.Menu:
            financial_statements_menu = tk.Menu(self)
            financial_statements_menu.add_cascade(label="Balance Sheet", command=lambda: logger.debug("Selected Menu Balance Sheet"))
            financial_statements_menu.add_cascade(label="Income Statement", command=lambda: logger.debug("Selected Menu Income Statement"))
            financial_statements_menu.add_cascade(label="Cash Flow", command=lambda: logger.debug("Selected Menu Cash Flow"))
            financial_statements_menu.add_cascade(label="Net Worth", command=lambda: logger.debug("Selected Menu Net Worth"))
            
            return financial_statements_menu


        def get_investments_menu(self) -> tk.Menu:
            investments_menu = tk.Menu(self)
            investments_menu.add_cascade(label="Investment Performance", command=lambda: logger.debug("Selected Menu Investment Performance"))
            
            return investments_menu


        def get_forecast_menu(self) -> tk.Menu:
            forecast_menu = tk.Menu(self)
            forecast_menu.add_cascade(label="Inflation", command=lambda: logger.debug("Selected Menu Inflation"))
            forecast_menu.add_cascade(label="Budgets", command=lambda: logger.debug("Selected Menu Budgets"))
        
            return forecast_menu


        reports_menu = tk.Menu(self)
        reports_menu.add_cascade(label="Financial Statements", menu=get_financial_statements_menu(self))
        reports_menu.add_cascade(label="Investments", menu=get_investments_menu(self))
        reports_menu.add_cascade(label="Forecast", menu=get_forecast_menu(self))

        return reports_menu


    def get_actions_menu(self) -> tk.Menu:
        actions_menu = tk.Menu(self)
        actions_menu.add_cascade(label="Add Account", command=lambda: logger.debug("Selected Menu Add Account"))
        actions_menu.add_cascade(label="Scheduled Transactions", command=lambda: logger.debug("Selected Menu Scheduled Transactions"))

        return actions_menu


    def get_tables_menu(self) -> tk.Menu:
        tables_menu = tk.Menu(self)
        tables_menu.add_cascade(label="Chart of Accounts", command=partial(ChartOfAccountView, parent=self.parent))
        tables_menu.add_cascade(label="Account Types", command=partial(AccountTypeListView, parent=self.parent))
        tables_menu.add_cascade(label="Providers", command=partial(ProviderListView, parent=self.parent))
        tables_menu.add_cascade(label="Currencies", command=partial(CurrencyListView, parent=self.parent))
        tables_menu.add_cascade(label="Transactions", command=lambda: logger.debug("Selected Menu Transactinos"))
        tables_menu.add_cascade(label="Credit Cards", command=lambda: logger.debug("Selected Menu Credit Cards"))
        tables_menu.add_cascade(label="Credit Cards Summaries", command=lambda: logger.debug("Selected Menu Credit Cards Summaries"))

        return tables_menu


    def get_tools_menu(self) -> tk.Menu:
        tools_menu = tk.Menu(self)
        tools_menu.add_cascade(label="Budgets", command=lambda: logger.debug("Selected Menu Budgets"))
        tools_menu.add_cascade(label="Currency Exchange", command=lambda: logger.debug("Selected Menu Currency Exchange"))
        tools_menu.add_cascade(label="Loan Calculator", command=lambda: logger.debug("Selected Menu Loan Calculator"))

        return tools_menu


