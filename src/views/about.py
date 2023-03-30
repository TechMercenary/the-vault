from utils import center_window
import tkinter as tk
import tkinter.ttk as ttk
import platform
import sys
import sqlalchemy


class AboutDialog(tk.Toplevel):
    """About dialog view."""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Acerca de")
        self.configure(padx=5, pady=3)
        self.resizable(False, False)
        
        # Frame for the title
        title_frame = ttk.Frame(self)
        ttk.Label(title_frame, font="{Arial} 14 {bold}", text='The Vault').grid()
        title_frame.grid(column=0, row=0)
        
        # Frame for the labels' information
        info_frame = self.get_info_frame()
        info_frame.grid(column=0, ipadx=40, pady=10, row=1, sticky="ew")
        
        # Separator between labels and button
        ttk.Separator(self, orient="horizontal").grid(column=0, row=2, sticky="ew")
        
        # Clossing button
        ttk.Button(self, text='Cerrar', command=self.destroy).grid(column=0, pady=3, row=3, sticky="n")
        
        center_window(window=self, context_window=self.parent)


    def get_info_frame(self):
        """Get the frame with the labels' information."""
        
        info_frame = ttk.Frame(self)
        app_data = self.get_app_data()
        ttk.Label(info_frame, text=f"Python: {app_data['python_version']}").grid(column=0, row=0, sticky="w")
        ttk.Label(info_frame, text=f"Tkinter: {app_data['tkinter_version']}").grid(column=0, row=2, sticky="w")
        ttk.Label(info_frame, text=f"Tk: {app_data['tk_version']}").grid(column=0, row=3, sticky="w")
        ttk.Label(info_frame, text=f"Tcl: {app_data['tcl_version']}").grid(column=0, row=4, sticky="w")
        ttk.Label(info_frame, text=f"SQLAlchemy : {app_data['sqlalchemy_version']}").grid(column=0, row=5, sticky="w")
        ttk.Label(info_frame, text=f"Sistema Operativo: {app_data['operating_system']} ({app_data['architecture']})").grid(column=0, row=6, sticky="w")
        ttk.Label(info_frame, text=f"Pantalla: {app_data['screen_width']}x{app_data['screen_height']}").grid(column=0, row=7, sticky="w")
        return info_frame
        
    def get_app_data(self):
        """Get data about the application."""
        sqlalchemy_version = sqlalchemy.__version__
        python_version = sys.version.split()[0]
        tkinter_version = tk.Tcl().eval('info patchlevel')
        tk_version = tk.TkVersion 
        tcl_version = tk.TclVersion
        architecture = platform.architecture()[0]
        operating_system = platform.system()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        return {
            "python_version": python_version,
            "tkinter_version": tkinter_version,
            "tk_version": tk_version,
            "tcl_version": tcl_version,
            "sqlalchemy_version": sqlalchemy_version,
            "architecture": architecture,
            "operating_system": operating_system,
            "screen_width": screen_width,
            "screen_height": screen_height
        }


if __name__ == '__main__':
    from utils import test_toplevel_class
    test_toplevel_class(AboutDialog)
