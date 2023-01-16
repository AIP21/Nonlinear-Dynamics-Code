from contextlib import contextmanager
from decimal import Decimal

try: # python 3
    import tkinter as tk
    from tkinter import ttk
    from tkinter import messagebox
    from tkinter import filedialog
    from tkinter import simpledialog
    from tkinter import scrolledtext
    from tkinter import Scrollbar
    from tkinter import font as tkFont
    from tkinter import Image
    from tkinter import PhotoImage
    from tkinter import TclError
    
    from PIL import Image as PImage, ImageColor, ImageDraw, ImageFilter
    import base64
    import hashlib
    import io
    import math
    import platform
    import threading
    import numpy as np

    from tkinter import N
    from tkinter import NE
    from tkinter import E
    from tkinter import SE
    from tkinter import S
    from tkinter import SW
    from tkinter import W
    from tkinter import NW

    from tkinter import CENTER
    from tkinter import BOTTOM
    from tkinter import LEFT
    from tkinter import RIGHT
    from tkinter import TOP
    from tkinter import NONE

    from tkinter import NORMAL
    from tkinter import ACTIVE
    from tkinter import DISABLED

    from tkinter import FLAT
    from tkinter import RAISED
    from tkinter import SUNKEN
    from tkinter import GROOVE
    from tkinter import RIDGE

    from tkinter import TRUE
    from tkinter import FALSE

except ImportError: # python 2
    import Tkinter as tkinter
    import tkMessageBox as messagebox
    import tkFileDialog as filedialog
    import tkSimpleDialog as simpledialog
    import ScrolledText as scrolledtext
    from Tkinter import Scrollbar
    from Tkinter import ttk
    
    from Tkinter import N
    from Tkinter import NE
    from Tkinter import E
    from Tkinter import SE
    from Tkinter import S
    from Tkinter import SW
    from Tkinter import W
    from Tkinter import NW
    
    from Tkinter import CENTER
    from Tkinter import BOTTOM
    from Tkinter import LEFT
    from Tkinter import RIGHT
    from Tkinter import TOP
    from Tkinter import NONE
    
    from Tkinter import NORMAL
    from Tkinter import ACTIVE
    from Tkinter import DISABLED
    
    from Tkinter import FLAT
    from Tkinter import RAISED
    from Tkinter import SUNKEN
    from Tkinter import GROOVE
    from Tkinter import RIDGE
    
    from Tkinter import TRUE
    from Tkinter import FALSE
    
_root = None
_pack_side = None
_events = []
_radioVariable = None
DEFAULT_COLOR = '#333'

class AutoScrollbar(Scrollbar):
    """
    A scrollbar that hides itself if it's not needed.  only
    Works if you use the grid geometry manager.
    """
    def set(self, lo, hi):
        if float(lo) <=  0.0 and float(hi) >=  1.0:
            # grid_remove is currently missing from Tkinter!
            self.tk.call("grid", "remove", self)
        else:
            self.grid()
            
        Scrollbar.set(self, lo, hi)
        
    def pack(self, **kw):
        raise TclError("cannot use pack with this widget")
    
    def place(self, **kw):
        raise TclError("cannot use place with this widget")

class DEGraphWin(tk.Tk):
    """Window for displaying anything. This is the main window for DE Graphics
    
    Usage:
        win = DEGraphWin(title = "Test Window", width = 100, height = 100)
        with win:
            Label("Hello World!")

    Args:
        title (str): Title of the window
        width (int): Width of the window
        height (int): Height of the window
        **kw: Other arguments to pass to tk.Tk
    """
    def __init__(self, title = "Window", width = 100, height = 100, **kw):
        tk.Tk.__init__(self)
        self.title(title)
        self.kw = kw
        self.width = width
        self.height = height
        
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.geometry('%dx%d' % (width + 14, height))
    
    def close(self):
        self.destroy()
        
    def __enter__(self):
        global _root, _pack_side

        # Create scroll bar
        self.vscrollbar = AutoScrollbar(self)
        self.vscrollbar.grid(row = 0, column = 1, sticky = N+S)

        # Create canvas
        self.canvas = tk.Canvas(self, bd = 0, borderwidth = 0, yscrollcommand = self.vscrollbar.set, yscrollincrement = 7)
        self.canvas.grid(row = 0, column = 0, sticky = N+S+E+W)

        # Configure scroll bar for canvas
        self.vscrollbar.config(command = self.canvas.yview)

        # Make the canvas expandable
        self.grid_rowconfigure(0, weight = 1)
        self.grid_columnconfigure(0, weight = 1)

        # Create frame in canvas
        self.frame = tk.Frame(self.canvas, borderwidth = 0, bd = 0)
        self.frame.columnconfigure(0, weight = 1)
        self.frame.columnconfigure(1, weight = 1)
        
        self.frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion = self.canvas.bbox("all")
            ),
        )

        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        _pack_side = TOP
        _root = self.frame
        return self # was _root for some reason
    
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
    def remove(self, item):
        self.canvas.delete(item)
        
    def __exit__(self, type, value, traceback):
        global _root, _pack_side
        
        # puts tkinter widget onto canvas
        self.canvas.create_window(0, 0, anchor = NW, window = self.frame, width = int(self.canvas.config()['width'][4])-int(self.vscrollbar.config()['width'][4]))

        # deal with canvas being resized
        def resize_canvas(event):
            self.canvas.create_window(0, 0, anchor = NW, window = self.frame, width = int(event.width)-int(self.vscrollbar.config()['width'][4]))
        self.canvas.bind("<Configure>", resize_canvas)

        # updates geometry management
        self.frame.update_idletasks()

        # set canvas scroll region to all of the canvas
        self.canvas.config(scrollregion = self.canvas.bbox("all"))

        # set minimum window width
        self.update()
        self.minsize(self.winfo_width(), 0)
        self.config(**self.kw)
        
        self.frame.update()
        
        # start mainloop
        self.mainloop()
        
        # window closed...
        
        _pack_side = None
        
        # stop all ongoing _events
        [event.set() for event in _events]
        
class Slot(tk.Frame):
    def __init__(self, **kw):
        self.kw = kw
        
    def __enter__(self):
        global _root, _pack_side
        self._root_old = _root
        self._pack_side_old = _pack_side
        tk.Frame.__init__(self, self._root_old, **self.kw)
        self.pack( side = self._pack_side_old, fill = tk.X)
        _root = self
        
    def __exit__(self, type, value, traceback):
        global _root, _pack_side
        _root = self._root_old
        _pack_side = self._pack_side_old
        
class Stack(Slot):
    def __init__(self, **kw):
        Slot.__init__(self, **kw)

    def __enter__(self):
        global _pack_side
        Slot.__enter__(self)
        _pack_side = TOP
        return _root
        
class Flow(Slot):
    def __init__(self, **kw):
        Slot.__init__(self, **kw)

    def __enter__(self):
        global _pack_side
        Slot.__enter__(self)
        _pack_side = LEFT
        return _root

class Button(tk.Canvas):
    """A button with rounded edges

    Args:
        width: Width of the button
        height: Height of the button
        cornerRadius: Radius of the rounded corners
        padding: Padding between the edge of the button and the text
        color: Color of the button background
        textColor: Color of the button text
        command: Function to be called when the button is clicked
        commandArgs: Arguments to be passed to the command function
    """
    
    def __init__(self, text = "", width = 100, height = 40, cornerRadius = 10, padding = 6, color = "dark gray", textColor = "black", command = None, commandArgs = None, **kw):
        tk.Canvas.__init__(self, _root, width = width, height = height, borderwidth = 0, relief = "flat", highlightthickness = 0, **kw)
        self.command = command
        self.commandArgs = commandArgs
        self.kw = kw
        self.color = color

        # Create background rounded rectangle
        self.rect = RoundedRectangle(self, padding, padding, (width - padding * 2), (height - padding * 2), cornerRadius, self.color)
        self.rect.draw()
        
        # Create the text label
        self.textvariable = tk.StringVar()
        self.textvariable.set(self.kw['text'] if 'text' in self.kw else text)
        self.text = self.create_text(width / 2, height / 2, text = self.textvariable.get(), fill = textColor, font = "Arial 10 bold")
        
        # Bind actions
        self.bind("<ButtonPress-1>", self.onPress)
        self.bind("<ButtonRelease-1>", self.onRelease)
        self.bind('<Enter>', self.hoverEnter)
        self.bind('<Leave>', self.hoverExit)
    
        self.pack(side = _pack_side)
        
    def hoverEnter(self, event):
        # Grow the rect
        self.rect.shrink(4, 4)
        self.lift(self.text)
        
    def hoverExit(self, event):
        # Shrink the rect
        self.rect.shrink(-4, -4)
        self.lift(self.text)

    def onPress(self, event):
        # Darken the background color
        self.rect.color = "gray"
        self.rect.draw()
        self.lift(self.text)

    def onRelease(self, event):
        # Return the background color to normal
        self.rect.color = self.color
        self.rect.draw()
        self.lift(self.text)
        
        if self.command is not None:
            if self.commandArgs is not None:
                self.command(**self.commandArgs)
            else:
                self.command()
        
    @property
    def text(self):
        return self.textvariable.get()
    
    @text.setter
    def text(self, text):
        self.textvariable.set(text)

