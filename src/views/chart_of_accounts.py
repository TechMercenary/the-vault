from utils import center_window
import tkinter as tk
import tkinter.ttk as ttk

class ChartOfAccountsView(tk.Toplevel):
    """A view for the chart of accounts."""

    def __init__(self, parent: tk.Toplevel | tk.Tk):
        super().__init__(parent)
        self.parent = parent
        self.title("Cuentas Contables")
        self.main_frame = ttk.Frame(self)
        
        self.buttons_frame = self.get_buttons_frame()
        self.buttons_frame.grid(column=0, row=1, sticky="ew")
        self.buttons_frame.grid_anchor("center")
        self.buttons_frame.columnconfigure("all", pad=15)
        
        self.treeview_frame = self.get_treeview_frame()
        self.treeview_frame.grid(column=0, row=2, sticky="ew")
        
        self.close_frame = self.get_close_frame()
        self.close_frame.grid(column=0, row=3, sticky="ew")
        self.close_frame.grid_anchor("center")
        
        self.main_frame.grid(column=0, ipadx=3, ipady=3, row=0)
        self.main_frame.grid_anchor("center")

        center_window(window=self, context_window=self.parent)


    def get_buttons_frame(self):
        buttons_frame = ttk.Frame(self.main_frame, padding=10)
        ttk.Button(buttons_frame, text='Nueva Cuenta').grid(column=0, row=0)
        ttk.Button(buttons_frame, text='Nuevo Grupo').grid(column=1, row=0)
        ttk.Button(buttons_frame, text='Editar').grid(column=2, row=0)
        ttk.Button(buttons_frame, text='Borrar').grid(column=3, row=0)
        return buttons_frame


    def get_treeview_frame(self):
        treeview_frame = ttk.Frame(self.main_frame, width=200)
        
        self.coa_table = ttk.Treeview(treeview_frame, selectmode="extended")
        self.coa_table.grid(column=0, ipadx=100, row=0)
        
        ttk.Scrollbar(treeview_frame, orient="vertical", command=self.coa_table.yview).grid(column=1, row=0, sticky="ns")

        return treeview_frame


    def get_close_frame(self):
        close_frame = ttk.Frame(self.main_frame, padding=5)
        ttk.Button(close_frame, text='Cerrar', command=self.destroy).grid(column=0, row=0)
        return close_frame


if __name__ == '__main__':
    from utils import test_toplevel_class
    test_toplevel_class(ChartOfAccountsView)
