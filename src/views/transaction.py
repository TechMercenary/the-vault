from utils import center_window
from database.sqlite_handler import get_session
from database.models import Currency
from tkinter import messagebox
from sqlalchemy import func
from custom_widgets.table import CustomTable
from custom_widgets.toplevel import CustomTopLvel
from custom_widgets.basic_view import BasicView
import tkinter as tk
import tkinter.ttk as ttk
from config import logger


class TransactionListView(BasicView):
    def __init__(self, parent: tk.Toplevel | tk.Tk):
        super().__init__(parent, title="Transactions")
        
        self.add_input(key='id', label='ID', value='1')
        
        # self.treeview = CustomTable(parent=self.main_frame, columns=('id', 'date', 'description', 'amount', 'currency'))
        
        
if __name__ == '__main__':
    from utils import toplevel_set_active
    
    root = tk.Tk()
    
    toplevel = TransactionListView(root)
    center_window(window=root, context_window=None)
    toplevel_set_active(window=toplevel)
    center_window(window=toplevel, context_window=root)
    root.mainloop()