class Label(tk.Label):
    def __init__(self, text = "", **kw):
        self.kw   = kw
        self.textvariable = tk.StringVar()
        self.textvariable.set(self.kw['text'] if 'text' in self.kw else text)
        if 'text' in self.kw:
            del self.kw['text']
        tk.Label.__init__(self, _root, textvariable = self.textvariable, **kw)
        self.pack( side = _pack_side )
        
    @property
    def text(self):
        return self.textvariable.get()
    
    @text.setter
    def text(self, text):
        self.textvariable.set(text)
        
class Message(tk.Message):
    def __init__(self, text = "", **kw):
        self.kw = kw
        self.textvariable = tk.StringVar()
        self.textvariable.set(self.kw['text'] if 'text' in self.kw else text)
        if 'text' in self.kw:
            del self.kw['text']
        tk.Message.__init__(self, _root, textvariable = self.textvariable, anchor = NW, **kw)
        self.pack( side = _pack_side )
        
    @property
    def text(self):
        return self.textvariable.get()
    
    @text.setter
    def text(self, text):
        self.textvariable.set(text)
        
class repeat(threading.Thread):
    def __init__(self, interval = 1):
        global _events
        threading.Thread.__init__(self)
        self.interval = interval
        self.stopped = threading.Event()
        _events.append(self.stopped)
        
    def __call__(self, func):
        self.func = func
        self.start()
        return func
        
    def run(self):
        while not self.stopped.wait(self.interval):
            self.func()
            
class loop(threading.Thread):
    def __init__(self):
        global _events
        threading.Thread.__init__(self)
        self.stopped = threading.Event()
        _events.append(self.stopped)
        
    def __call__(self, func):
        self.func = func
        self.start()
        return func
        
    def run(self):
        while not self.stopped.isSet():
            self.func()
            
class TextBox(tk.Entry):
    def __init__(self, text = "", *args, **kwargs):
        self.textvariable = tk.StringVar()
        self.textvariable.set(text)
        tk.Entry.__init__(self, _root, textvariable = self.textvariable, **kwargs)
        self.pack(side = _pack_side)
    
    @property
    def text(self):
        return self.textvariable.get()
    
    @text.setter
    def text(self, text):
        self.textvariable.set(text)
        
def showInfo(title = "Info", message = "", **kw):
    messagebox.showinfo(title, message, **kw)
    
def showWarning(title = "Warning", message = "", **kw):
    messagebox.showwarning(title, message, **kw)

def showError(title = "Error", message = "", **kw):
    messagebox.showerror(title, message, **kw)
    
def askYesNo(title = "Question", message = "", **kw):
    return messagebox.askyesno(title, message, **kw)
    
def askOkCancel(title = "Question", message = "", **kw):
    return messagebox.askokcancel(title, message, **kw)
    
def askRetryCancel(title = "Retry?", message = "", **kw):
    return messagebox.askretrycancel(title, message, **kw)
    
def askYesNoCancel(title = "Retry?", message = "", **kw): # returns None on cancel
    return messagebox.askyesnocancel(title, message, **kw)
    
def askOpenFilename(**kw):
    return filedialog.askopenfilename(**kw)
    
def askSaveAsFilename(**kw):
    return filedialog.asksaveasfilename(**kw)
    
def askOpenFilenames(**kw):
    return filedialog.askopenfilenames(**kw)

@contextmanager
def askOpenFile(**kw):
    file = filedialog.askopenfile(**kw)
    try:
        yield file
    finally:
        file.close()

@contextmanager
def askOpenFiles(**kw):
    files = filedialog.askopenfiles(**kw)
    try:
        yield files
    finally:
        for file in files:
            file.close()

@contextmanager
def askSaveAsFile(**kw):
    file = filedialog.asksaveasfile(**kw)
    try:
        yield file
    finally:
        file.close()
    
def askDirectory(**kw):
    return filedialog.askdirectory(**kw)
    
def askInteger(title, prompt, **kw):
    return simpledialog.askinteger(title, prompt, **kw)
    
def askFloat(title, prompt, **kw):
    return simpledialog.askfloat(title, prompt, **kw)
    
def askString(title, prompt, **kw):
    return simpledialog.askstring(title, prompt, **kw)
    
class ScrollableText(scrolledtext.ScrolledText):
    def __init__(self, text = "", bg = 'white', height = 10, expand = True, editable = True, **kw):
        global _root, _pack_side
        scrolledtext.ScrolledText.__init__(self, _root, bg = bg, height = height, **kw)
        self.insert(tk.END, text)
        if not editable:
            self.config(state = DISABLED)
        self.pack(fill = tk.BOTH, side = _pack_side, expand = expand)
        
    @property
    def editable(self):
        return self.state == NORMAL
    
    @editable.setter
    def editable(self, editable):
        if editable:
            self.config(state = NORMAL)
        else:
            self.config(state = DISABLED)

class CheckBox(tk.Checkbutton):
    def __init__(self, text = "", checked = False, *args, **kwargs):
        self.textvariable = tk.StringVar()
        self.textvariable.set(text)
        self._checked = tk.BooleanVar()
        self._checked.set(checked)
        tk.Checkbutton.__init__(self, _root, textvariable = self.textvariable, variable = self._checked, **kwargs)
        self.pack(side = _pack_side)
        
    def __call__(self, func):
        self.config(command = lambda: func(self.checked))
        return func
    
    @property
    def text(self):
        return self.textvariable.get()
    
    @text.setter
    def text(self, text):
        self.textvariable.set(text)
        
    @property
    def checked(self):
        return self._checked.get()
    
    @checked.setter
    def checked(self, text):
        self._checked.set(text)

class RadioButton(tk.Radiobutton):
    def __init__(self, value, text = "", variable = None, checked = False, *args, **kwargs):
        global _radioVariable
        self.textvariable = tk.StringVar()
        self.textvariable.set(text)
        if variable is None:
            variable = _radioVariable
        self.variable = variable
        tk.Radiobutton.__init__(self, _root, textvariable = self.textvariable, variable = self.variable, value = value, **kwargs)
        self.pack(side = _pack_side)
        
    def __call__(self, func):
        self.config(command = lambda: func(self.variable.get()))
        return func
    
    @property
    def text(self):
        return self.textvariable.get()
    
    @text.setter
    def text(self, text):
        self.textvariable.set(text)
        
class RadioButtonGroup(object):
    def __enter__(self):
        global _radioVariable
        self.IntVar = tk.IntVar()
        _radioVariable = self.IntVar
        return self
        
    def __exit__(self, type, value, traceback):
        pass
        
    @property
    def number(self):
        return self.IntVar.get()
    
    @number.setter
    def number(self, n):
        self.IntVar.set(n)
        
class Spinner(tk.Spinbox):
    def __init__(self, **kw):
        tk.Spinbox.__init__(self, _root, **kw)
        self.pack(side = _pack_side)
        
    def __call__(self, func):
        self.config(command = lambda: func(self.get()))
        return func
        
    @property
    def value(self):
        return self.get()
        
class ScaleBar(tk.Scale):
    def __init__(self, range = None, enabled = True, **kw):
        tk.Scale.__init__(self, _root, **kw)
        self.pack(side = _pack_side)
        self._enabled = enabled
        
    def __call__(self, func):
        self.config(command = func)
        return func
        
    @property
    def value(self):
        return self.get()
        
    @value.setter
    def value(self, value):
        if not self.enabled:
            self.config(state = NORMAL)
        self.set(value)
        if not self.enabled:
            self.config(state = DISABLED)
        
    @property
    def enabled(self):
        return self._enabled
    
    @enabled.setter
    def enabled(self, enabled):
        self._enabled = enabled
        if enabled:
            self.config(state = NORMAL)
        else:
            self.config(state = DISABLED)
            
class OptionsMenu(tk.OptionMenu):
    def __init__(self, *values, **kw):
        self.values = values
        self.kw = kw
        self.StringVar = tk.StringVar()
        tk.OptionMenu.__init__(self, _root, self.StringVar, *values, **kw)
        self.pack(side = _pack_side)
        
    def __call__(self, func):
        self.StringVar = tk.StringVar()
        tk.OptionMenu.__init__(self, _root, self.StringVar, *self.values, command = func, **self.kw)
        self.pack(side = _pack_side)
        return func
        
    @property
    def option(self):
        return self.StringVar.get()
    
    @option.setter
    def option(self, option):
        self.StringVar.set(option)
    
class ListBox(tk.Listbox):
    def __init__(self, **kw):
        values = kw['values']
        if 'values' in kw:
            del kw['values']
        tk.Listbox.__init__(self, _root, **kw)
        self.pack(side = _pack_side)
        for item in values:
            self.insert(tk.END, item)
            
    @property
    def selection(self):
        return self.curselection()[0]

