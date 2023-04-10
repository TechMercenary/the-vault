import tkinter as tk
import re
from config import LOCAL_TIME_ZONE
import pendulum 


def datetime_timezone_converter(date_str: str, tz_from: str, tz_to: str) -> str:
    dt_from = pendulum.parser.parse(date_str, tz=tz_from)
    dt_to = dt_from.in_timezone(tz_to)
    return dt_to.to_datetime_string()

def get_datetime_from_db(value: str) -> str:
    return datetime_timezone_converter(
        date_str=value,
        tz_from='UTC',
        tz_to=LOCAL_TIME_ZONE,
    )
    
def get_datetime_to_db(value: str) -> str:
    return datetime_timezone_converter(
        date_str=value,
        tz_from=LOCAL_TIME_ZONE,
        tz_to='UTC',
    )

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
    width, height, offset_x, offset_y = tuple(
        int(x) for x in re.findall(r'[0-9]+', window.winfo_geometry())
    )
    return {
        'width': width,
        'height': height,
        'offset_x': offset_x,
        'offset_y': offset_y
    }
    
    
def set_geometry(window: tk.Toplevel | tk.Tk, width: int=None, height: int = None, offset_x: int = None, offset_y: int = None):
    
    assert (width is not None and height is not None) or (offset_x is not None and offset_y is not None ), \
        "Either (height and width) or (offset_x, offset_y) must both be provided"
    
    geometry_size = f"{width}x{height}" if width is not None else ''
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

    