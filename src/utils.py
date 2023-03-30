import functools
import tkinter as tk
import re
from tkinter import messagebox


def handle_db_errors(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__} with args {args} and kwargs {kwargs}")
        try:
            result = func(*args, **kwargs)
            if result.get('error'):
                messagebox.showerror("Error", result['error'])
            else:
                return result['result']
        except Exception as e:
            messagebox.showerror("Error", str(e))
    return wrapper


def test_toplevel_class(ToplevelClass: tk.Toplevel, *args, **kwargs):
    root = tk.Tk()
    center_window(window=root, context_window=None)
    toplevel = ToplevelClass(root, *args, **kwargs)
    toplevel_set_active(window=toplevel)
    
    root.mainloop()

    
def toplevel_set_active(window: tk.Toplevel | tk.Tk):
    window.deiconify()
    window.lift()
    window.focus_force()
    window.grab_set()
    window.grab_release()
    

def get_geometry(window: tk.Toplevel | tk.Tk):
    window.update_idletasks()
    width, height, offset_x, offset_y = tuple([int(x) for x in re.findall(r'[0-9]+', window.winfo_geometry())])
    return {
        'width': width,
        'height': height,
        'offset_x': offset_x,
        'offset_y': offset_y
    }
    
    
    
def set_geometry(window: tk.Toplevel | tk.Tk, width: int=None, height: int = None, offset_x: int = None, offset_y: int = None):
    if width is not None:
        assert height is not None, "Height must be provided if width is provided"
    if height is not None:
        assert width is not None, "Width must be provided if height is provided"
    if offset_x is not None:
        assert offset_y is not None, "Offset_y must be provided if offset_x is provided"
    if offset_y is not None:
        assert offset_x is not None, "Offset_x must be provided if offset_y is provided"
        
    geometry_size = ''
    if width is not None:
        geometry_size=f"{width}x{height}"
    geometry_offset = ''
    if offset_x is not None:
        geometry_offset_x = f"{'+' if offset_x > 0 else '-'}{offset_x}"
        geometry_offset_y = f"{'+' if offset_y > 0 else '-'}{offset_y}"
        geometry_offset = f"{geometry_offset_x}{geometry_offset_y}"

    window.geometry(f"{geometry_size}{geometry_offset}")
    
    
def center_window(window: tk.Toplevel | tk.Tk, context_window=None) -> None:
    """ Center a window on the screen relative to another window, or the screen if no other window is provided. """
    
    def get_nearest_ancester_geometry(widget):
        """Get the geometry of the nearest ancestor that has a geometry attribute."""
        if getattr(widget, 'geometry', None) is None:
            return get_nearest_ancester_geometry(widget.parent)
        else:
            return get_geometry(widget)

    if context_window is None:
        parent_geometry = {
            'width': window.winfo_screenwidth(),
            'height': window.winfo_screenheight(),
            'offset_x': 0,
            'offset_y': 0
        }
    else:
        parent_geometry = get_nearest_ancester_geometry(context_window)
    
    window_geometry = get_geometry(window)
    
    offset_x = int(parent_geometry['offset_x'] + parent_geometry['width']//2 - window_geometry['width']//2)
    offset_y = int(parent_geometry['offset_y'] + parent_geometry['height']//2 - window_geometry['height']//2)
    
    set_geometry(window, offset_x=offset_x, offset_y=offset_y)
   