class ScrollableFrame(tk.Frame):
    """
    A frame that you can scroll through
    
    Usage:
        with ScrollableFrame(root):
            # add your widgets here
    """
    
    def __init__(self, **kw):
        self.kw = kw
        
    def __enter__(self):
        global _root, _pack_side

        self._root_old = _root
        self._pack_side_old = _pack_side
        tk.Frame.__init__(self, self._root_old, **self.kw)
        self.pack(side = self._pack_side_old, fill = tk.X)
        
        # create scroll bars
        self.vScrollBar = AutoScrollbar(self)
        self.vScrollBar.grid(row = 0, column = 1, sticky = N+S)

        # create canvas
        self.canvas = tk.Canvas(self, yscrollcommand = self.vScrollBar.set,  bd = 5)
        self.canvas.grid(row = 0, column = 0, sticky = N+S+E+W)

        # configure scroll bar for canvas
        self.vScrollBar.config(command = self.canvas.yview)

        # make the canvas expandable
        self.grid_rowconfigure(0, weight = 1)
        self.grid_columnconfigure(0, weight = 1)

        # create frame in canvas
        self.frame = tk.Frame(self.canvas)
        self.frame.columnconfigure(0, weight = 1)
        self.frame.columnconfigure(1, weight = 1)

        self.frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion = self.canvas.bbox("all"), width = e.width
            ),
        )

        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        _pack_side = TOP
        _root = self.frame

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def __exit__(self, type, value, traceback):
        global _root, _pack_side
        
        # puts tkinter widget onto canvas
        self.canvas.create_window(0, 0, anchor = NW, window = self.frame, width = int(self.canvas.config()['width'][4]) - int(self.vScrollBar.config()['width'][4]))

        # deal with canvas being resized
        def resize_canvas(event):
            self.canvas.create_window(0, 0, anchor = NW, window = self.frame, width = int(event.width)-int(self.vScrollBar.config()['width'][4]))
        self.canvas.bind("<Configure>", resize_canvas)

        # updates geometry management
        self.frame.update_idletasks()

        # set canvas scroll region to all of the canvas
        self.canvas.config(scrollregion = self.canvas.bbox("all"))

        # set minimum window width
        self.update()
        
        self.frame.update()
        
        # stop all ongoing _events
        [event.set() for event in _events]
        
        global _root, _pack_side
        _root = self._root_old
        _pack_side = self._pack_side_old

class Image(tk.Canvas):
    '''
    An image
    '''
    
    def __init__(self, path, width, height, imageWidth = None, imageHeight = None):
        '''
        Args:
            path: Path to the image
            width: Width of the image frame
            height: Height of the image frame
            imageWidth: Width of the image
            imageHeight: Height of the image
        '''
        widthImg = imageWidth or width
        heightImg = imageHeight or height
        img = resizeImage(PImage.open(path), size = (widthImg, heightImg), keep_aspect_ratio = False)
        img.save(path)
        self.image = PhotoImage(master = _root, file = path)#.zoom(int(widthImg // width), int(heightImg // height))
        super().__init__(_root, width = width, height = height, bd = 0, highlightthickness = 0)
        
        self.img = self.create_image(0, 0, image = self.image, anchor = tk.NW)
        self.pack(side = _pack_side)

class Plot(tk.Canvas):
    '''
    A 2D plot where you can draw points onto. (this time its FAST)
    
    Create the plot with an array of pre-configured pixels or just plot points onto it later.
    '''
    
    def __init__(self, width, height, backgroundColor, pixels = None):
        '''
        Args:
            pixels: Initialize this plot with an array of pixels. The array should be a 1D array of RGB tuples.
        '''
        self.width = width
        self.height = height
        super().__init__(_root, width = self.width, height = self.height, bd = 0, highlightthickness = 0)

        if pixels:
            self.image = PImage.fromarray(pixels)
        else:
            self.image = PImage.new("RGB", (width, height), backgroundColor)
        
        self.image.save("image.png")
            
        self.imageP = PhotoImage(master = _root, file = "image.png", height = self.height, width = self.width)
        
        self.imageObj = self.create_image(0, 0, image = self.imageP, anchor = tk.NW)
        self.pack(side = _pack_side)
        
    def plot(self, x, y, color):
        self.image.putpixel((x, y), color)
        
        self.image.save("image.png")
            
        self.imageP = PhotoImage(master = _root, file = "image.png", height = self.height, width = self.width)
        
        self.delete(self.imageObj)
        self.imageObj = self.create_image(0, 0, image = self.imageP, anchor = tk.NW)
        
class Graph(tk.Frame):
    """
    Tkinter native graph (pretty basic, but doesn't require heavy install).::
    NOTE: This must me created INSIDE of a frame, like so:
    with Stack():
        graph = tk_tools.Graph(
            x_min=-1.0,
            x_max=1.0,
            y_min=0.0,
            y_max=2.0,
            x_tick=0.2,
            y_tick=0.2,
            width=500,
            height=400
        )
        graph.grid(row=0, column=0)
        # create an initial line
        line_0 = [(x/10, x/10) for x in range(10)]
        graph.plot_line(line_0)
        
    :param x_min: the x minimum
    :param x_max: the x maximum
    :param y_min: the y minimum
    :param y_max: the y maximum
    :param x_tick: the 'tick' on the x-axis
    :param y_tick: the 'tick' on the y-axis
    :param options: additional valid tkinter.canvas options
    """

    def __init__(
        self,
        x_min: float,
        x_max: float,
        y_min: float,
        y_max: float,
        x_tick: float,
        y_tick: float,
        **options
    ):
        self._parent = _root
        super().__init__(self._parent, **options)

        self.canvas = tk.Canvas(self)
        self.canvas.grid(row=0, column=0)

        self.w = float(self.canvas.config("width")[4])
        self.h = float(self.canvas.config("height")[4])
        self.x_min = x_min
        self.x_max = x_max
        self.x_tick = x_tick
        self.y_min = y_min
        self.y_max = y_max
        self.y_tick = y_tick
        self.px_x = (self.w - 100) / ((x_max - x_min) / x_tick)
        self.px_y = (self.h - 100) / ((y_max - y_min) / y_tick)

        self.draw_axes()
        self.pack(side = _pack_side)

    def draw_axes(self):
        """
        Removes all existing series and re-draws the axes.
        :return: None
        """
        self.canvas.delete("all")
        rect = 50, 50, self.w - 50, self.h - 50

        self.canvas.create_rectangle(rect, outline="black")

        for x in self.frange(0, self.x_max - self.x_min + 1, self.x_tick):
            value = Decimal(self.x_min + x)
            if self.x_min <= value <= self.x_max:
                x_step = (self.px_x * x) / self.x_tick
                coord = 50 + x_step, self.h - 50, 50 + x_step, self.h - 45
                self.canvas.create_line(coord, fill="black")
                coord = 50 + x_step, self.h - 40

                label = round(Decimal(self.x_min + x), 1)
                self.canvas.create_text(coord, fill="black", text=label)

        for y in self.frange(0, self.y_max - self.y_min + 1, self.y_tick):
            value = Decimal(self.y_max - y)

            if self.y_min <= value <= self.y_max:
                y_step = (self.px_y * y) / self.y_tick
                coord = 45, 50 + y_step, 50, 50 + y_step
                self.canvas.create_line(coord, fill="black")
                coord = 35, 50 + y_step

                label = round(value, 1)
                self.canvas.create_text(coord, fill="black", text=label)

    def plot_point(self, x, y, visible=True, color="black", size=5):
        """
        Places a single point on the grid
        :param x: the x coordinate
        :param y: the y coordinate
        :param visible: True if the individual point should be visible
        :param color: the color of the point
        :param size: the point size in pixels
        :return: The absolute coordinates as a tuple
        """
        xp = (self.px_x * (x - self.x_min)) / self.x_tick
        yp = (self.px_y * (self.y_max - y)) / self.y_tick
        coord = 50 + xp, 50 + yp

        if visible:
            # divide down to an appropriate size
            size = int(size / 2) if int(size / 2) > 1 else 1
            x, y = coord

            self.canvas.create_oval(x - size, y - size, x + size, y + size, fill=color)

        return coord

    def plot_line(self, points: list, color="black", point_visibility=False):
        """
        Plot a line of points
        :param points: a list of tuples, each tuple containing an (x, y) point
        :param color: the color of the line
        :param point_visibility: True if the points should be individually visible
        :return: None
        """
        last_point = ()
        for point in points:
            this_point = self.plot_point(
                point[0], point[1], color=color, visible=point_visibility
            )

            if last_point:
                self.canvas.create_line(last_point + this_point, fill=color)
            last_point = this_point
            # print last_point

    @staticmethod
    def frange(start, stop, step, digits_to_round=3):
        """
        Works like range for doubles
        :param start: starting value
        :param stop: ending value
        :param step: the increment_value
        :param digits_to_round: the digits to which to round (makes floating-point numbers much easier to work with)
        :return: generator
        """
        while start < stop:
            yield round(start, digits_to_round)
            start += step
        
#region Shape graphics stuff
class GraphicsObject:
    def __init__(self, canvas, x, y, color):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.color = color
        self.id = None

    def draw(self):
        pass

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        self.canvas.move(self.id, dx, dy)

    def delete(self):
        self.canvas.delete(self.id)

# Rectangle
class Rectangle(GraphicsObject):
    def __init__(self, canvas, x, y, width, height, color):
        super().__init__(canvas, x, y, color)
        self.width = width
        self.height = height

    def draw(self):
        self.id = self.canvas.create_rectangle(self.x, self.y, self.x + self.width, self.y + self.height, fill=self.color)

# Ellipse
class Ellipse(GraphicsObject):
    def __init__(self, canvas, x, y, width, height, color):
        super().__init__(canvas, x, y, color)
        self.width = width
        self.height = height

    def draw(self):
        self.id = self.canvas.create_oval(self.x, self.y, self.x + self.width, self.y + self.height, fill=self.color)

# Line
class Line(GraphicsObject):
    def __init__(self, canvas, x1, y1, x2, y2, color):
        super().__init__(canvas, x1, y1, color)
        self.x2 = x2
        self.y2 = y2

    def draw(self):
        self.id = self.canvas.create_line(self.x, self.y, self.x2, self.y2, fill=self.color)

    def get_endpoints(self):
        return self.x, self.y, self.x2, self.y2

    def set_endpoints(self, x1, y1, x2, y2):
        self.x = x1
        self.y = y1
        self.x2 = x2
        self.y2 = y2

# Text
class Text(GraphicsObject):
    def __init__(self, canvas, x, y, text, color):
        super().__init__(canvas, x, y, color)
        self.text = text

    def draw(self):
        self.id = self.canvas.create_text(self.x, self.y, text=self.text, fill=self.color)

    def get_text(self):
        return self.text

    def set_text(self, text):
        self.text = text

# Polygon
class Polygon(GraphicsObject):
    def __init__(self, canvas, points, color):
        super().__init__(canvas, 0, 0, color)
        self.points = points

    def draw(self):
        self.id = self.canvas.create_polygon(self.points, fill=self.color)

    def get_points(self):
        return self.points

    def set_points(self, points):
        self.points = points

# Image
class GraphicsImage(GraphicsObject):
    def __init__(self, canvas, x, y, image):
        super().__init__(canvas, x, y, None)
        self.image = image

    def draw(self):
        self.id = self.canvas.create_image(self.x, self.y, image=self.image)

    def get_image(self):
        return self.image

    def set_image(self, image):
        self.image = image

# Arc
class Arc(GraphicsObject):
    def __init__(self, canvas, x, y, width, height, start, extent, color):
        super().__init__(canvas, x, y, color)
        self.width = width
        self.height = height
        self.start = start
        self.extent = extent

    def draw(self):
        self.id = self.canvas.create_arc(self.x, self.y, self.x + self.width, self.y + self.height, start=self.start, extent=self.extent, fill=self.color)

    def get_arc(self):
        return self.x, self.y, self.width, self.height, self.start, self.extent

    def set_arc(self, x, y, width, height, start, extent):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.start = start
        self.extent = extent

# Rounded rectangle
class RoundedRectangle(GraphicsObject):
    def __init__(self, canvas, x, y, width, height, radius, color):
        super().__init__(canvas, x, y, color)
        self.width = width
        self.height = height
        self.radius = radius

    def draw(self):
        self.canvas.delete(self.id)
        self.id = roundedRect(self.canvas, self.x, self.y, self.x + self.width, self.y + self.height, self.radius, fill = self.color)
    
    def shrink(self, x, y):
        self.width += x
        self.height += y
        self.x -= x / 2
        self.y -= y / 2
        self.draw()

#endregion

# Adapted from: https://github.com/vednig/shadowTk
class Shadow(tk.Tk):
    # Credit: https://stackoverflow.com/questions/28089942/difference-between-fill-and-expand-options-for-tkinter-pack-method/28090362

    '''
    Add shadow to a widget
    
    This class adds a squared shadow to a widget. The size, the position, and
    the color of the shadow can be customized at will. Different shadow
    behaviors can also be specified when hovering or clicking on the widget,
    with binding autonomously performed when initializing the shadow. If the
    widget has a 'command' function, it will be preserved when updating the
    shadow appearance.
    Note that enough space around the widget is required for the shadow to
    correctly appear. Moreover, other widgets nearer than shadow's size will be
    covered by the shadow.
    '''
    def __init__(self, widget, color = '#212121', size = 5, offset_x = 0, offset_y = 0,
                onhover = {}, onclick = {}):
        '''
        Bind shadow to a widget.
        Parameters:
        ----------
        widget : tkinter widget
            Widgets to which shadow should be bound.
        color : str, optional
            Shadow color in hex. The default is '#212121'.
        size : int or float, optional
            Size of the shadow. If int type, it is the size of the shadow out
            from the widget bounding box. If float type, it is a multiplier of
            the widget bounding box (e.g. if size = 2. then shadow is double in
            size with respect to widget). The default is 5.
        offset_x : int, optional
            Offset by which shadow will be moved in the horizontal axis. If
            positive, shadow moves toward right direction. The default is 0.
        offset_y : int, optional
            Offset by which shadow will be moved in the vertical axis. If
            positive, shadow moves toward down direction. The default is 0.
        onhover : dict, optional
            Specify the behavior of the shadow when widget is hovered. Keys may
            be: 'size', 'color', 'offset_x', 'offset_y'. If a key-value pair is
            not provided, normal behavior is maintained for that key. The
            default is {}.
        onclick : dict, optional
            Specify the behavior of the shadow when widget is clicked. Keys may
            be: 'size', 'color', 'offset_x', 'offset_y'. If a key-value pair is
            not provided, normal behavior is maintained for that key. The
            default is {}.
        Returns
        -------
        None.
        '''
        # Save parameters
        self.widget = widget
        self.normal_size = size
        self.normal_color = color
        self.normal_x = int(offset_x)
        self.normal_y = int(offset_y)
        self.onhover_size = onhover.get('size', size)
        self.onhover_color = onhover.get('color', color)
        self.onhover_x = onhover.get('offset_x', offset_x)
        self.onhover_y = onhover.get('offset_y', offset_y)
        self.onclick_size = onclick.get('size', size)
        self.onclick_color = onclick.get('color', color)
        self.onclick_x = onclick.get('offset_x', offset_x)
        self.onclick_y = onclick.get('offset_y', offset_y)
        
        # Get master and master's background
        self.master = widget.master
        self.to_rgb = tuple([el//257 for el in self.master.winfo_rgb(self.master.cget('bg'))])
        
        # Start with normal view
        self.__lines = []
        self.__normal()
        
        # Bind events to widget
        self.widget.bind("<Enter>", self.__onhover, add = '+')
        self.widget.bind("<Leave>", self.__normal, add = '+')
        self.widget.bind("<ButtonPress-1>", self.__onclick, add = '+')
        self.widget.bind("<ButtonRelease-1>", self.__normal, add = '+')
    
    def __normal(self, event = None):
        ''' Update shadow to normal state '''
        self.shadow_size = self.normal_size
        self.shadow_color = self.normal_color
        self.shadow_x = self.normal_x
        self.shadow_y = self.normal_y
        self.display()
    
    def __onhover(self, event = None):
        ''' Update shadow to hovering state '''
        self.shadow_size = self.onhover_size
        self.shadow_color = self.onhover_color
        self.shadow_x = self.onhover_x
        self.shadow_y = self.onhover_y
        self.display()
    
    def __onclick(self, event = None):
        ''' Update shadow to clicked state '''
        self.shadow_size = self.onclick_size
        self.shadow_color = self.onclick_color
        self.shadow_x = self.onclick_x
        self.shadow_y = self.onclick_y
        self.display()
    
    def __destroy_lines(self):
        ''' Destroy previous shadow lines '''
        for ll in self.__lines:
            ll.destroy()
        self.__lines = []
    
    def display(self):
        ''' Destroy shadow according to selected configuration '''
        def _rgb2hex(rgb):
            """
            Translates an rgb tuple of int to hex color
            """
            return "#%02x%02x%02x" % rgb
    
        def _hex2rgb(h):
                """
                Translates an hex color to rgb tuple of int
                """
                h = h.strip('#')
                return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
        
        # Destroy old lines
        self.__destroy_lines()
        
        # Get widget position and size
        self.master.update_idletasks()
        x0, y0, w, h = self.widget.winfo_x(), self.widget.winfo_y(), self.widget.winfo_width(), self.widget.winfo_height()
        x1 = x0 + w - 1
        y1 = y0 + h - 1
        
        # Get shadow size from borders
        if type(self.shadow_size) is int:
            wh_shadow_size = self.shadow_size
        else:
            wh_shadow_size = min([int(dim * (self.shadow_size - 1)) for dim in (w,h)])
        uldr_shadow_size = wh_shadow_size - self.shadow_y, wh_shadow_size - self.shadow_x, \
                        wh_shadow_size + self.shadow_y, wh_shadow_size + self.shadow_x
        uldr_shadow_size = {k:v for k,v in zip('uldr', uldr_shadow_size)}
        self.uldr_shadow_size = uldr_shadow_size
        
        # Prepare shadow color
        shadow_color = self.shadow_color
        if not shadow_color.startswith('#'):
            shadow_color = _rgb2hex(tuple([min(max(self.to_rgb) + 30, 255)] * 3))
        self.from_rgb = _hex2rgb(shadow_color)
        
        # Draw shadow lines
        max_size = max(uldr_shadow_size.values())
        diff_size = {k: max_size-ss for k,ss in uldr_shadow_size.items()}
        rs = np.linspace(self.from_rgb[0], self.to_rgb[0], max_size, dtype = int)
        gs = np.linspace(self.from_rgb[2], self.to_rgb[2], max_size, dtype = int)
        bs = np.linspace(self.from_rgb[1], self.to_rgb[1], max_size, dtype = int)
        rgbs = [_rgb2hex((r,g,b)) for r,g,b in zip(rs,gs,bs)]
        for direction, size in uldr_shadow_size.items():
            for ii, rgb in enumerate(rgbs):
                ff = tk.Frame(self.master, bg = rgb)
                self.__lines.append(ff)
                if direction == 'u' or direction == 'd':
                    diff_1 = diff_size['l']
                    diff_2 = diff_size['r']
                    yy = y0-ii+1+diff_size[direction] if direction  ==  'u' else y1+ii-diff_size[direction]
                    if diff_1 <=  ii < diff_size[direction]:
                        ff1 = tk.Frame(self.master, bg = rgb)
                        self.__lines.append(ff1)
                        ff1.configure(width = ii+1-diff_1, height = 1)
                        ff1.place(x = x0-ii+1+diff_size['l'], y = yy)
                    if diff_2 <=  ii < diff_size[direction]:
                        ff2 = tk.Frame(self.master, bg = rgb)
                        self.__lines.append(ff2)
                        ff2.configure(width = ii+1-diff_2, height = 1)
                        ff2.place(x = x1, y = yy)
                    if ii >=  diff_size[direction]:
                        ff.configure(width = x1-x0+ii*2-diff_size['l']-diff_size['r'], height = 1)
                        ff.place(x = x0-ii+1+diff_size['l'], y = yy)
                elif direction == 'l' or direction == 'r':
                    diff_1 = diff_size['u']
                    diff_2 = diff_size['d']
                    xx = x0-ii+1+diff_size[direction] if direction  ==  'l' else x1+ii-diff_size[direction]
                    if diff_1 <=  ii < diff_size[direction]:
                        ff1 = tk.Frame(self.master, bg = rgb)
                        self.__lines.append(ff1)
                        ff1.configure(width = 1, height = ii+1-diff_1)
                        ff1.place(x = xx, y = y0-ii+1+diff_size['u'])
                    if diff_2 <=  ii < diff_size[direction]:
                        ff2 = tk.Frame(self.master, bg = rgb)
                        self.__lines.append(ff2)
                        ff2.configure(width = 1, height = ii+1-diff_2)
                        ff2.place(x = xx, y = y1)
                    if ii >=  diff_size[direction]:
                        ff.configure(width = 1, height = y1-y0+ii*2-diff_size['u']-diff_size['d'])
                        ff.place(x = xx, y = y0-ii+1+diff_size['u'])

def roundedRect(canvas, x1, y1, x2, y2, radius = 25, **kwargs):
    points = [x1+radius, y1,
              x1+radius, y1,
              x2-radius, y1,
              x2-radius, y1,
              x2, y1,
              x2, y1+radius,
              x2, y1+radius,
              x2, y2-radius,
              x2, y2-radius,
              x2, y2,
              x2-radius, y2,
              x2-radius, y2,
              x1+radius, y2,
              x1+radius, y2,
              x1, y2,
              x1, y2-radius,
              x1, y2-radius,
              x1, y1+radius,
              x1, y1+radius,
              x1, y1]

    return canvas.create_polygon(points, **kwargs, smooth = True)

#region Adapted heavily from: https://github.com/Aboghazala/AwesomeTkinter
class ToolTip:
    def __init__(self, widget, text, waitTime = 500, xOffset = 10, yOffset = 10, **kwargs):
        """
        Tooltip widget
        Args:
            widget: any tkinter widget
            text: tooltip text
            waitTime: time in milliseconds to wait before showing tooltip
            xOffset(int): x - offset (pixels) of tooltip box from mouse pointer
            yoOfset(int): y - offset (pixels) of tooltip box from mouse pointer
            kwargs: parameters to be passed to tooltip label, e.g: , background = 'red', foreground = 'blue', etc
        """
        self.widget = widget
        self._text = text
        self.waitTime = waitTime  # milliseconds
        self.xOffset = xOffset
        self.yOffset = yOffset
        self.kwargs = kwargs
        self.tooltipWindow = None
        self.label = None
        self.id = None
        self._id1 = self.widget.bind("<Enter>", self.showTooltip, add = '+')
        self._id2 = self.widget.bind("<Leave>", self.hideTooltip, add = '+')
        self._id3 = self.widget.bind("<ButtonPress>", self.hideTooltip, add = '+')

        # for dynamic tooltip, use widget.update_tooltip('new text')
        widget.update_tooltip = self.updateTooltip

        widget.tooltip = self

    def __del__(self):
        try:
            self.widget.unbind("<Enter>", self._id1)
            self.widget.unbind("<Leave>", self._id2)
            self.widget.unbind("<ButtonPress>", self._id3)
            self.unschedule()
            self.hide()
        except tk.TclError:
            pass

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, txt):
        self._text = txt
        self.updateTooltip(txt)

    def updateTooltip(self, text):
        self._text = text
        try:
            self.label.config(text = text)
        except:
            pass

    def showTooltip(self, event = None):
        self.schedule()

    def hideTooltip(self, event = None):
        self.unschedule()
        self.hide()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waitTime, self.show)

    def unschedule(self):
        if self.id:
            self.widget.after_cancel(self.id)
            self.id = None

    def show(self):
        if self.tooltipWindow:
            return

        # tip text should be displayed away from the mouse pointer to prevent triggering leave event
        x = self.widget.winfo_pointerx() + self.xOffset
        y = self.widget.winfo_pointery() + self.yOffset

        self.tooltipWindow = tw = tk.Toplevel(self.widget)

        # show no border on the top level window
        tw.wm_overrideredirect(1)

        self.label = ttk.Label(tw, text = self.text, justify = tk.LEFT, padding = (5, 2),
                            background = "#ffffe0", relief = tk.SOLID, borderwidth = 1)

        lbl = self.label
        self.kwargs['background'] = self.kwargs.get('background') or self.kwargs.get('bg') or "#ffffe0"
        self.kwargs['foreground'] = self.kwargs.get('foreground') or self.kwargs.get('fg') or "black"
        configureWidget(lbl, **self.kwargs)

        # get text width using font, because .winfo_width() needs to call "update_idletasks()" to get correct width
        font = tkFont.Font(font = lbl['font'])
        txt_width = font.measure(self.text)

        # correct position to stay inside screen
        x = min(x, lbl.winfo_screenwidth() - txt_width)

        tw.wm_geometry("+%d+%d" % (x, y))
        lbl.pack()

    def hide(self):
        if self.tooltipWindow:
            self.tooltipWindow.destroy()
            self.tooltipWindow = None

class AutoWrappingLabel(tk.Label):
    """
    Auto-wrapping label
    Wrap text based on a widgets size
    """

    def __init__(self, text = "", justify = 'left', anchor = 'w', **kwargs):
        tk.Label.__init__(self, _root, text = text, justify = justify, anchor = anchor, **kwargs)
        self.bind('<Configure>', lambda event: self.config(wraplength = self.winfo_width()))
        self.pack(side = _pack_side)

class AutofitLabel(tk.Label):
    """
    Label that fits contents by using 3 dots in place of truncated text
    Should be autoresizable, e.g. packed with expand = True and fill = 'x', or grid with sticky = 'ew'
    """

    def __init__(self, text = "", justify = 'left', anchor = 'w', refreshTime = 500, **kwargs):
        self.refreshTime = refreshTime
        tk.Label.__init__(self, _root, text = text, justify = justify, anchor = anchor, **kwargs)
        self.originalText = ''
        self.id = None
        self.bind('<Configure>', self.schedule)
        self.pack(side = _pack_side)

    def schedule(self, *args):
        self.unschedule()
        self.id = self.after(self.refreshTime, self.update_text)

    def unschedule(self):
        if self.id:
            self.after_cancel(self.id)
            self.id = None

    def update_text(self, *args):
        txt = self.originalText or self['text']
        self.originalText = txt
        width = self.winfo_width()
        font = tkFont.Font(font = self['font'])
        txt_width = font.measure(txt)

        if txt_width > width:
            for i in range(0, len(txt), 2):
                num = len(txt) - i
                slice = num // 2
                new_txt = txt[0:slice] + ' ... ' + txt[-slice:]
                if font.measure(new_txt) < width:
                    self['text'] = new_txt
                    break
        else:
            self['text'] = self.originalText

class RadialProgressBar(tk.Frame):
    """
    A radial progress bar
    
    Basically this is a ttk horizontal progress bar modified using custom style layout and images
    
    Usage:
        bar = RadialProgressBar(frame1, size = 150, fg = 'green')
        bar.grid(padx = 10, pady = 10)
        bar.start()
    """

    # class variables to be shared between objects
    styles = []  # hold all style names created for all objects
    imgs = {}  # imgs{"size":{"color": img}}  example: imgs{"100":{"red": img}}

    def __init__(self, size = 100, bg = None, fg = 'cyan', text_fg = None, text_bg = None, font = None, font_size_ratio = 0.1,
                base_img = None, indicator_img = None, parent_bg = None, **extra):
        """
        Initialize progress bar
        
        Args:
            size (int or 2-tuple(int, int)) size of progressbar in pixels
            bg (str): color of base ring
            fg(str): color of indicator ring
            text_fg (str): percentage text color
            font (str): tkinter font for percentage text, e.g. 'any 20'
            font_size_ratio (float): font size to progressbar width ratio, e.g. for a progressbar size 100 pixels,
                                    a 0.1 ratio means font size 10
            base_img (tk.PhotoImage): base image for progressbar
            indicator_img (tk.PhotoImage): indicator image for progressbar
            parent_bg (str): color of parent container (automatically set, but could be overridden)
            extra: any extra kwargs
        """

        self.parent = _root
        self.parent_bg = parent_bg or getWidgetAttribute(self.parent, 'background')
        self.bg = bg or calculateContrastingColor(self.parent_bg, 30)
        self.fg = fg
        self.text_fg = text_fg or calculateFontColor(self.parent_bg)
        self.text_bg = text_bg or self.parent_bg
        self.size = size if isinstance(size, (list, tuple)) else (size, size)
        self.font_size_ratio = font_size_ratio
        self.font = font or f'any {int((sum(self.size) // 2) * self.font_size_ratio)}'

        self.base_img = base_img
        self.indicator_img = indicator_img

        self.var = tk.IntVar()

        # initialize super class
        tk.Frame.__init__(self, master = _root)

        # create custom progressbar style
        self.bar_style = self.createStyle()

        # create tk Progressbar
        self.bar = ttk.Progressbar(self, orient = 'horizontal', mode = 'determinate', length = self.size[0],
                                variable = self.var, style = self.bar_style)
        self.bar.pack()

        # percentage Label
        self.percent_label = ttk.Label(self.bar, text = '0%')
        self.percent_label.place(relx = 0.5, rely = 0.5, anchor = "center")

        # trace progressbar value to show in label
        self.var.trace_add('write', self.showPercentage)

        # set default attributes
        self.config(**extra)

        self.start = self.bar.start
        self.stop = self.bar.stop
        
        self.pack(side = _pack_side)

    def set(self, value):
        """set and validate progressbar value"""
        value = self.validateValue(value)
        self.var.set(value)

    def get(self):
        """get validated progressbar value"""
        value = self.var.get()
        return self.validateValue(value)

    def validateValue(self, value):
        """validate progressbar value
        """

        try:
            value = int(value)
            if value < 0:
                value = 0
            elif value > 100:
                value = 100
        except:
            value = 0

        return value

    def createStyle(self):
        """create ttk style for progressbar
        style name is unique and will be stored in class variable "styles"
        """

        # create unique style name
        bar_style = f'radial_progressbar_{len(RadialProgressBar.styles)}'

        # add to styles list
        RadialProgressBar.styles.append(bar_style)

        # create style object
        s = ttk.Style()

        RadialProgressBar.imgs.setdefault(self.size, {})
        self.indicator_img = self.indicator_img or RadialProgressBar.imgs[self.size].get(self.fg)
        self.base_img = self.base_img or RadialProgressBar.imgs[self.size].get(self.bg)

        if not self.indicator_img:
            img = createCircle(self.size, color = self.fg)
            self.indicator_img = PhotoImage(img)
            RadialProgressBar.imgs[self.size].update(**{self.fg: self.indicator_img})

        if not self.base_img:
            img = createCircle(self.size, color = self.bg)
            self.base_img = PhotoImage(img)
            RadialProgressBar.imgs[self.size].update(**{self.bg: self.base_img})

        # create elements
        indicator_element = f'top_img_{bar_style}'
        base_element = f'bottom_img_{bar_style}'

        try:
            s.element_create(base_element, 'image', self.base_img, border = 0, padding = 0)
        except:
            pass

        try:
            s.element_create(indicator_element, 'image', self.indicator_img, border = 0, padding = 0)
        except:
            pass

        # create style layout
        s.layout(bar_style,
                [(base_element, {'children':
                        [('pbar', {'side': 'left', 'sticky': 'nsew', 'children':
                                [(indicator_element, {'sticky': 'nswe'})]})]})])

        # configure new style
        s.configure(bar_style, pbarrelief = 'flat', borderwidth = 0, troughrelief = 'flat')

        return bar_style

    def showPercentage(self, *args):
        """display progressbar percentage in a label"""
        bar_value = self.get()
        self.percent_label.config(text = f'{bar_value}%')

    def config(self, **kwargs):
        """config widgets' parameters"""

        # create style object
        s = ttk.Style()

        kwargs = {k: v for k, v in kwargs.items() if v}
        self.__dict__.update(kwargs)

        # frame bg
        self['bg'] = self.parent_bg

        # bar style configure
        s.configure(self.bar_style, background = self.parent_bg, troughcolor = self.parent_bg)

        # percentage label
        self.percent_label.config(background = self.text_bg, foreground = self.text_fg, font = self.font)

class ProgressBar(tk.Canvas):
    def __init__(self, value = 0, range = 100, bg = None, fg = None, width = 100, height = 10):
        master_bg = getWidgetAttribute(_root, 'background')
        bg = bg or calculateContrastingColor(master_bg, 30)
        self.fg = fg or calculateFontColor(bg)
        self.height = height
        self.width = width
        super().__init__(_root, bg = bg, width = self.width, height = self.height, bd = 0, highlightthickness = 0)
        self.bind('<Configure>', self._redraw)
        self.pack(side = _pack_side)
        
        self.value = value
        self.range = range
        
        self.background = self.create_rectangle(0, 0, self.range, self.height, fill = bg, width = 0)
        self.bar = self.create_rectangle(0, 0, self.width * (self.value / self.range), self.height, fill = self.fg, width = 0)
        self._redraw()

    def setValue(self, value):
        """Set the bar's value"""
        self.value = value
        self._redraw()

    def setRange(self, range):
        """Set the bar's range"""
        self.range = range
        self._redraw()

    def _redraw(self, *args):
        # in case the window gets resized by user
        scale = self.winfo_width() / self.width
        self.width = self.winfo_width()
        
        self.delete(self.bar)
        self.bar = self.create_rectangle(0, 0, self.width * (self.value / self.range), self.height, fill = self.fg, width = 0)

        self.update_idletasks()

class ContextMenu(tk.Menu):
    """Context menu popup that appears on right click"""

    def __init__(self, parent, menu_items, callback = None, bg = 'white', fg = 'black', abg = 'blue', afg = 'white',
                bind_left_click = False, bind_right_click = True):
        """
        Initialize the context menu
        
        Args:
            parent: tkinter widget to show this menu when right clicked
            menu_items (iterable): a list of entries / options to show in right click menu, to add a separator you can
                                pass a string '---' as an item name
            callback (callable): any function or method that will be called when an option get selected,
                                should expect option name as a positional argument
            bg: background color
            fg: text color
            abg: background color on mouse hover
            afg: text color on mouse hover
            bind_left_click: if true will bind left mouse click
            bind_right_click: if true will bind right mouse click
        
        Usage:
            right_click_map = {'say hi': lambda x: print(x),  # x = 'say hi'
                            'help': show_help,
                            'blah blah': blah_callback,
                            }
            ContextMenu(my_listbox, right_click_map.keys(),
                        callback = lambda option: right_click_map[option](),
                        bg = 'white', fg = 'black', abg = blue, afg = 'white')
        """
        self.callback = callback

        # initialize super
        tk.Menu.__init__(self, parent, tearoff = 0, bg = bg, fg = fg, activebackground = abg, activeforeground = afg)

        for option in menu_items:
            if option  ==  '---':
                self.add_separator()
            else:
                self.add_command(label = f' {option}', command = lambda x = option: self.context_menu_handler(x))

        self.parent = parent

        # prevent random selection if menu shows under mouse 
        self.pressflag = False

        def onpress(event):
            self.pressflag = True

        def onrelease(event):
            # diable mouse release action if no mouse press
            if not self.pressflag:
                return 'break'
            else:
                self.pressflag = False

        trigger_buttons = []
        if bind_left_click:
            trigger_buttons.append(1)
        if bind_right_click:
            trigger_buttons +=  [2, 3]

        for i in trigger_buttons:
            if i  ==  1 and parent.winfo_class()  ==  'Button':
                parent['command'] = self.popup
                continue
            parent.bind(f"<Button-{i}>", self.popup, add = '+')
            self.bind(f'<{i}>', onpress, add = '+')
            self.bind(f'<ButtonRelease-{i}>', onrelease, add = '+')

    def popup(self, event = None):
        """show right click menu"""
        # x, y = event.x_root, event.y_root
        x = self.parent.winfo_pointerx()
        y = self.parent.winfo_pointery()
        self.tk_popup(x, y)

    def context_menu_handler(self, option):
        """handle selected option
        Args:
            option (str): selected option
        """

        if callable(self.callback):
            self.callback(option)
#endregion

#region Utils
def getOS():
    """identify current operating system
    Returns:
        (str): 'Windows', 'Linux', or 'Darwin' for mac
    """

    return platform.system()

def calculateMD5(binary_data):
    return hashlib.md5(binary_data).hexdigest()

def generateUniqueName(*args):
    """get md5 encoding for any arguments that have a string representation
    Returns:
        md5 string
    """
    name = ''.join([str(x) for x in args])

    try:
        name = calculateMD5(name.encode())
    except:
        pass

    return name

def invertColor(color):
    """return inverted hex color
    """
    color = colorToRGBA(color)
    r, g, b, a = color

    inverted_color = rgbToHex(255 - r, 255 - g, 255 - b)
    return inverted_color

def rgbToHex(r, g, b):
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)

def changeImageColor(img, new_color, old_color = None):
    """Change image color
    Args:
        img: pillow image
        new_color (str): new image color, ex: 'red', '#ff00ff', (255, 0, 0), (255, 0, 0, 255)
        old_color (str): color to be replaced, if omitted, all colors will be replaced with new color keeping
                        alpha channel.
    Returns:
        pillow image
    """

    # convert image to RGBA color scheme
    img = img.convert('RGBA')

    # load pixels data
    pixdata = img.load()

    # handle color
    new_color = colorToRGBA(new_color)
    old_color = colorToRGBA(old_color)

    for y in range(img.size[1]):
        for x in range(img.size[0]):
            alpha = pixdata[x, y][-1]
            if old_color:
                if pixdata[x, y]  ==  old_color:
                    r, g, b, _ = new_color
                    pixdata[x, y] = (r, g, b, alpha)
            else:
                r, g, b, _ = new_color
                pixdata[x, y] = (r, g, b, alpha)

    return img

def resizeImage(img, size, keep_aspect_ratio = True):
    """resize image using pillow
    Args:
        img (PIL.Image): pillow image object
        size(int or tuple(in, int)): width of image or tuple of (width, height)
        keep_aspect_ratio(bool): maintain aspect ratio relative to width
    Returns:
        (PIL.Image): pillow image
    """

    if isinstance(size, int):
        size = (size, size)

    # get ratio
    width, height = img.size
    requested_width = size[0]

    if keep_aspect_ratio:
        ratio = width / requested_width
        requested_height = height / ratio
    else:
        requested_height = size[1]

    size = (int(requested_width), int(requested_height))

    img = img.resize(size, resample = PImage.LANCZOS)

    return img

def mixImages(background_img, foreground_img):
    """paste an image on top of another image
    Args:
        background_img: pillow image in background
        foreground_img: pillow image in foreground
    Returns:
        pillow image
    """
    background_img = background_img.convert('RGBA')
    foreground_img = foreground_img.convert('RGBA')

    img_w, img_h = foreground_img.size
    bg_w, bg_h = background_img.size
    offset = ((bg_w - img_w) // 2, (bg_h - img_h) // 2)
    background_img.paste(foreground_img, offset, mask = foreground_img)

    return background_img

def colorToRGBA(color):
    """Convert color names or hex notation to RGBA,
    Args:
        color (str): color e.g. 'white' or '#333' or formats like #rgb or #rrggbb
    Returns:
        (4-tuple): tuple of format (r, g, b, a) e.g. it will return (255, 0, 0, 255) for solid red
    """

    if color is None:
        return None

    if isinstance(color, (tuple, list)):
        if len(color)  ==  3:
            r, g, b = color
            color = (r, g, b, 255)
        return color
    else:
        return ImageColor.getcolor(color, 'RGBA')

def isColorDark(color):
    """rough check if color is dark or light
    Returns:
        (bool): True if color is dark, False if light
    """
    r, g, b, a = colorToRGBA(color)

    # calculate lumina, reference https://stackoverflow.com/a/1855903
    lumina = (0.299 * r + 0.587 * g + 0.114 * b) / 255

    return True if lumina < 0.6 else False

def calculateFontColor(bg):
    """calculate font color based on given background
    Args:
        bg (str): background color
    Returns:
        (str): color name, e.g. "white" for dark background and "black" for light background
    """

    return 'white' if isColorDark(bg) else 'black'

def calculateContrastingColor(color, offset):
    """calculate a contrast color
    for darker colors will get a slightly lighter color depend on "offset" and for light colors will get a darker color
    Args:
        color (str): color
        offset (int): 1 to 254
    Returns:
        (str): color
    """

    r, g, b, a = colorToRGBA(color)
    if isColorDark(color):
        new_color = [x + offset if x + offset <=  255 else 255 for x in (r, g, b)]
    else:
        new_color = [x - offset if x - offset >=  0 else 0 for x in (r, g, b)]

    return rgbToHex(*new_color)

def textToImage(text, text_color, bg_color, size):
    """Not implemented"""
    pass
    # img = Image.new('RGBA', size, color_to_rgba(text_color))
    # draw = ImageDraw.Draw(img)
    # font = ImageFont.truetype(current_path + "s.ttf", size - int(0.15 * width))
    # draw.text((pad, -pad), str(num), font = font, fill = color_to_rgba(bg_color))

def createPILImage(fp = None, color = None, size = None, b64 = None):
    """
    A pillow Image object
    
    Args:
        fp: A filename (string), pathlib.Path object or a file object. The file object must implement read(), seek(),
            and tell() methods, and be opened in binary mode.
        color (str): color in tkinter format, e.g. 'red', '#3300ff', also color can be a tuple or a list of RGB,
                    e.g. (255, 0, 255)
        size (int or 2-tuple(int, int)): an image required size in a (width, height) tuple
        b64 (str): base64 hex representation of an image, if "fp" is given this parameter will be ignored
    
    Returns:
        pillow image object
    """

    if not fp and b64:
        fp = io.BytesIO(base64.b64decode(b64))

    img = Image.open(fp)

    # change color
    if color:
        img = changeImageColor(img, color)

    # resize
    if size:
        if isinstance(size, int):
            size = (size, size)
        img = resizeImage(img, size)

    return img

def createImage(fp = None, img = None, color = None, size = None, b64 = None):
    """
    A tkinter PhotoImage object that can modify size and color of original image
    
    Args:
        fp: A filename (string), pathlib.Path object or a file object. The file object must implement read(), seek(),
            and tell() methods, and be opened in binary mode.
        img (pillow image): if exist fp or b64 arguments will be ignored
        color (str): color in tkinter format, e.g. 'red', '#3300ff', also color can be a tuple or a list of RGB,
                    e.g. (255, 0, 255)
        size (int or 2-tuple(int, int)): an image required size in a (width, height) tuple
        b64 (str): base64 hex representation of an image, if "fp" is given this parameter will be ignored
    
    Returns:
        tkinter PhotoImage object
    """
    
    # create pillow image
    if not img:
        img = createPILImage(fp, color, size, b64)

    # create tkinter images using pillow ImageTk
    img = PhotoImage(img)

    return img

def createCircle(size = 100, thickness = None, color = 'black', fill = None, antialias = 4, offset = 0):
    """
    A high-quality circle
    Draws a bigger size circle and then resize it to the requested size
    Inspired by: https://stackoverflow.com/a/34926008
    
    Args:
        size (tuple or list, or int): outer diameter of the circle or width of bounding box
        thickness (int): outer line thickness in pixels
        color (str): outer line color
        fill (str): fill color, default is a transparent fill
        antialias (int): used to enhance outer line quality and make it smoother
        offset (int): correct cut edges of circle outline
    
    Returns:
        PIL image: a circle on a transparent image
    """

    if isinstance(size, int):
        size = (size, size)
    else:
        size = size

    fill_color = colorToRGBA(fill) or '#0000'

    requested_size = size

    # calculate thickness to be 2% of circle diameter
    thickness = thickness or max(size[0] * 2 // 100, 2)

    offset = offset or thickness // 2

    # make things bigger
    size = [x * antialias for x in requested_size]
    thickness *=  antialias

    # create a transparent image with a big size
    img = Image.new(size = size, mode = 'RGBA', color = '#0000')

    draw = ImageDraw.Draw(img)

    # draw circle with a required color
    draw.ellipse([offset, offset, size[0] - offset, size[1] - offset], outline = color, fill = fill_color, width = thickness)

    img = img.filter(ImageFilter.BLUR)

    # resize image back to the requested size
    img = img.resize(requested_size, Image.LANCZOS)

    # change color again will enhance quality (weird)
    if fill:
        img = changeImageColor(img, color, old_color = color)
        img = changeImageColor(img, fill, old_color = fill)
    else:
        img = changeImageColor(img, color)

    return img

def applyGradient(img, gradient = 'vertical', colors = None, keep_transparency = True):
    """
    A gradient color for a pillow image
    Args:
        img: pillow image
        gradient (str): vertical, horizontal, diagonal, radial
        colors (iterable): 2-colors for the gradient
        keep_transparency (bool): keep original transparency
    """

    size = img.size
    colors = colors or ['black', 'white']
    color1 = colorToRGBA(colors[0])
    color2 = colorToRGBA(colors[1])

    # load pixels data
    pixdata = img.load()

    if gradient in ('horizontal', 'vertical', 'diagonal'):

        for x in range(0, size[0]):
            for y in range(0, size[1]):

                if gradient  ==  'horizontal':
                    ratio1 = x / size[1]
                elif gradient  ==  'vertical':
                    ratio1 = y / size[1]
                elif gradient  ==  'diagonal':
                    ratio1 = (y + x) / size[1]

                ratio2 = 1 - ratio1

                r = ratio1 * color2[0] + ratio2 * color1[0]
                g = ratio1 * color2[1] + ratio2 * color1[1]
                b = ratio1 * color2[2] + ratio2 * color1[2]

                if keep_transparency:
                    a = pixdata[x, y][-1]
                else:
                    a = ratio1 * color2[3] + ratio2 * color1[3]

                r, g, b, a = (int(x) for x in (r, g, b, a))

                # Place the pixel
                img.putpixel((x, y), (r, g, b, a))

    elif gradient  ==  'radial':  # inspired by https://stackoverflow.com/a/30669765
        d = min(size)
        radius = d // 2

        for x in range(0, size[0]):
            for y in range(0, size[1]):

                # Find the distance to the center
                distance_to_center = math.sqrt((x - size[0] / 2) ** 2 + (y - size[1] / 2) ** 2)

                ratio1 = distance_to_center / radius
                ratio2 = 1 - ratio1

                r = ratio1 * color2[0] + ratio2 * color1[0]
                g = ratio1 * color2[1] + ratio2 * color1[1]
                b = ratio1 * color2[2] + ratio2 * color1[2]

                if keep_transparency:
                    a = pixdata[x, y][-1]
                else:
                    a = ratio1 * color2[3] + ratio2 * color1[3]
                r, g, b, a = (int(x) for x in (r, g, b, a))

                # Place the pixel
                img.putpixel((x, y), (r, g, b, a))

    return img

def scrollWithMouseWheel(widget, target = None, modifier = 'Shift', apply_to_children = False):
    """scroll a widget with mouse wheel
    Args:
        widget: tkinter widget
        target: scrollable tkinter widget, in case you need "widget" to catch mousewheel event and make another widget
                to scroll, useful for child widget in a scrollable frame
        modifier (str): Modifier to use with mousewheel to scroll horizontally, default is shift key
        apply_to_children (bool): bind all children
    Examples:
        scroll_with_mousewheel(my_text_widget, target = 'my_scrollable_frame')
        to make a scrollable canvas:
        for w in my_canvas:
            scroll_with_mousewheel(w, target = my_canvas)
    """

    def _scroll_with_mousewheel(widget):

        target_widget = target if target else widget

        def scroll_vertically(event):
            # scroll vertically  ----------------------------------
            if event.num  ==  4 or event.delta > 0:
                target_widget.yview_scroll(-1, "unit")

            elif event.num  ==  5 or event.delta < 0:
                target_widget.yview_scroll(1, "unit")

            return 'break'

        # bind events for vertical scroll ----------------------------------------------
        if hasattr(target_widget, 'yview_scroll'):
            # linux
            widget.bind("<Button-4>", scroll_vertically, add = '+')
            widget.bind("<Button-5>", scroll_vertically, add = '+')

            # windows and mac
            widget.bind("<MouseWheel>", scroll_vertically, add = '+')

        # scroll horizontally ---------------------------------------
        def scroll_horizontally(event):
            # scroll horizontally
            if event.num  ==  4 or event.delta > 0:
                target_widget.xview_scroll(-10, "unit")

            elif event.num  ==  5 or event.delta < 0:
                target_widget.xview_scroll(10, "unit")

            return 'break'

        # bind events for horizontal scroll ----------------------------------------------
        if hasattr(target_widget, 'xview_scroll'):
            # linux
            widget.bind(f"<{modifier}-Button-4>", scroll_horizontally, add = '+')
            widget.bind(f"<{modifier}-Button-5>", scroll_horizontally, add = '+')

            # windows and mac
            widget.bind(f"<{modifier}-MouseWheel>", scroll_horizontally, add = '+')

    _scroll_with_mousewheel(widget)

    def handle_children(w):
        for child in w.winfo_children():
            _scroll_with_mousewheel(child)

            # recursive call
            if child.winfo_children():
                handle_children(child)

    if apply_to_children:
        handle_children(widget)

def unbindMouseWheel(widget):
    """unbind mousewheel for a specific widget, e.g. combobox which have mouswheel scroll by default"""

    # linux
    widget.unbind("<Button-4>")
    widget.unbind("<Button-5>")

    # windows and mac
    widget.unbind("<MouseWheel>")

def getWidgetAttribute(widget, attr):
    """get an attribute of a widget
    Args:
        widget: tkinter widget "tk or ttk"
        attr (str): attribute or property e.g. 'background'
    Returns:
        attribute value, e.g. '#ffffff' for a background color
    """

    # if it is ttk based will get style applied, it will raise an error if the widget not a ttk
    try:
        style_name = widget.cget('style') or widget.winfo_class()
        s = ttk.Style()
        value = s.lookup(style_name, attr)
        return value
    except:
        pass

    try:
        # if it's a tk widget will use cget
        return widget.cget(attr)
    except:
        pass

    return None

def configureWidget(widget, **kwargs):
    """configure widget's attributes"""
    for k, v in kwargs.items():
        # set widget attribute
        try:
            # treat as a "tk" widget, it will raise if widget is a "ttk"
            widget.config(**{k: v})
            continue
        except:
            pass

        try:
            # in case above failed, it might be a ttk widget
            style_name = widget.cget('style') or widget.winfo_class()
            s = ttk.Style()
            s.configure(style_name, **{k: v})
        except:
            pass

def setDefaultTheme():
    # select tkinter theme required for things to be right on windows,
    # only 'alt', 'default', or 'classic' can work fine on windows 10
    s = ttk.Style()
    s.theme_use('default')

def themeCompatCheck(print_warning = False):
    """check if current theme is compatible
    Return:
        bool: True or False
    """
    compatible_themes = ['alt', 'default', 'classic']
    s = ttk.Style()
    current_theme = s.theme_use()
    if current_theme not in compatible_themes:
        if print_warning:
            print(f'AwesomeTkinter Warning: Widgets might not work properly under current theme ({current_theme})\n'
                f"compatible_themes are ['alt', 'default', 'classic']\n"
                f"you can set default theme using atk.set_default_theme() or style.theme_use('default')")
        return False

    return True

def centerWindow(window, width = None, height = None, set_geometry_wh = True, reference = None):
    """center a tkinter window on screen's center and set its geometry if width and height given
    Args:
        window (tk.root or tk.Toplevel): a window to be centered
        width (int): window's width
        height (int): window's height
        set_geometry_wh (bool): include width and height in geometry
        reference: tk window e.g parent window as a reference
    """

    # update_idletasks will cause a window to show early at the top left corner
    # then change position to center in non-proffesional way
    # window.update_idletasks()

    if width and height:
        if reference:
            refx = reference.winfo_x() + reference.winfo_width() // 2
            refy = reference.winfo_y() + reference.winfo_height() // 2
        else:
            refx = window.winfo_screenwidth() // 2
            refy = window.winfo_screenheight() // 2

        x = refx - width // 2
        y = refy - height // 2

        if set_geometry_wh:
            window.geometry(f'{width}x{height}+{x}+{y}')
        else:
            window.geometry(f'+{x}+{y}')

    else:
        window.eval('tk::PlaceWindow . center')

def color_rgb(r,g,b):
    '''r,g,b are intensities of r(ed), g(reen), and b(lue).
    Each value MUST be an integer in the interval [0,255]
    Returns color specifier string for the resulting color'''
    return "#%02x%02x%02x" % (r,g,b)
#endregion