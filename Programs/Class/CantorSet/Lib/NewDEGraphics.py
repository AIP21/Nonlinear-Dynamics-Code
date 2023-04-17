"""
This version of DEGraphics was created by Alexander Irausquin-Petit for AT Nonlinear Dynamics.
I wrote this from the ground up to be fast, easy to use, extensible, and good-looking all while sticking to Tkinter.

I used some code from other python libraries on GitHub, and have modified it to fit my needs.
Any code that I did not write myself is marked with a comment above the function or region of code, it contains the link to the GitHub repository where I found that code.
"""

from contextlib import contextmanager
from decimal import Decimal
import struct
import platform
import ctypes
import subprocess

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
    from tkinter import colorchooser

    try:
        from PIL import Image as PImage, ImageTk, ImageColor, ImageDraw, ImageFilter
        hasPIL = True
    except:
        hasPIL = False
    
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
_canvas = None

_events = []
_radioVariable = None
DEFAULT_COLOR = '#333'

class AutoScrollbar(Scrollbar):
    """
    A scrollbar that hides itself if it's not needed.
    Only works if you use the grid geometry manager.
    """
    def set(self, min, max):
        if float(min) <=  0.0 and float(max) >=  1.0:
            self.tk.call("grid", "remove", self)
        else:
            self.grid()
        
        Scrollbar.set(self, min, max)
        
    def pack(self, **kw):
        raise TclError("Cannot use pack with this widget")
    
    def place(self, **kw):
        raise TclError("Cannot use place with this widget")

class DEGraphWin(tk.Tk):
    """
    Window for displaying anything. This is the main window for DE Graphics
    
    Usage:
        win = DEGraphWin(title = "Test Window", width = 100, height = 100)
        with win:
            Label("Hello World!")

    Args:
        title (str): Title of the window
        width (int): Width of the window
        height (int): Height of the window
        showScrollbar (boolean): Whether or not to show a scrollbar (if the content is taller than the window)
        edgePadding (list): Padding to add to the edges of the window. [left, top, right, bottom]
        **kw: Other arguments to pass to tk.Tk
    """
    
    dragStart = (0, 0)
    
    def __init__(self, title = "DE Graphics Window", width = 500, height = 500, showScrollbar = False, edgePadding = [0, 0, 0, 0], debugMode = False, **kw):
        tk.Tk.__init__(self, sync = debugMode, **kw)
        self.title(title)
        self.kw = kw
        self.width = width
        self.height = height
        self.showScrollbar = showScrollbar
        self.edgePadding = edgePadding
        self.debugMode = debugMode
        
        # Set close protocol (x button on window top bar)
        self.protocol("WM_DELETE_WINDOW", self.close)
        
        # Set color to be used for background blur  
        # self.config(bg = 'green')
        # self.wm_attributes("-transparent", 'green')
        
        
        # Set window size
        self.geometry('%dx%d' % (width, height))
    
        # Blur the background
        # GlobalBlur(self.HWND)
        
        # Change window icon
        # self.tk.call('wm', 'iconphoto', self._w, PhotoImage(file = 'icon.png'))
    
    # '''
    # Set the frosted glass state of the window
    # '''
    # def setFrostedGlass(self, enabled):
    #     if enabled:
    #         self.wm_attributes("-transparent", 'green')
    #     else:
    #         self.wm_attributes("-transparent", 'pink') 

    def close(self):
        self.destroy()
    
    def onMouseWheel(self, event):
        self.canvas.yview_scroll(int(-1 * event.delta), 'units')
     
    def setOnClick(self, func):
        '''
        Set the function to call when this Image object is clicked
        
        Args:
            func: The function to call
        '''
        self.bind("<Button-1>", func)

    def setOnRightClick(self, func):
        '''
        Set the function to call when this Image object is right clicked
        
        Args:
            func: The function to call
        '''
        self.bind("<Button-3>", func)
    
    def remove(self, item):
        self.canvas.delete(item.id)
    
    def __enter__(self):
        global _root, _pack_side, theme

        if self.showScrollbar:
            # Create scroll bar
            self.vscrollbar = AutoScrollbar(self)
            self.vscrollbar.grid(row = 0, column = 1, sticky = N+S)

            # Create canvas
            self.canvas = tk.Canvas(self, bd = 0, borderwidth = 0, highlightthickness = 0, yscrollcommand = self.vscrollbar.set, yscrollincrement = 7)
            self.canvas.grid(row = 0, column = 0, sticky = N+S+E+W)

            # Configure scroll bar for canvas
            self.vscrollbar.config(command = self.canvas.yview)

            # Bind mouse wheel to canvas
            self.canvas.bind_all("<MouseWheel>", self.onMouseWheel)
        else:
            # Create canvas
            self.canvas = tk.Canvas(self, bd = 0, highlightthickness = 0, borderwidth = 0)
            self.canvas.grid(row = 0, column = 0, sticky = N+S+E+W)

        # Make the canvas expandable
        self.grid_rowconfigure(0, weight = 1)
        self.grid_columnconfigure(0, weight = 1)

        # Create frame in canvas
        self.frame = tk.Frame(self.canvas, borderwidth = 0, highlightthickness = 0, bd = 0)
        self.frame.columnconfigure(0, weight = 1)
        self.frame.columnconfigure(1, weight = 1)
        
        if self.showScrollbar:
            # Configure scroll region in frame
            self.frame.bind(
                "<Configure>",
                lambda e: self.canvas.configure(
                    scrollregion = self.canvas.bbox("all")
                ),
            )

        _pack_side = TOP
        _root = self.frame
        return self # Duct tape for a dumb bug, was _root for some reason
     
    def __exit__(self, type, value, traceback):
        global _root, _pack_side
        
        if self.showScrollbar:
            # Puts tkinter widget onto canvas
            self.canvas.create_window(self.edgePadding[0], self.edgePadding[1], anchor = NW, window = self.frame, width = int(self.canvas.config()['width'][4]) - int(self.vscrollbar.config()['width'][4]) - self.edgePadding[2] * 2, height = int(self.canvas.config()['height'][4]) - self.edgePadding[3] * 2)
        
            # Handle the canvas being resized
            def resize_canvas(event):
                self.canvas.create_window(self.edgePadding[0], self.edgePadding[1], anchor = NW, window = self.frame, width = int(event.width) - int(self.vscrollbar.config()['width'][4]) - self.edgePadding[2] * 2, height = int(event.height) - self.edgePadding[3] * 2)
        
            # Set canvas scroll region to the entire canvas
            self.canvas.config(scrollregion = self.canvas.bbox("all"))
        else:
            self.canvas.create_window(self.edgePadding[0], self.edgePadding[1], anchor = NW, window = self.frame, width = int(self.canvas.config()['width'][4]) - self.edgePadding[2] * 2, height = int(self.canvas.config()['height'][4]) - self.edgePadding[3] * 2)

            # Handle the canvas being resized
            def resize_canvas(event):
                self.canvas.create_window(self.edgePadding[0], self.edgePadding[1], anchor = NW, window = self.frame, width = int(event.width) - self.edgePadding[2] * 2, height = int(event.height) - self.edgePadding[3] * 2)
        
        self.canvas.bind("<Configure>", resize_canvas)
        
        # Update the geometry management
        self.frame.update_idletasks()

        # Set min window width
        self.update()
        self.minsize(self.winfo_width(), 0)
        self.config(**self.kw)
        
        self.frame.update()
        
        # Start mainloop
        self.mainloop()
                
        _pack_side = None
        
        # Stop all ongoing _events
        [event.set() for event in _events]

class Window(tk.Toplevel):
    """
    A window for displaying anything.
    
    Usage:
        win = Window(title = "Test Window", width = 100, height = 100)
        with win:
            Label("Hello World!")

    Args:
        title (str): Title of the window
        width (int): Width of the window
        height (int): Height of the window
        **kw: Other arguments to pass to tk.Tk
    """
    
    dragStart = (0, 0)
    showScrollbar = False
    edgePadding = (10, 10, 10, 10)
    
    def __init__(self, title = "Window", width = 500, height = 500, x = 100, y = 100, edgePadding = (10, 10, 10, 10), showScrollbar = False, **kw):
        tk.Toplevel.__init__(self)
        self.title(title)
        self.kw = kw
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.edgePadding = edgePadding
        self.showScrollbar = showScrollbar
        
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.geometry('%dx%d+%d+%d' % (self.width, self.height, self.x, self.y))
    
    def close(self):
        self.destroy()
    
    def onMouseWheel(self, event):
        self.canvas.yview_scroll(int(-1 * event.delta), 'units')
     
    def setOnClick(self, func):
        '''
        Set the function to call when this Image object is clicked
        
        Args:
            func: The function to call
        '''
        self.bind("<Button-1>", func)

    def setOnRightClick(self, func):
        '''
        Set the function to call when this Image object is right clicked
        
        Args:
            func: The function to call
        '''
        self.bind("<Button-3>", func)
    
    def remove(self, item):
        self.canvas.delete(item.id)
    
    def hideTitlebar(self):
        self.wm_overrideredirect(True)
    
    def showTitlebar(self):
        self.wm_overrideredirect(False)
    
    def __enter__(self):
        global _root, _pack_side

        if self.showScrollbar:
            # Create scroll bar
            self.vscrollbar = AutoScrollbar(self)
            self.vscrollbar.grid(row = 0, column = 1, sticky = N+S)

            # Create canvas
            self.canvas = tk.Canvas(self, bd = 0, borderwidth = 0, highlightthickness = 0, yscrollcommand = self.vscrollbar.set, yscrollincrement = 7)
            self.canvas.grid(row = 0, column = 0, sticky = N+S+E+W)

            # Configure scroll bar for canvas
            self.vscrollbar.config(command = self.canvas.yview)

            # Bind mouse wheel to canvas
            self.canvas.bind_all("<MouseWheel>", self.onMouseWheel)
        else:
            # Create canvas
            self.canvas = tk.Canvas(self, bd = 0, highlightthickness = 0, borderwidth = 0)
            self.canvas.grid(row = 0, column = 0, sticky = N+S+E+W)

        # Make the canvas expandable
        self.grid_rowconfigure(0, weight = 1)
        self.grid_columnconfigure(0, weight = 1)

        # Create frame in canvas
        self.frame = tk.Frame(self.canvas, borderwidth = 0, highlightthickness = 0, bd = 0)
        self.frame.columnconfigure(0, weight = 1)
        self.frame.columnconfigure(1, weight = 1)
        
        if self.showScrollbar:
            # Configure scroll region in frame
            self.frame.bind(
                "<Configure>",
                lambda e: self.canvas.configure(
                    scrollregion = self.canvas.bbox("all")
                ),
            )

        _pack_side = TOP
        _root = self.frame
        return self # Duct tape for a dumb bug, was _root for some reason
     
    def __exit__(self, type, value, traceback):
        global _root, _pack_side
        
        if self.showScrollbar:
            # Puts tkinter widget onto canvas
            self.canvas.create_window(self.edgePadding[0], self.edgePadding[1], anchor = NW, window = self.frame, width = int(self.canvas.config()['width'][4]) - int(self.vscrollbar.config()['width'][4]) - self.edgePadding[2] * 2, height = int(self.canvas.config()['height'][4]) - self.edgePadding[3] * 2)
        
            # Handle the canvas being resized
            def resize_canvas(event):
                self.canvas.create_window(self.edgePadding[0], self.edgePadding[1], anchor = NW, window = self.frame, width = int(event.width) - int(self.vscrollbar.config()['width'][4]) - self.edgePadding[2] * 2, height = int(event.height) - self.edgePadding[3] * 2)
        
            # Set canvas scroll region to the entire canvas
            self.canvas.config(scrollregion = self.canvas.bbox("all"))
        else:
            self.canvas.create_window(self.edgePadding[0], self.edgePadding[1], anchor = NW, window = self.frame, width = int(self.canvas.config()['width'][4]) - self.edgePadding[2] * 2, height = int(self.canvas.config()['height'][4]) - self.edgePadding[3] * 2)

            # Handle the canvas being resized
            def resize_canvas(event):
                self.canvas.create_window(self.edgePadding[0], self.edgePadding[1], anchor = NW, window = self.frame, width = int(event.width) - self.edgePadding[2] * 2, height = int(event.height) - self.edgePadding[3] * 2)
        
        self.canvas.bind("<Configure>", resize_canvas)
        
        # Update the geometry management
        self.frame.update_idletasks()

        # Set min window width
        self.update()
        self.minsize(self.winfo_width(), 0)
        self.config(**self.kw)
        
        self.frame.update()
        
        # Start mainloop
        self.mainloop()
                
        _pack_side = None
        
        # Stop all ongoing _events
        [event.set() for event in _events]

class Canvas(tk.Canvas):
    '''
    A canvas that can be used to draw GraphicsObjects on.
    '''
    offset = (0, 0)
    zoom = 1
    
    pressed = False
    dragging = False
    offsetPreDrag = (0, 0)
    dragOffset = (0, 0)
    
    drawnObjects = []
    
    interactionCallback = None
    
    def __init__(self, widgetAlignment = 'top', **kw):
        self.kw = kw
        self.widgetAlignment = widgetAlignment
        
    def __enter__(self):
        global _root, _pack_side, _canvas
        self._rootOld = _root
        self._canvasOld = _canvas
        
        tk.Canvas.__init__(self, _root, bd = 0, highlightthickness = 0, borderwidth = 0, **self.kw)
        self.pack(side = _pack_side, fill = 'both', expand = True)
        # self.canvas.pack()
        _canvas = self
        _root = self
        
        self.width = self.kw['width'] if 'width' in self.kw else self.winfo_width()
        self.height = self.kw['height'] if 'height' in self.kw else self.winfo_height()
        
        self.bind("<ButtonPress-1>", self.onMouseDown)
        self.bind("<B1-Motion>", self.onMouseDrag)
        self.bind("<ButtonRelease-1>", self.onMouseUp)
        self.bind("<MouseWheel>", self.onMouseWheel)
    
    def __exit__(self, type, value, traceback):
        global _root, _canvas
        _root = self._rootOld
        _canvas = self._canvasOld
    
    def onMouseWheel(self, event):
        if not self.dragging:
            # Zoom in and out of the center of the screen
            if event.delta > 0:
                self.zoom *= 1.1
            else:
                self.zoom /= 1.1
            
            # Update offset to keep the center of the screen in the same place
            # self.offset = (self.offset[0] - (self.width * self.zoom) / 2, self.offset[1] - (self.height * self.zoom) / 2)
            
            self.updateInteractibleDrawn()
        
        self.updateInteractibleDrawn()
    
    def onMouseDown(self, event):
        self.startDrag = (event.x, event.y)
        self.offsetPreDrag = self.offset
        self.pressed = True
    
    def onMouseDrag(self, event):
        if self.pressed:
            self.dragging = True

            self.offset = (self.offsetPreDrag[0] + (event.x - self.startDrag[0]), self.offsetPreDrag[1] + (event.y - self.startDrag[1]))
            self.updateInteractibleDrawn()
    
    def onMouseUp(self, event):
        self.dragging = False
        self.pressed = False
        
        self.updateInteractibleDrawn()
    
    def updateInteractibleDrawn(self):
        for obj in self.drawnObjects:
            if obj.shouldPanZoom:
                try:
                    obj.draw()
                except:
                    pass
        
        if self.interactionCallback:
            self.interactionCallback()
    
    def setInteractionCallback(self, func):
        '''
        Set the function to call when the user interacts with the canvas
        
        Args:
            func: The function to call
        '''
        self.interactionCallback = func
    
    def setOnClick(self, func):
        '''
        Set the function to call when this canvas is clicked
        
        Args:
            func: The function to call
        '''
        self.bind("<Button-1>", func)

    def setOnRightClick(self, func):
        '''
        Set the function to call when this canvas is right clicked
        
        Args:
            func: The function to call
        '''
        self.bind("<Button-3>", func)
    
    def setOnDrag(self, func):
        '''
        Set the function to call when the user drags the mouse on this canvas
        
        Args:
            func: The function to call
        '''
        self.bind("<B1-Motion>", func)
    
    def addDrawn(self, obj):
        '''
        Add a GraphicsObject to the canvas
        
        Args:
            obj: The GraphicsObject to add
        '''
        if obj not in self.drawnObjects:
            self.drawnObjects.append(obj)
    
    def removeDrawn(self, obj):
        '''
        Remove a GraphicsObject from the canvas
        
        Args:
            obj: The GraphicsObject to remove
        '''
        if obj in self.drawnObjects:
            self.drawnObjects.remove(obj)
        
        self.delete(obj.id)
    
    def resetView(self):
        '''
        Reset the view of the canvas
        '''
        self.offset = (0, 0)
        self.zoom = 1
        self.updateInteractibleDrawn()
    
    def isBoundingBoxVisible(self, x1, y1, width, height):
        '''
        Check if a bounding box is visible on the canvas
        
        Args:
            x1: The x coordinate of the top left corner of the bounding box
            y1: The y coordinate of the top left corner of the bounding box
            width: The width of the bounding box
            height: The height of the bounding box
        
        Returns:
            True if the bounding box is visible, False otherwise
        '''
        x2 = x1 + width
        y2 = y1 + height
        
        x1 = x1 * self.zoom + self.offset[0] + self.dragOffset[0]
        y1 = y1 * self.zoom + self.offset[1] + self.dragOffset[1]
        
        x2 = x2 * self.zoom + self.offset[0] + self.dragOffset[0]
        y2 = y2 * self.zoom + self.offset[1] + self.dragOffset[1]
        
        # AABB check
        if x1 > self.width or x2 < 0 or y1 > self.height or y2 < 0:
            return False
        
        return True
        
class Slot(tk.Frame):
    def __init__(self, **kw):
        self.kw = kw
        
    def __enter__(self):
        global _root, _pack_side
        self._root_old = _root
        self._pack_side_old = _pack_side
        tk.Frame.__init__(self, self._root_old, **self.kw)
        self.canvas = tk.Canvas(self, bd = 0, highlightthickness = 0, borderwidth = 0)
        self.pack(side = self._pack_side_old, fill = 'both')
        _root = self
    
    def __exit__(self, type, value, traceback):
        global _root, _pack_side
        _root = self._root_old
        _pack_side = self._pack_side_old
    
    def setOnClick(self, func):
        '''
        Set the function to call when this widget is clicked
        
        Args:
            func: The function to call
        '''
        self.bind("<Button-1>", func)

    def setOnRightClick(self, func):
        '''
        Set the function to call when this widget is right clicked
        
        Args:
            func: The function to call
        '''
        self.bind("<Button-3>", func)
    
    def setOnDrag(self, func):
        '''
        Set the function to call when the user drags the mouse on this widget
        
        Args:
            func: The function to call
        '''
        self.bind("<B1-Motion>", func)

class Stack(Slot):
    '''
    A frame with a layout that automatically places widgets from top to bottom
    '''
    def __init__(self, **kw):
        Slot.__init__(self, **kw)

    def __enter__(self):
        global _pack_side
        Slot.__enter__(self)
        _pack_side = TOP
        return _root

class Flow(Slot):
    '''
    A frame with a layout that automatically places widgets in from left to right
    '''
    def __init__(self, **kw):
        Slot.__init__(self, **kw)

    def __enter__(self):
        global _pack_side
        Slot.__enter__(self)
        _pack_side = LEFT
        return _root

class Layout(Slot):
    '''
    A frame with a layout that automatically places widgets in a customizable direction
    
    args:
        align: TOP, BOTTOM, LEFT, RIGHT
    '''
    def __init__(self, align = LEFT, **kw):
        Slot.__init__(self, **kw)
        self.align = align

    def __enter__(self):
        global _pack_side
        Slot.__enter__(self)
        _pack_side = self.align
        return _root

class HideableFrame(Slot):
    '''
    A frame with a layout that automatically places widgets in a configurable direction
    
    Can be hidden or shown by clicking its arrow button
    
    args:
        align: top, bottom, left, right
    '''
    
    hidden = False
    showHideButton = None
    
    def __init__(self, titleText = "", titleFont = "", align = "top", depth = 0, **kw):
        self.kw = kw
        self.titleText = titleText
        self.titleFont = titleFont if titleFont != "" else "Arial 12 bold"
        self.align = align
        self.depth = depth
    
        self.subFrame = None

        with self:
            self.headerFrame = Flow()

            with self.headerFrame:
                # Indent based on depth
                self.indent = Label("", width = self.depth * 5)
                
                # Show/hide button
                self.showHideButton = Button("⏷", width = 30, height = 30, cornerRadius = 25, command = self.toggleHidden)
                
                # Title text
                if self.titleText != "":
                    self.title = Label(self.titleText, padx = 10, justify = 'left', font = self.titleFont)
            
        self.subFrame = tk.Frame(self)
        self.subFrame.pack(side = self.align, fill = tk.X)
        
        # Toggle on click
        self.headerFrame.bind("<ButtonPress-1>", lambda func: self.toggleHidden())
        if self.titleText != "":
            self.title.bind("<ButtonPress-1>", lambda func: self.toggleHidden())
        
        # Hover effect
        self.originalBg = self.headerFrame.cget("bg")
        self.headerFrame.bind("<Enter>", self.hoverEnter)
        self.headerFrame.bind("<Leave>", self.hoverLeave)
        
        self.show()
    
    def hoverEnter(self, func):
        hoverColor = colorRGB(230, 230, 230)
        
        self.headerFrame.config(bg = hoverColor)
        self.showHideButton.config(bg = hoverColor)
        self.indent.config(bg = hoverColor)
        
        if self.titleText != "":
            self.title.config(bg = hoverColor)
    
    def hoverLeave(self, func):
        self.headerFrame.config(bg = self.originalBg)
        self.showHideButton.config(bg = self.originalBg)
        self.indent.config(bg = self.originalBg)

        if self.titleText != "":
            self.title.config(bg = self.originalBg)
        
    def toggleHidden(self):
        if self.hidden:
            self.show()
        else:
            self.hide()
    
    def hide(self):
        self.hidden = True
        self.showHideButton.text = "⏵"
        
        # Hide subframe
        self.subFrame.pack_forget()
        
        # Update geometry
        self.pack()
    
    def show(self):
        self.hidden = False
        self.showHideButton.text = "⏷"

        # Show subframe
        self.subFrame.pack(side = self.align, fill = tk.X)
        
        # Update geometry
        self.pack()
      
    def __enter__(self):
        global _root, _pack_side
        self._root_old = _root
        self._pack_side_old = _pack_side
        tk.Frame.__init__(self, self._root_old, **self.kw)
        self.pack(side = self._pack_side_old, fill = tk.X)
        
        if self.subFrame == None:
            _root = self
        else:
            _root = self.subFrame
    
    def __exit__(self, type, value, traceback):
        global _root, _pack_side
        _root = self._root_old
        _pack_side = self._pack_side_old

class ScrollableFrame(tk.Frame):
    """
    A frame that you can scroll through. It has a scroll bar.
    
    Usage:
        with ScrollableFrame():
            # add your widgets here
    """
    
    def __init__(self, **kw):
        self.kw = kw
    
    def onMouseWheel(self, event):
        self.canvas.yview_scroll(int(-1 * event.delta), 'units')

    def __enter__(self):
        global _root, _pack_side
        self._root_old = _root
        self._pack_side_old = _pack_side
        tk.Frame.__init__(self, self._root_old, **self.kw)
        
        # Create scroll bar
        self.vscrollbar = AutoScrollbar(self)
        self.vscrollbar.grid(row = 0, column = 1, sticky = N+S)

        # Make the canvas expandable
        self.grid_rowconfigure(0, weight = 1)
        self.grid_columnconfigure(0, weight = 1)

        # Create canvas
        self.canvas = tk.Canvas(self, bd = 0, borderwidth = 0, highlightthickness = 0, yscrollcommand = self.vscrollbar.set, yscrollincrement = 7)
        self.canvas.grid(row = 0, column = 0, sticky = N+S+E+W)

        # Configure scroll bar for canvas
        self.vscrollbar.config(command = self.canvas.yview)

        # Bind mouse wheel to canvas
        self.canvas.bind_all("<MouseWheel>", self.onMouseWheel)
        
        # Create frame in canvas
        self.frame = tk.Frame(self.canvas, borderwidth = 0, highlightthickness = 0, bd = 0)
        self.frame.columnconfigure(0, weight = 1)
        self.frame.columnconfigure(1, weight = 1)
        
        # Configure scroll region in frame
        self.frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion = self.canvas.bbox("all")
            ),
        )
        
        self.pack(side = self._pack_side_old, fill = tk.X)
        _pack_side = TOP
        _root = self.frame
        return self.frame
    
    def __exit__(self, type, value, traceback):
        global _root, _pack_side
        
        # Puts tkinter widget onto canvas
        self.canvas.create_window(0, 0, anchor = NW, window = self.frame, width = int(self.canvas.config()['width'][4]) - int(self.vscrollbar.config()['width'][4]))
    
        # Handle the canvas being resized
        def resize_canvas(event):
            self.canvas.create_window(0, 0, anchor = NW, window = self.frame, width = int(event.width) - int(self.vscrollbar.config()['width'][4]))
    
        # Set canvas scroll region to the entire canvas
        self.canvas.config(scrollregion = self.canvas.bbox("all"))
        self.canvas.bind("<Configure>", resize_canvas)
        
        self.update()
        
        self.frame.update()
        
        _root = self._root_old
        _pack_side = self._pack_side_old

class Separator(tk.Canvas):
    def __init__(self, width, height, horizontalSpacing, verticalSpacing, color = (100, 100, 100), **kw):
        self.kw = kw
        tk.Canvas.__init__(self, _root, width = width + horizontalSpacing * 2, height = height + verticalSpacing * 2, highlightthickness = 0, **self.kw)
        self.color = color
        
        if width != 0 and height != 0:
            rect = Rectangle(horizontalSpacing, verticalSpacing, width, height, color = colorRGB(*self.color), outline = colorRGB(*self.color), canvas = self)
            rect.draw()
        
        self.pack(side = _pack_side)

class Button(tk.Canvas):
    """
    A button with rounded edges. Has a hover and click effect.

    Args:
        text: The button's label text
        width: Width of the button
        height: Height of the button
        cornerRadius: Radius of the rounded corners
        padding: Padding between the edge of the button and the text
        color: Color of the button background
        textColor: Color of the button text
        textFont: Font of the button text
        command: Function to be called when the button is clicked
        commandArgs: Arguments to be passed to the command function
    """
    
    hoverEffect = ("grow/darken", (4, 4, (20, 20, 20)))
    enabled = True
    mouseOver = False
    
    def __init__(self, text, width = 120, height = 40, cornerRadius = 10, padding = 6, color = (200, 200, 200), backgroundColor = (240, 240, 240), textColor = (0, 0, 0), textFont = "Arial 10 bold", command = None, commandArgs = None, **kw):
        tk.Canvas.__init__(self, _root, width = width, height = height, borderwidth = 0, bg = colorRGB(*backgroundColor), relief = "flat", highlightthickness = 0, **kw)
        self.command = command
        self.commandArgs = commandArgs
        self.kw = kw
        self.color = color
        self.textColor = textColor
        self.width = width
        self.height = height
        self.padding = padding

        # Create background rounded rectangle
        self.rect = RoundedRectangle(padding, padding, width - padding * 2, height - padding * 2, cornerRadius, color = colorRGB(*self.color), canvas = self)
        self.rect.draw()
        
        # Create the text label
        self.labelText = text
        self.label = self.create_text(width / 2, height / 2, width = width - (padding + 5) * 2, text = self.labelText, fill = colorRGB(*self.textColor), font = textFont)
        
        # Bind actions
        self.bind("<ButtonPress-1>", self.onPress)
        self.bind("<ButtonRelease-1>", self.onRelease)
        self.bind('<Enter>', self.hoverEnter)
        self.bind('<Leave>', self.hoverExit)
    
        self.pack(side = _pack_side)
    
    def setColor(self, color):
        '''
        Set the button's color
        '''
        
        self.color = color
        self.rect.color = colorRGB(*self.color)
        self.rect.draw()
        
        # Keep text on top
        self.lift(self.label)
    
    def setHoverEffect(self, hoverEffect):
        '''
        Set the button's hover effect
        
        Options:
            "grow (x, y)": The button will grow when hovered over (default).
            "darken (r, g, b)": The button will darken when hovered over.
            "grow/darken (x, y, (r, g, b))": The button will grow and darken when hovered over.
            "color (r, g, b)": The button will change color when hovered over.
            "none": The button will not have a hover effect
        '''
        
        self.hoverEffect = hoverEffect
    
    def hoverEnter(self, event):
        self.mouseOver = True
        
        if not self.enabled:
            return
        
        if self.hoverEffect[0] == "grow":
            # Grow the rect
            self.rect.grow(self.hoverEffect[1][0], self.hoverEffect[1][1])
        elif self.hoverEffect[0] == "darken":
            # Darken the rect
            self.rect.color = colorRGB(clamp(self.color[0] - self.hoverEffect[1][0], 0, 255), clamp(self.color[1] - self.hoverEffect[1][1], 0, 255), clamp(self.color[2] - self.hoverEffect[1][2], 0, 255))
        elif self.hoverEffect[0] == "grow/darken":
            # Grow and darken the rect
            self.rect.grow(self.hoverEffect[1][0], self.hoverEffect[1][1])
            self.rect.color = colorRGB(clamp(self.color[0] - self.hoverEffect[1][2][0], 0, 255), clamp(self.color[1] - self.hoverEffect[1][2][1], 0, 255), clamp(self.color[2] - self.hoverEffect[1][2][2], 0, 255))
        elif self.hoverEffect[0] == "color":
            # Change the rect color
            self.rect.color = colorRGB(*self.hoverEffect[1])
        elif self.hoverEffect[0] == "none":
            pass
        
        self.rect.draw()
        self.lift(self.label)
        
    def hoverExit(self, event):
        self.mouseOver = False
        
        if not self.enabled:
            return
        
        if self.hoverEffect[0] == "grow":
            # Shrink the rect
            # self.rect.shrink(-self.hoverEffect[1][0], -self.hoverEffect[1][1])
            self.rect.setPos(self.padding, self.padding)
            self.rect.resize(self.width - self.padding * 2, self.height - self.padding * 2)
        elif self.hoverEffect[0] == "darken":
            # Return the rect color to normal
            self.rect.color = colorRGB(*self.color)
        elif self.hoverEffect[0] == "grow/darken":
            # Return the rect size and color to normal
            # self.rect.shrink(-self.hoverEffect[1][0], -self.hoverEffect[1][1])
            self.rect.setPos(self.padding, self.padding)
            self.rect.resize(self.width - self.padding * 2, self.height - self.padding * 2)
            self.rect.color = colorRGB(*self.color)
        elif self.hoverEffect[0] == "color":
            # Return the rect color to normal
            self.rect.color = colorRGB(*self.color)
        elif self.hoverEffect[0] == "none":
            pass
        
        self.rect.draw()
        self.lift(self.label)

    def onPress(self, event):
        if not self.enabled:
            return
        
        # Darken the background color
        self.rect.color = colorRGB(clamp(self.color[0] - 50, 0, 255), clamp(self.color[1] - 50, 0, 255), clamp(self.color[2] - 50, 0, 255))
        
        # Slightly shrink the rect
        self.rect.grow(-2, -2)
        
        self.rect.draw()
        
        self.lift(self.label)
    
    def onRelease(self, event):
        if not self.enabled:
            return
        
        # Return the background color to normal (or hover color if hovering over button)
        if self.mouseOver:
            self.rect.color = colorRGB(clamp(self.color[0] - 50, 0, 255), clamp(self.color[1] - 50, 0, 255), clamp(self.color[2] - 50, 0, 255))
            self.rect.resize(self.width - self.padding * 2, self.height - self.padding * 2)
            self.rect.setPos(self.padding, self.padding)
            
            self.hoverEnter(None)
        else:
            self.rect.color = colorRGB(clamp(self.color[0] - 50, 0, 255), clamp(self.color[1] - 50, 0, 255), clamp(self.color[2] - 50, 0, 255))
            self.rect.resize(self.width - self.padding * 2, self.height - self.padding * 2)
            self.rect.setPos(self.padding, self.padding)
        
        self.rect.draw()
        
        self.lift(self.label)
        
        if self.mouseOver:
            if self.command is not None:
                if self.commandArgs is not None:
                    self.command(*self.commandArgs)
                else:
                    self.command()
    
    def disable(self):
        if self.mouseOver:
            self.hoverExit(None)
        
        self.enabled = False
        
        self.config(state = tk.DISABLED)
        
        # Lighten the text color and darken the background color
        self.itemconfig(self.label, fill = colorRGB(min(255, self.textColor[0] + 100), min(255, self.textColor[1] + 100), min(255, self.textColor[2] + 100)))
        self.rect.color = colorRGB(max(0, self.color[0] - 50), max(0, self.color[1] - 50), max(0, self.color[2] - 50))
    
    def enable(self):
        self.enabled = True
        
        self.config(state = tk.NORMAL)
        
        # Return the text color and the background color to normal
        self.itemconfig(self.label, fill = colorRGB(max(0, self.textColor[0] - 100), max(0, self.textColor[1] - 100), max(0, self.textColor[2] - 100)))
        self.rect.color = colorRGB(*self.color)
    
    def isEnabled(self):
        return self.enabled
    
    @property
    def text(self):
        return self.labelText
    
    @text.setter
    def text(self, text):
        self.labelText = text
        self.itemconfig(self.label, text = self.labelText)

class Label(tk.Label):
    '''
    A text label.

    Args:
        text: The label's text
        color: Color of the text
        font: Font of the text
        **kw: All other options in tkinter.Label (height, state, width,
        activebackground, activeforeground, anchor,
        background, bitmap, borderwidth, cursor,
        disabledforeground, font, foreground,
        highlightbackground, highlightcolor,
        highlightthickness, image, justify,
        padx, pady, relief, takefocus, text,
        textvariable, underline, wraplength)
    '''
    def __init__(self, text, color = "black", font = "Arial 10", **kw):
        self.kw   = kw
        if type(text) == str:
            self.textvariable = tk.StringVar()
            self.textvariable.set(text)
        elif type(text) == tk.StringVar:
            self.textvariable = text
        
        tk.Label.__init__(self, _root, textvariable = self.textvariable, highlightthickness = 0, foreground = color, font = font, **kw)
        self.pack(side = _pack_side)
        
    @property
    def text(self):
        return self.textvariable.get()

    @text.setter
    def text(self, text):
        self.textvariable.set(text)

class Message(tk.Message): # ??? I forget what this does...
    def __init__(self, text = "", **kw):
        self.kw = kw
        self.textvariable = tk.StringVar()
        self.textvariable.set(self.kw['text'] if 'text' in self.kw else text)
        if 'text' in self.kw:
            del self.kw['text']
        tk.Message.__init__(self, _root, textvariable = self.textvariable, highlightthickness = 0, anchor = NW, **kw)
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

class TextBox(tk.Frame):
    hoverEffect = ("grow/darken", (4, 4, (20, 20, 20)))
    enabled = True
    validInput = True
    mouseOver = False
    
    '''
    A text box where the user can type things into.

    Args:
        width: Width of the text box
        height: Height of the text box
        text: The placeholder in the text box
        command: A function to be called when the text is changed
        commandArgs: Arguments to be passed to the command function
        executeOnType: Whether or not to execute the command function on every key press
        padding: Padding around the text box
        cornerRadius: Corner radius of the text box
        inputType: Type of input. Can be 'text', 'int', or 'decimal'
        color: Color of the text box
        textColor: Color of the text
    '''
    def __init__(self, width, height, text = "", command = None, commandArgs = None, executeOnType = True, padding = 5, cornerRadius = 10, inputType = 'text', color = (200, 200, 200), textColor = (0, 0, 0), invalidTextColor = (255, 20, 20), **kwargs):
        self.textvariable = tk.StringVar()
        self.textvariable.set(text)
        
        self.width = width
        self.height = height
        self.command = command
        self.commandArgs = commandArgs
        self.executeOnType = executeOnType
        self.inputType = inputType
        self.color = color
        self.textColor = textColor
        self.invalidTextColor = invalidTextColor
        
        tk.Frame.__init__(self, _root, width = width, height = height, highlightthickness = 0)

        self.canvas = tk.Canvas(self, width = width, height = height, highlightthickness = 0)
        self.canvas.place(rely = 0, relx = 0)
        
        # Create actual entry object
        self.entry = tk.Entry(self, width = width, textvariable = self.textvariable, highlightthickness = 0, bg = colorRGB(*self.color), fg = colorRGB(*self.textColor), relief = "flat", **kwargs)
        self.entry.place(relx = cornerRadius / width, rely = padding / height, relwidth = 1 - ((cornerRadius * 2) / width), relheight = 1 - ((padding * 2) / height))

        # Create background rounded rectangle
        self.rect = RoundedRectangle(padding, padding, width - (padding * 2), height - (padding * 2), cornerRadius, color = colorRGB(*self.color), canvas = self.canvas)
        self.rect.draw()
    
        # Bind actions
        val = self.register(self.validateChar)
        self.entry.config(validate = "key", validatecommand = (val, '%P'))
        self.entry.bind('<Return>', self.submit)
        self.bind('<Enter>', self.hoverEnter)
        self.bind('<Leave>', self.hoverExit)
    
        self.pack(side = _pack_side)
    
    def setHoverEffect(self, hoverEffect):
        '''
        Set the widget's hover effect
        
        Options:
            "grow (x, y)": The widget will grow when hovered over (default).
            "darken (r, g, b)": The widget will darken when hovered over.
            "grow/darken (x, y, (r, g, b))": The widget will grow and darken when hovered over.
            "color (r, g, b)": The widget will change color when hovered over.
            "none": The widget will not have a hover effect
        '''
        self.hoverEffect = hoverEffect
    
    def hoverEnter(self, event):
        if not self.enabled:
            return
        
        self.mouseOver = True
        
        if self.hoverEffect[0] == "grow":
            # Grow the rect
            self.rect.grow(self.hoverEffect[1][0], self.hoverEffect[1][1])
        elif self.hoverEffect[0] == "darken":
            # Darken the rect
            self.rect.color = colorRGB(self.color[0] - self.hoverEffect[1][0], self.color[1] - self.hoverEffect[1][1], self.color[2] - self.hoverEffect[1][2])
            self.entry.config(bg = self.rect.color)
        elif self.hoverEffect[0] == "grow/darken":
            # Grow and darken the rect
            self.rect.grow(self.hoverEffect[1][0], self.hoverEffect[1][1])
            self.rect.color = colorRGB(self.color[0] - self.hoverEffect[1][2][0], self.color[1] - self.hoverEffect[1][2][1], self.color[2] - self.hoverEffect[1][2][2])
            self.entry.config(bg = self.rect.color)
        elif self.hoverEffect[0] == "color":
            # Change the rect color
            self.rect.color = colorRGB(*self.hoverEffect[1])
            self.entry.config(bg = self.rect.color)
        elif self.hoverEffect[0] == "none":
            pass
        
        self.rect.draw()
        
    def hoverExit(self, event):
        if not self.enabled:
            return
        
        self.mouseOver = True
        
        if self.hoverEffect[0] == "grow":
            # Shrink the rect
            self.rect.grow(-self.hoverEffect[1][0], -self.hoverEffect[1][1])
        elif self.hoverEffect[0] == "darken":
            # Return the rect color to normal
            self.rect.color = colorRGB(*self.color)
            self.entry.config(bg = self.rect.color)
        elif self.hoverEffect[0] == "grow/darken":
            # Return the rect size and color to normal
            self.rect.grow(-self.hoverEffect[1][0], -self.hoverEffect[1][1])
            self.rect.color = colorRGB(*self.color)
            self.entry.config(bg = self.rect.color)
        elif self.hoverEffect[0] == "color":
            # Return the rect color to normal
            self.rect.color = colorRGB(*self.color)
            self.entry.config(bg = self.rect.color)
        elif self.hoverEffect[0] == "none":
            pass
        
        self.rect.draw()
    
    def disable(self):
        if self.mouseOver:
            self.hoverExit(None)
            
        self.enabled = False
        
        self.config(state = tk.DISABLED)
            
        # Lighten the text color and darken the background color
        self.itemconfig(self.text, fill = colorRGB(min(255, self.textColor[0] + 100), min(255, self.textColor[1] + 100), min(255, self.textColor[2] + 100)))
        self.rect.color = colorRGB(max(0, self.color[0] - 50), max(0, self.color[1] - 50), max(0, self.color[2] - 50))
    
    def enable(self):
        self.enabled = True
        
        self.config(state = tk.NORMAL)
        
        # Return the text color and the background color to normal
        self.rect.color = colorRGB(*self.color)
    
    # Validate each character that gets typed
    def validateChar(self, newText):
        if not self.enabled:
            return False
        
        if self.inputType == 'text':
            # Set text color to black
            self.entry.config(foreground = colorRGB(*self.textColor))
            self.validInput = True
            
            if self.executeOnType:
                self.submit(None, newText)
        elif self.inputType == 'int' and isInt(newText):
            # Set text color to black
            self.entry.config(foreground = colorRGB(*self.textColor))
            self.validInput = True
            
            if self.executeOnType:
                self.submit(None, newText)
        elif self.inputType == 'decimal' and isFloat(newText):
            # Set text color to black
            self.entry.config(foreground = colorRGB(*self.textColor))
            self.validInput = True
            
            if self.executeOnType:
                self.submit(None, newText)
        else:
            # Set text color to red
            self.entry.config(foreground = colorRGB(*self.invalidTextColor))
            self.validInput = False
        
        return True
    
    def submit(self, value, newText = None):
        if not self.enabled:
            return False
        
        # Execute callback function with its arguments and the inputted text
        if self.validInput and self.command != None:
            if self.commandArgs != None and len(self.commandArgs) != 0:
                if newText:
                    self.command(newText, *self.commandArgs)
                else:
                    self.command(self.text, *self.commandArgs)
            else:
                if newText:
                    self.command(newText)
                else:
                    self.command(self.text)

            # Unfocus this entry if this wasn't called by typing
            if not newText:
                _root.focus()
    
    def setInputCallback(self, callback, *args):
        self.command = callback
        self.commandArgs = args
    
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
        scrolledtext.ScrolledText.__init__(self, _root, bg = bg, height = height, highlightthickness = 0, **kw)
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
    '''
    A tickable CheckBox
    '''
    
    _checked = False
    
    def __init__(self, text = "", checked = False, command = None, commandArgs = None, *args, **kwargs):
        self.textvariable = tk.StringVar()
        self.textvariable.set(text)
        
        self._checked = checked
        self.tickedCommand = command
        self.commandArgs = commandArgs
        
        tk.Checkbutton.__init__(self, _root, command = self._changed, textvariable = self.textvariable, highlightthickness = 0, relief = "flat", **kwargs)
        self.pack(side = _pack_side)
        
        if checked:
            self.select()
    
    # Callback
    def _changed(self):
        self._checked = not self._checked
        
        if self.tickedCommand:
            if self.commandArgs:
                self.tickedCommand(self._checked, *self.commandArgs)
            else:
                self.tickedCommand(self._checked)
    
    def toggleCheck(self):
        '''Toggle this CheckBox'''
        self._checked = not self._checked
        self.select() if self._checked else self.deselect()
    
    def uncheck(self):
        '''Uncheck this CheckBox'''
        self._checked = False
        self.deselect()
    
    def check(self):
        '''Check this CheckBox'''
        self._checked = True
        self.select()
    
    def setChecked(self, newState: bool):
        '''Set this CheckBox's checked state'''
        self._checked = newState
        
        if newState:
            self.check()
        else:
            self.uncheck()
    
    def getChecked(self):
        return self._checked
    
    def setTickedCallback(self, callback, *args):
        self.tickedCommand = callback
        self.commandArgs = args
    
    def disable(self):
        self.config(state = DISABLED)
    
    def enable(self):
        self.config(state = NORMAL)
    
    @property
    def text(self):
        return self.textvariable.get()
    
    @text.setter
    def text(self, text):
        self.textvariable.set(text)

class RadioButton(tk.Radiobutton):
    def __init__(self, value, text = "", variable = None, checked = False, *args, **kwargs):
        global _radioVariable
        self.textvariable = tk.StringVar()
        self.textvariable.set(text)
        if variable is None:
            variable = _radioVariable
        self.variable = variable
        tk.Radiobutton.__init__(self, _root, textvariable = self.textvariable, highlightthickness = 0, variable = self.variable, value = value, relief = "flat", **kwargs)
        self.pack(side = _pack_side)
    
    def deselect(self):
        self.deselect()
    
    def select(self):
        self.select()
            
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
        tk.Spinbox.__init__(self, _root, highlightthickness = 0, relief = "flat", **kw)
        self.pack(side = _pack_side)
        
    def __call__(self, func):
        self.config(command = lambda: func(self.get()))
        return func
    
    @property
    def value(self):
        return self.get()
    
    @value.setter
    def value(self, value):
        self.value = value
        
class ScaleBar(tk.Scale):
    def __init__(self, range = None, enabled = True, **kw):
        tk.Scale.__init__(self, _root, highlightthickness = 0, relief = "flat", **kw)
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
        tk.Listbox.__init__(self, _root, highlightthickness = 0, relief = "flat", **kw)
        self.pack(side = _pack_side)
        for item in values:
            self.insert(tk.END, item)
    
    @property
    def selection(self):
        return self.curselection()[0]

class Image(tk.Canvas):
    '''
    An image. Takes an image file from path or from a PIL image (requires PIL to be installed to create from a PIL image). 
    
    Supported image file formats: PGM, PPM, GIF, and PNG
    '''
    
    def __init__(self, width, height, path = None, image = None, resizeImage = True, resizeKeepAspectRatio = True, imageWidth = None, imageHeight = None):
        '''
        Args:
            path: Path to the image
            width: Width of the image frame
            height: Height of the image frame
            imageWidth: Width of the image
            imageHeight: Height of the image
            resize: Whether or not to resize the image to the size of this widget or the image size specified in imageWidth and imageHeight
            resizeKeepAspectRatio: Whether or not to keep the aspect ratio of the image when resizing
        '''
        
        self.width = width
        self.height = height
        self.imgWidth = imageWidth or self.width
        self.imgHeight = imageHeight or self.height
        self.image = None
        
        super().__init__(_root, width = width, height = height, bd = 0, highlightthickness = 0)
        
        self.img = None
        self.imageObj = None
                
        # Set the image
        if image:            
            self.setImage(image, resizeImage, resizeKeepAspectRatio)
        elif path:
            self.setPath(path)
        
        self.pack(side = _pack_side)
    
    def setImage(self, image, resize = True, resizeKeepAspectRatio = True):
        '''
        Set the image of this Image object to a PIL image object
        
        REQUIRES PIL TO BE INSTALLED
        
        Args:
            image: The image to set
            resize: Whether or not to resize the image to the size of this widget or the size specified in the constructor
            resizeKeepAspectRatio: Whether or not to keep the aspect ratio of the image when resizing
        '''
        
        if hasPIL:
            if resize:
                img = resizeImage(image, size = (self.imgWidth, self.imgHeight), keep_aspect_ratio = resizeKeepAspectRatio)
            else:
                img = image

            self.img = ImageTK.PhotoImage(master = _root, image = img, width = self.width, height = self.height)
            
            if self.imageObj == None:
                self.imageObj = self.create_image(0, 0, image = self.img, anchor = tk.NW)
            else:
                self.itemconfig(self.imageObj, image = self.img)
        else:
            print("PIL not installed. Cannot set image from image object")
    
    def setPath(self, path):
        '''
        Set the image of this Image object to a file path
        
        Supported image formats: PGM, PPM, GIF, and PNG
        
        Args:
            path: The path to the image to set
        '''
        
        if ".jpg" in path:
            print("WARNING: JPG images are not supported. Use PNG or GIF instead")
            return
    
        self.img = tk.PhotoImage(master = _root, width = self.width, height = self.height, file = path)
        
        if self.imageObj == None:
            self.imageObj = self.create_image(0, 0, image = self.img, anchor = tk.NW)
        else:
            self.itemconfig(self.imageObj, image = self.img)
    
    def setOnClick(self, func):
        '''
        Set the function to call when this Image object is clicked
        
        Args:
            func: The function to call
        '''
        self.bind("<Button-1>", func)

    def setOnRightClick(self, func):
        '''
        Set the function to call when this Image object is right clicked
        
        Args:
            func: The function to call
        '''
        self.bind("<Button-3>", func)

class Plot(tk.Canvas):
    '''
    A 2D plot where you can draw points onto. Just like the plot function on DEGraphWin but this time it's FAST.
    
    You can drag the mouse to create a selection box.
    
    Create the plot with an array of pre-configured pixels or just plot points onto it later.
    '''
    
    enableSelectionBox = True
    selectionBox = None
    selectionMaintainAspectRatio = False
    
    clickFunc = None
    dragFunc = None
    
    def __init__(self, width, height, background = 'white'):
        self.width = width
        self.height = height
        self.background = background
        
        super().__init__(_root, width = self.width, height = self.height, bd = 0, highlightthickness = 0)
            
        self.imageP = PhotoImage(master = _root, height = self.height, width = self.width)
        
        # Set background color
        self.imageP.put(background, to = (0, 0, self.width, self.height))
        
        self.imageObj = self.create_image(0, 0, image = self.imageP, anchor = tk.NW)
        self.pack(side = _pack_side)
        
        self.bind("<B1-Motion>", self.dragClick)
        self.bind("<Button-1>", self.onClickDown)
        self.bind("<ButtonRelease-1>", self.onClickUp)
        
        self.dragBox = None
    
    def onClickDown(self, event):
        if self.clickDownFunc != None:
            self.clickDownFunc(event)
        
        self.dragStart = (event.x, event.y)
    
    def onClickUp(self, event):
        if self.clickUpFunc != None:
            self.clickUpFunc(event)
        
        if self.dragBox != None:
            self.delete(self.dragBox)
            self.dragBox = None
    
    def dragClick(self, event):
        if self.dragFunc != None:
            self.dragFunc(event)
        
        if self.enableSelectionBox:
            if self.selectionMaintainAspectRatio:
                # Keep the selection box sqaure
                if event.x - self.dragStart[0] > event.y - self.dragStart[1]:
                    self.selectionBox = (self.dragStart[0], self.dragStart[1], event.x, self.dragStart[1] + event.x - self.dragStart[0])
                else:
                    self.selectionBox = (self.dragStart[0], self.dragStart[1], self.dragStart[0] + event.y - self.dragStart[1], event.y)
            else:
                self.selectionBox = (self.dragStart[0], self.dragStart[1], event.x, event.y)
                    
            # Draw a selection rectangle
            if self.dragBox == None:
                self.dragBox = self.create_rectangle(*self.selectionBox, outline = "red", width = 2)
            else:
                # Resize the drag box
                self.coords(self.dragBox, *self.selectionBox)
            
            # Make sure the drag box is on top
            self.tag_raise(self.dragBox, self.imageObj)
    
    def plot(self, x, y, color):
        self.imageP.put("{color}".format(color = colorRGB(*color)), (x, y))
            
    def plotBulk(self, xStart, yStart, colors):
        self.imageP.put(colors, (xStart, yStart))
    
    def fill(self, color, x, y, width, height):
        '''
        Fill a rectangle with a color
        '''
        colorRows = ""
        
        for y in range(height):
            rowColors = []
            
            for x in range(width):
                rowColors.append(color)
            
            colorRows += ("{" + str(rowColors)[1:-1].replace('\'', '').replace(',', '') + "} ")
        
        self.imageP.put(rowColors, to = (x, y))
    
    def reset(self):
        self.fill(self.background, 0, 0, self.width, self.height)
    
    def clear(self):
        self.imageP.blank()
    
    def saveImage(self, path):
        self.imageP.write(path, format = 'png')
    
    # def refresh(self):
    #     self.itemconfig(self.imageObj, image = self.imageP)
    #     self.pack(side = _pack_side)
        
    #     self.update()
    
    def getWidth(self):
        '''
        Get the width of this widget
        
        Returns:
            The width of this widget
        '''
        return self.winfo_width()

    def getHeight(self):
        '''
        Get the height of this widget
        
        Returns:
            The height of this widget
        '''
        return self.winfo_height()

    def setOnClickDown(self, func):
        '''
        Set the function to call when the mouse is pressed above this widget
        
        Args:
            func: The function to call
        '''
        self.clickDownFunc = func
    
    def setOnClickUp(self, func):
        '''
        Set the function to call when the mouse is unpressed above this widget
        
        Args:
            func: The function to call
        '''
        self.clickUpFunc = func

    def setOnRightClick(self, func):
        '''
        Set the function to call when this widget is right clicked
        
        Args:
            func: The function to call
        '''
        self.bind("<Button-3>", func)

    def setOnDrag(self, func):
        '''
        Set the function to call when the user drags the mouse on this widget
        
        Args:
            func: The function to call
        '''
        self.dragFunc = func

class Graph(tk.Frame):
    """
    Tkinter native graph (pretty basic, but doesn't require heavy install).::
    
    NOTE: This must me created INSIDE of a frame, like so:
    with Stack():
        graph = tk_tools.Graph(
            xMin = -1.0,
            xMax = 1.0,
            yMin = 0.0,
            yMax = 2.0,
            xTicks = 0.2,
            yTicks = 0.2,
            width = 500,
            height = 400
        )
        
        graph.grid(row = 0, column = 0)

        lineToPlot = [(x / 10, x / 10) for x in range(10)]
        graph.plot_line(lineToPlot)
        
    :param xMin: the x minimum
    :param xMax: the x maximum
    :param yMin: the y minimum
    :param yMax: the y maximum
    :param xTicks: the 'tick' on the x-axis
    :param yTicks: the 'tick' on the y-axis
    :param args: additional valid tkinter.canvas options
    """

    def __init__(self, minX: float, maxX: float, minY: float, maxY: float, xTicks: float, yTicks: float, **args):
        self._parent = _root
        super().__init__(self._parent, **args)

        self.canvas = tk.Canvas(self, highlightthickness = 0)
        self.canvas.grid(row=0, column=0)

        self.w = float(self.canvas.config("width")[4])
        self.h = float(self.canvas.config("height")[4])
        self.minX = minX
        self.maxX = maxX
        self.xTicks = xTicks
        self.yMin = minY
        self.yMax = maxY
        self.yTicks = yTicks
        self.pixX = (self.w - 100) / ((maxX - minX) / xTicks)
        self.pixY = (self.h - 100) / ((maxY - minY) / yTicks)

        self.drawAxes()
        self.pack(side = _pack_side)

    def drawAxes(self):
        """
        Removes all existing series and re-draws the axes.
        :return: None
        """
        self.canvas.delete("all")
        rect = 50, 50, self.w - 50, self.h - 50

        self.canvas.create_rectangle(rect, outline="black")

        for x in self.frange(0, self.maxX - self.minX + 1, self.xTicks):
            value = Decimal(self.minX + x)
            if self.minX <= value <= self.maxX:
                xStep = (self.pixX * x) / self.xTicks
                coord = 50 + xStep, self.h - 50, 50 + xStep, self.h - 45
                self.canvas.create_line(coord, fill = "black")
                coord = 50 + xStep, self.h - 40

                label = round(Decimal(self.minX + x), 1)
                self.canvas.create_text(coord, fill = "black", text = label)

        for y in self.frange(0, self.yMax - self.yMin + 1, self.yTicks):
            value = Decimal(self.yMax - y)

            if self.yMin <= value <= self.yMax:
                yStep = (self.pixY * y) / self.yTicks
                coord = 45, 50 + yStep, 50, 50 + yStep
                self.canvas.create_line(coord, fill = "black")
                coord = 35, 50 + yStep

                label = round(value, 1)
                self.canvas.create_text(coord, fill = "black", text = label)

    def plotPoint(self, x, y, visible = True, color = "black", size = 5):
        """
        Places a single point on the grid
        :param x: the x coordinate
        :param y: the y coordinate
        :param visible: True if the individual point should be visible
        :param color: the color of the point
        :param size: the point size in pixels
        :return: The absolute coordinates as a tuple
        """
        xp = (self.pixX * (x - self.minX)) / self.xTicks
        yp = (self.pixY * (self.yMax - y)) / self.yTicks
        coord = 50 + xp, 50 + yp

        if visible:
            # divide down to an appropriate size
            size = int(size / 2) if int(size / 2) > 1 else 1
            x, y = coord

            self.canvas.create_oval(x - size, y - size, x + size, y + size, fill = color)

        return coord

    def plotLine(self, points: list, color = "black", pointsVisible = False):
        """
        Plot a line of points
        :param points: a list of tuples, each tuple containing an (x, y) point
        :param color: the color of the line
        :param point_visibility: True if the points should be individually visible
        :return: None
        """
        lastPt = ()
        for point in points:
            pt = self.plotPoint(point[0], point[1], color = color, visible = pointsVisible)

            if lastPt:
                self.canvas.create_line(lastPt + pt, fill=color)
            lastPt = pt

    @staticmethod
    def frange(start, stop, step, digitsToRound = 3):
        """
        Works like range for doubles
        :param start: starting value
        :param stop: ending value
        :param step: the increment_value
        :param digits_to_round: the digits to which to round (makes floating-point numbers much easier to work with)
        :return: generator
        """
        while start < stop:
            yield round(start, digitsToRound)
            start += step

class ProgressBar(tk.Canvas):
    '''
    A progress bar that shows the value in a range
    '''
    
    def __init__(self, start, end, value, width, height, suffix = "", padding = 10, cornerRadius = 20, color = (150, 150, 250), backgroundColor = (100, 100, 100), labelFont = "Arial 8 bold", labelColor = (255, 255, 255), **args):
        tk.Canvas.__init__(self, _root, width = width, height = height, borderwidth = 0, relief = "flat", highlightthickness = 0, **args)
        self.start = start
        self.end = end
        self.width = width
        self.height = height
        self.padding = padding
        self.value = value
        self.color = color
        self.backgroundColor = backgroundColor
        self.labelColor = labelColor
        self.labelFont = labelFont
        self.cornerRadius = cornerRadius
        self.suffix = suffix
        
        # Create background rect
        bgPadMult = 0.7
        self.background = RoundedRectangle(x = int(self.padding * bgPadMult), y = int(self.padding * bgPadMult), width = int(self.width - ((self.padding * bgPadMult) * 2)), height = int(self.height - ((self.padding * bgPadMult) * 2)), radius = self.cornerRadius, color = colorRGB(*self.backgroundColor), canvas = self)
        self.background.draw()
        
        # Create progress bar track
        self.track = RoundedRectangle(x = self.padding, y = self.padding, width = (self.width - self.padding * 2) * inverseLerp(self.value, self.start, self.end), height = self.height - self.padding * 2, radius = self.cornerRadius, color = colorRGB(*self.color), canvas = self)

        if self.value != 0:
            self.track.draw()
        
        # Create the text label
        self.text = self.create_text(self.width / 2, self.height / 2, text = str(round(self.value, 1)) + self.suffix)
        self.itemconfig(self.text, font = self.labelFont, fill = colorRGB(*self.labelColor))
        
        self.pack(side = _pack_side)
    
    def setValue(self, newValue):
        self.value = newValue
        
        # Resize bar
        # If the value is 0 then hide the track
        if self.value == 0:
            self.track.undraw()
        else:
            self.track.resize((self.width * inverseLerp(self.value, self.start, self.end)) - self.padding * 2, self.height - self.padding * 2)
            self.track.draw()
        
        # Set text
        self.itemconfig(self.text, text = str(round(self.value, 1)) + self.suffix)
        
        # Keep the text on top
        self.tag_raise(self.text)
    
    def getValue(self):
        return self.value

class Slider(tk.Canvas):
    '''
    A slider that can be dragged to change the value. It also has a label to show it's current value.
    
    You can change the step, min and max value, and label suffix
    '''
    
    enabled = True
    mouseOver = False
    dragging = False
    
    def __init__(self, start, end, value, width, height, step = 0, command = None, labelText = "", suffix = "", padding = [20, 10], cornerRadius = 20, color = (150, 150, 250), backgroundColor = (100, 100, 100), thumbColor = (200, 200, 255), labelFont = "Arial 8 bold", labelColor = (255, 255, 255), labelWidth = 100, **args):
        tk.Canvas.__init__(self, _root, width = width, height = height, borderwidth = 0, relief = "flat", highlightthickness = 0, **args)
        self.start = start
        self.end = end
        self.width = width
        self.height = height
        self.padding = padding
        self.value = value
        self.step = step
        self.color = color
        self.suffix = suffix
        self.backgroundColor = backgroundColor
        self.labelColor = labelColor
        self.labelFont = labelFont
        self.cornerRadius = cornerRadius
        self.thumbRadius = cornerRadius / 2
        self.thumbColor = thumbColor
        
        self.labelWidth = 0 if labelText == "" else labelWidth + 10
        actualLabelWidth = self.labelWidth - 10
                
        # Create the label
        self.label = Text(padding[0] + actualLabelWidth / 2, self.height / 2, width = self.labelWidth, height = self.height - (padding[1] * 2), justify = 'right', text = labelText, font = "Arial 12", canvas = self)
        self.label.draw()
                
        # Local pixel minimum and maximum
        self.min = self.padding[0] + self.labelWidth
        self.max = self.width - self.padding[0]
        
        # Create background rect
        bgPaddingX = self.padding[0] * 0.8
        bgPaddingY = self.padding[1] * 0.7
        self.background = RoundedRectangle(x = bgPaddingX + self.labelWidth, y = bgPaddingY, width = self.width - bgPaddingX * 2 - self.labelWidth, height = self.height - bgPaddingY * 2, radius = self.cornerRadius, color = colorRGB(*self.backgroundColor), canvas = self)
        self.background.draw()
        
        # Create slider track
        self.track = RoundedRectangle(x = self.min, y = self.padding[1], width = self.convertToPixel(self.value) - self.thumbRadius - self.labelWidth, height = self.height - self.padding[1] * 2, radius = self.cornerRadius * (2 / 3), color = colorRGB(*self.color), canvas = self)
        
        if self.value != self.start:
            self.track.draw()
        
        # Create the thumb
        self.thumb = RoundedRectangle(x = self.convertToPixel(self.value), y = (self.height / 2) - ((self.height - self.thumbRadius) / 2), width = self.thumbRadius, height = self.height - self.thumbRadius, radius = self.thumbRadius, color = self.thumbColor, canvas = self)
        self.thumb.draw()
        
        # Create the text label
        self.text = Text(self.labelWidth + self.padding[0] + ((self.width - self.padding[0] * 2 - self.labelWidth) / 2), self.height / 2, width = 50, height = self.height, font = self.labelFont, text = str(round(self.value, 1)) + self.suffix, color = 'white', canvas = self)
        self.text.draw()
        
        # Make sure the thumb and label are on top
        self._raiseElements()
        
        self.pack(side = _pack_side)
        
        self.dragFunc = None
        
        if command != None:
            self.setInputCallback(command)
        
        # Bind inputs
        self.bind("<B1-Motion>", self.dragClick)
        self.bind("<ButtonPress-1>", self.onClickDown)
        self.bind("<ButtonRelease-1>", self.onClickUp)
        self.bind('<Enter>', self.hoverEnter)
        self.bind('<Leave>', self.hoverExit)
        self.bind("<MouseWheel>", self.onMouseWheel)
    
    def onMouseWheel(self, event):
        if not self.enabled:
            return
        
        self.setValue(clamp(self.value - (event.delta / 120) * self.step, self.start, self.end))

        # Call change function
        if self.dragFunc != None:
            self.dragFunc(self.getValue())
        
    def hoverEnter(self, event):
        self.mouseOver = True
        
        if self.dragging or not self.enabled:
            return
        
        # Grow the thumb
        self.thumb.resize(self.thumbRadius + 5, self.height - self.thumbRadius + 5)
        self.thumb.move(-2.5, -2.5)
        self.thumb.draw()
        
        # Make sure the thumb and label are on top
        self._raiseElements()
        
    def hoverExit(self, event):
        self.mouseOver = False
        
        if self.dragging or not self.enabled:
            return
        
        # Return the thumb back to its normal size
        self.thumb.resize(self.thumbRadius, self.height - self.thumbRadius)
        self.thumb.move(2.5, 2.5)
        # self.thumb.setPos(self.convertToPixel(self.value) - self.thumbRadius, (self.height / 2) - ((self.height - self.thumbRadius) / 2))
        self.thumb.draw()
        
        # Make sure the thumb and label are on top
        self._raiseElements()

    def dragClick(self, event):
        if not self.enabled:
            return
        
        self.dragging = True
        
        # Darken the track
        self.track.color = colorRGB(self.color[0] - 25, self.color[1] - 25, self.color[2] - 25)
        self.track.draw()
        
        # Set the value
        self.setValue(self.convertToLocal(event.x))
        
        # Call change function
        if self.dragFunc != None:
            self.dragFunc(self.getValue())
    
    def onClickDown(self, event):
        if not self.enabled:
            return
        
        # Darken the track
        self.track.color = colorRGB(self.color[0] - 25, self.color[1] - 25, self.color[2] - 25)
        self.track.draw()
        
        # Set the value
        self.setValue(self.convertToLocal(event.x))
        
        # Call change function
        if self.dragFunc != None:
            self.dragFunc(self.getValue())
    
    def onClickUp(self, event):
        if not self.enabled:
            return
        
        self.dragging = False
        
        # Return the track back to its normal color
        self.track.color = colorRGB(*self.color)
        self.track.draw()
        
        # Make sure the thumb and label are on top
        self._raiseElements()
    
    # Set the value of the slider
    def setValue(self, newValue):
        self.value = newValue
        self.valuePix = self.convertToPixel(self.value)
        
        # Resize slider bar
        # If the value is 0 then hide the track
        if self.value == self.start:
            self.track.resize(self.valuePix - self.labelWidth - (self.thumbRadius * 2), self.height - self.padding[1] * 2)
            self.track.undraw()
        else:
            self.track.resize(self.valuePix - self.labelWidth - (self.thumbRadius * 2), self.height - self.padding[1] * 2)
            self.track.draw()
        
        # Set text
        self.text.setText(str(round(self.getValue(), 2)) + self.suffix)
        self.text.draw()
        
        # Set thumb position
        self.thumb.setPos(self.valuePix - self.thumbRadius + 2.5, (self.height / 2) - ((self.height - self.thumbRadius) / 2) - 2.5)
        self.thumb.draw()
        
        # Make sure the thumb and label are on top
        self._raiseElements()
    
    def getValue(self):
        return int(self.value) if (isInt(self.step) and self.step != 0) else self.value
    
    # Convert a pixel coordinate into this slider's range and using the step value (clamped)
    def convertToLocal(self, x):
        if self.step == 0:
            return remap(clamp(x, self.min, self.max), self.min, self.max, self.start, self.end)
        else:
            return round(remap(clamp(x, self.min, self.max), self.min, self.max, self.start, self.end), self.step - 1)
    
    # Convert a local value into pixel coordinates
    def convertToPixel(self, value):
        return remap(value, self.start, self.end, self.min, self.max)
    
    # Move the thumb and label to the top
    def _raiseElements(self):
        self.tag_raise(self.thumb.id)
        self.tag_raise(self.text.id)
    
    def setInputCallback(self, func):
        '''
        Set the function to call when the user drags the slider
        
        Args:
            func: The function to call
        '''
        self.dragFunc = func
    
    def enable(self):
        self.enabled = True
        
        # Make the slider color
        self.track.setColor(colorRGB(*self.color))
        
        # Show the thumb
        self.thumb.draw()
    
    def disable(self):
        if self.mouseOver:
            self.hoverExit(None)
            
        self.enabled = False
        
        # Make the slider gray
        self.track.setColor(colorRGB(150, 150, 150))
        
        # Hide the thumb
        self.thumb.undraw()

class SliderWithTextInput(Flow):
    '''
        A slider with a text input.
    '''
    def __init__(self, start, end, value, width, height, step = 0, command = None, entryWidth = 70, labelText = "", suffix = "", padding = [20, 10], cornerRadius = 20, color = (150, 150, 250), backgroundColor = (100, 100, 100), thumbColor = (200, 200, 255), labelFont = "Arial 8 bold", labelColor = (255, 255, 255), labelWidth = 100, **kwargs):
        super().__init__()
        
        self.command = command
        
        inputType = "int" if (isInt(step) and step != 0) else "decimal"
        
        with self:
            # Create the slider
            self.slider = Slider(start, end, value, width - entryWidth, height, step, command = self.onSliderInput, labelText = labelText, suffix = suffix, padding = padding, cornerRadius = cornerRadius, color = color, backgroundColor = backgroundColor, thumbColor = thumbColor, labelFont = labelFont, labelColor = labelColor, labelWidth = labelWidth, **kwargs)
            
            # Create the text input
            self.textInput = TextBox(entryWidth, height, str(value), command = self.onTextInput, padding = 6, inputType = inputType)

        # Set the text input value
        self.textInput.text = str(value)
    
    def getValue(self):
        return self.slider.getValue()
    
    def onTextInput(self, event):
        # Set the slider value
        self.slider.setValue(float(self.textInput.text))
        
        if self.command != None:
            self.command(self.slider.getValue())
        
    def onSliderInput(self, event):
        # Set the text input value
        self.textInput.text = str(round(self.slider.getValue(), 2))
        
        if self.command != None:
            self.command(self.slider.getValue())
            
    def setValue(self, newValue):
        self.slider.setValue(newValue)
        self.textInput.text = str(newValue)
    
    def enable(self):
        self.slider.enable()
        self.textInput.enable()
    
    def disable(self):
        self.slider.disable()
        self.textInput.disable()
    
    def setInputCallback(self, func):
        '''
        Set the function to call when the user drags the slider
        
        Args:
            func: The function to call
        '''
        self.command = func

class Popup:
    def __init__(self, widget, text, closeButtonText = "X", xOffset = 10, yOffset = 10, **kwargs):
        """
        A popup window that shows next to a given widget. It also has a button to close the window
        
        Args:
            widget: The target widget. The popup will appear next to it
            text: Popup text
            closeButtonText: The label of the close button
            xOffset(int): x - offset (pixels) of popup box from mouse pointer
            yOffset(int): y - offset (pixels) of popup box from mouse pointer
            kwargs: parameters to be passed to popup label, e.g: , background = 'red', foreground = 'blue', etc
        """
        self.widget = widget
        self._text = text
        self.xOffset = xOffset
        self.yOffset = yOffset
        self.kwargs = kwargs
        self.popupWindow = None
        self.label = None
        self.id = None
        self.closeCommand = None
        self.closeButtonText = closeButtonText

    def __del__(self):
        try:
            self.hide()
        except tk.TclError:
            pass

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, txt):
        self._text = txt
        self.setText(txt)

    def setTarget(self, target):
        self.widget = target
        self.hide()
        self.show()

    def setText(self, text):
        self._text = text
        try:
            self.label.config(text = text)
        except:
            pass

    def show(self):
        if self.popupWindow:
            return

        # tip text should be displayed away from the mouse pointer to prevent triggering leave event
        x = int(self.widget.winfo_rootx()) + self.xOffset
        y = int(self.widget.winfo_rooty()) + self.yOffset

        self.popupWindow = win = tk.Toplevel(self.widget, bg = 'white', borderwidth = 1, highlightthickness = 0, relief = tk.SOLID)

        # Hide the border on the top level window
        win.wm_overrideredirect(True)

        self.label = tk.Label(win, text = self.text, justify = LEFT, padx = 5, pady = 2, background = 'white')
        self.popupWindow.bind('<Configure>', lambda event: self.label.config(wraplength = 300))

        lbl = self.label
        self.kwargs['background'] = self.kwargs.get('background') or self.kwargs.get('bg') or 'white'
        self.kwargs['foreground'] = self.kwargs.get('foreground') or self.kwargs.get('fg') or 'black'
        configureWidget(lbl, **self.kwargs)
        
        self.closeButton = tk.Button(win, text = self.closeButtonText, width = 20, command = self.close)

        # Get text width using font, because .winfo_width() needs to call "update_idletasks()" to get correct width
        font = tkFont.Font(font = lbl['font'])
        lineCount = font.measure(self.label.cget('text')) / 300
        textWidth = font.measure(self.label.cget('text'))

        # Correct the position to keep the popup inside the screen
        if (x + (textWidth / lineCount) + 20) > lbl.winfo_screenwidth():
            x = _root.winfo_screenwidth() - (textWidth / lineCount) - 20
        
        win.wm_geometry("+%d+%d" % (x, y))
        self.label.pack(side = TOP, fill = 'both', pady = (5, 0))
        self.closeButton.pack(pady = (10, 10))
        
        win.focus()
    
    def close(self):
        if self.closeCommand != None:
            self.closeCommand()
        
        self.hide()
    
    def hide(self):
        if self.popupWindow:
            self.popupWindow.destroy()
            self.popupWindow = None

    def registerCloseCommand(self, command):
        self.closeCommand = command

def openColorChooser(initialColor = None):
    """
    Open a color chooser window
    
    Args:
        initialColor: The initial color to set the color chooser to
        
    Returns:
        The color selected by the user
    """
    if initialColor == None:
        initialColor = "#000000"
    
    return colorchooser.askcolor(initialColor)[1]

class ColorWidget(Flow):
    '''
    A widget that displays a color, its name, and allows the user to change it
    '''
    def __init__(self, name, color, colorChangeCommand, buttonLabelPrefix = "Edit ", width = 100, height = 30):
        super().__init__()
        
        self.name = name
        self.color = color
        self.colorChangeCommand = colorChangeCommand
        
        with self:
            self.editButton = Button(buttonLabelPrefix + name, width, height, color = color, textFont = "Arial 12", command = self.editColor)
    
    def editColor(self):
        returned = openColorChooser(self.color)
        if returned != None:
            self.color = colorToRGB(returned)
            self.editButton.setColor(self.color)
            
            self.colorChangeCommand(self.name, self.color)

#region Shape graphics stuff
# Abstract Base
class GraphicsObject:
    '''
    A graphics object that can be drawn on a canvas
    You can use this class to create your own graphics objects, simply inherit it and implement the draw() method
    
    Args:
        x: The x coordinate of the object
        y: The y coordinate of the object
        color: The color of the object
        outline: The outline color of the object
        shouldPanZoom(bool): Whether or not the object should be affected to zooming and panning on the canvas
        canvas(tk.Canvas): The canvas to draw the object on
    '''
    
    isDrawn = False
    shouldPanZoom = False

    def __init__(self, x, y, color, outline, shouldPanZoom = False, canvas = None):
        global _canvas
        # if type(canvas) == DEGraphWin or type(canvas) == Window:
        #     # Throw exception
        #     print("GRAPHICS OBJECT ERROR: The canvas object passed is a DEGraphWin or Window object. Please use the canvas property of the window instead")
        #     return
        
        # try:
        #     if type(canvas) != tk.Canvas:
        #         self.canvas = canvas.canvas
        #     else:
        #         self.canvas = canvas
        # except:
        #     # Throw exception
        #     print("GRAPHICS OBJECT ERROR: The canvas object passed is not a canvas and does not contain any canvas children")
        #     return
        
        if canvas == None:
            self.canvas = _canvas
        else:
            self.canvas = canvas
        
        self.x = x
        self.y = y
        self.shouldPanZoom = shouldPanZoom
        
        if type(color) == str:
            self.color = color
        else:
            self.color = colorRGB(*color)
        
        if outline == None:
            self.outline = None
        elif type(outline) == str:
            self.outline = outline
        else:
            self.outline = colorRGB(*outline)
        
        self.id = None

    def draw(self):
        self.canvas.delete(self.id)
        
        # TODO: This is duct tape because I couldn't be bothered to fix the problem fully (some canvasses that these objects can be drawn on don't implement addDrawn or removeDrawn). Actually fix this!
        if self.shouldPanZoom:
            try:
                drawX = self.x * self.canvas.zoom + self.canvas.offset[0] + self.canvas.dragOffset[0]
                drawY = self.y * self.canvas.zoom + self.canvas.offset[1] + self.canvas.dragOffset[1]
                self._draw(drawX, drawY, self.canvas.zoom)
            except:
                self._draw(self.x, self.y, 1)
        else:
            self._draw(self.x, self.y, 1)
        
        try:
            self.canvas.addDrawn(self)
        except:
            pass
        
        self.isDrawn = True
    
    def _draw(self, drawX, drawY, drawScale):
        pass

    def undraw(self):
        # TODO: This is duct tape because I couldn't be bothered to fix the problem fully (some canvasses that these objects can be drawn on don't implement addDrawn or removeDrawn). Actually fix this!
        try:
            # if self.isDrawn:
            self.canvas.removeDrawn(self.id)
            self.isDrawn = False
        except:
            pass
    
    def setPos(self, x, y):
        self.move(x - self.x, y - self.y)

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        self.canvas.move(self.id, dx, dy)
    
    def setColor(self, color):
        self.color = color
    
    def setOutline(self, outline):
        self.outline = outline

# Rectangle
class Rectangle(GraphicsObject):
    def __init__(self, x, y, width, height, color, outline, shouldPanZoom = False, canvas = None):
        super().__init__(x, y, color, outline, shouldPanZoom, canvas)
        self.width = width
        self.height = height

    def _draw(self, drawX, drawY, drawScale):
        self.id = self.canvas.create_rectangle(drawX, drawY, drawX + self.width * drawScale, drawY + self.height * drawScale, outline = self.outline, fill = self.color)

# Ellipse
class Ellipse(GraphicsObject):
    def __init__(self, x, y, width, height, color, outlineWidth = 0, outline = None, shouldPanZoom = False, canvas = None):
        super().__init__(x, y, color, outline, shouldPanZoom, canvas)
        self.width = width
        self.height = height
        self.outlineWidth = outlineWidth

    def _draw(self, drawX, drawY, drawScale):
        self.id = self.canvas.create_oval(drawX, drawY, drawX + self.width * drawScale, drawY + self.height * drawScale, width = self.outlineWidth, outline = self.outline, fill = self.color)

    def shrink(self, x, y):
        self.width += x
        self.height += y
        self.x -= x / 2
        self.y -= y / 2
    
    def resize(self, width, height):
        self.width = width
        self.height = height
    
    def setCenter(self, x, y):
        self.x = x - self.width / 2
        self.y = y - self.height / 2
        self.draw()
    
    def setSize(self, width, height):
        self.width = width
        self.height = height
        self.draw()

# Line
class Line(GraphicsObject):
    def __init__(self, x1, y1, x2, y2, color, outline = None, shouldPanZoom = False, canvas = None):
        super().__init__(x1, y1, color, outline, shouldPanZoom, canvas)
        self.x2 = x2
        self.y2 = y2

    def _draw(self, drawX, drawY, drawScale):
        self.id = self.canvas.create_line(drawX, drawY, self.x2 * drawScale + drawX, self.y2 * drawScale + drawY, fill = self.color, width = self.outline)

    def getPoints(self):
        return self.x, self.y, self.x2, self.y2

    def setPoints(self, x1, y1, x2, y2):
        self.x = x1
        self.y = y1
        self.x2 = x2
        self.y2 = y2

# Text
class Text(GraphicsObject):
    '''
    A text object that can be drawn on a canvas
    
    Justify can be: left, center, right
    '''
    def __init__(self, x, y, width, height, text, color = 'black', justify = 'center', font = "Arial 10", outline = None, shouldPanZoom = False, canvas = None):
        super().__init__(x, y, color, outline, shouldPanZoom, canvas)
        self.width = width
        self.height = height
        self.text = text
        self.justify = justify
        self.font = font

    def _draw(self, drawX, drawY, drawScale):
        self.id = self.canvas.create_text(drawX, drawY, width = self.width, text = self.text, justify = self.justify, font = self.font, outline = self.outline, fill = self.color)
        # self.id = self.canvas.create_text(self.x, self.y, width = self.width,text = self.text, justify = self.justify, font = self.font, outline = self.outline, fill = self.color)

    def getText(self):
        return self.text

    def setText(self, text):
        self.text = text

    def setJustify(self, justify):
        self.justify = justify

    def setFont(self, font):
        self.font = tkFont

# Polygon
class Polygon(GraphicsObject):
    def __init__(self, points, color, outline = None, shouldPanZoom = False, canvas = None):
        super().__init__(0, 0, color, outline, shouldPanZoom, canvas)
        self.points = points

    def _draw(self, drawX, drawY, drawScale):
        pts = []
        for i in range(0, len(self.points)):
            pts.append((self.points[i][0] * drawScale + drawX, self.points[i][1] * drawScale + drawY))
        
        self.id = self.canvas.create_polygon(pts, fill = self.color, outline = self.outline)
        

    def getPoints(self):
        return self.points

    def setPoints(self, points):
        self.points = points

# Image
class GraphicsImage(GraphicsObject):
    def __init__(self, x, y, image, shouldPanZoom = False, canvas = None):
        super().__init__(x, y, None, None, shouldPanZoom, canvas)
        self.image = image

    def _draw(self, drawX, drawY, drawScale):
        self.id = self.canvas.create_image(drawX, drawY, image = self.image)

    def getImage(self):
        return self.image

    def setImage(self, image):
        self.image = image

# Arc
class Arc(GraphicsObject):
    def __init__(self, x, y, width, height, start, extent, color, outline = None, shouldPanZoom = False, canvas = None):
        super().__init__(x, y, color, outline, shouldPanZoom, canvas)
        self.width = width
        self.height = height
        self.start = start
        self.extent = extent

    def _draw(self, drawX, drawY, drawScale):
        self.id = self.canvas.create_arc(drawX, drawY, drawX + self.width * drawScale, drawY + self.height * drawScale, start = self.start, extent = self.extent, outline = self.outline, fill = self.color)

    def getArc(self):
        return self.x, self.y, self.width, self.height, self.start, self.extent

    def setArc(self, x, y, width, height, start, extent):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.start = start
        self.extent = extent

# Rounded rectangle
class RoundedRectangle(GraphicsObject):
    def __init__(self, x, y, width, height, radius, color, outline = None, shouldPanZoom = False, canvas = None):
        super().__init__(x, y, color, outline, shouldPanZoom, canvas)
        self.width = width
        self.height = height
        self.radius = radius

    def _draw(self, drawX, drawY, drawScale):
        self.id = roundedRect(self.canvas, drawX, drawY, drawX + self.width * drawScale, drawY + self.height * drawScale, self.radius * drawScale, outline = self.outline, fill = self.color)
        # self.id = roundedRect(self.canvas, self.x, self.y, self.x + self.width, self.y + self.height, self.radius, outline = self.outline, fill = self.color)

    def grow(self, x, y):
        self.width += x
        self.height += y
        self.x -= x / 2
        self.y -= y / 2
    
    def resize(self, width, height):
        self.width = width
        self.height = height

def roundedRect(canvas, x1, y1, x2, y2, radius = 25, **kwargs):
    points = [x1 + radius, y1,
              x1 + radius, y1,
              x2 - radius, y1,
              x2 - radius, y1,
              x2, y1,
              x2, y1 + radius,
              x2, y1 + radius,
              x2, y2 - radius,
              x2, y2 - radius,
              x2, y2,
              x2 - radius, y2,
              x2 - radius, y2,
              x1 + radius, y2,
              x1 + radius, y2,
              x1, y2,
              x1, y2 - radius,
              x1, y2 - radius,
              x1, y1 + radius,
              x1, y1 + radius,
              x1, y1]

    return canvas.create_polygon(points, **kwargs, smooth = True)
#endregion

# Shadow widget adapted from: https://github.com/vednig/shadowTk
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

#region The content in this region is adapted from: https://github.com/Aboghazala/AwesomeTkinter
class Tooltip:
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

        # For dynamic tooltips, use widget.update_tooltip('new text')
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

        self.label = tk.Label(tw, text = self.text, justify = tk.LEFT, padx = 5, pady = 2, background = 'white', relief = tk.SOLID, borderwidth = 1)
        self.tooltipWindow.bind('<Configure>', lambda event: self.label.config(wraplength = 150))

        lbl = self.label
        self.kwargs['background'] = self.kwargs.get('background') or self.kwargs.get('bg') or 'white'
        self.kwargs['foreground'] = self.kwargs.get('foreground') or self.kwargs.get('fg') or 'black'
        configureWidget(lbl, **self.kwargs)

        # get text width using font, because .winfo_width() needs to call "update_idletasks()" to get correct width
        font = tkFont.Font(font = lbl['font'])
        lineCount = font.measure(self.label.cget('text')) / 150
        textWidth = font.measure(self.label.cget('text'))

        # Correct the position to keep the tooltip inside the screen
        if (x + (textWidth / lineCount) + 20) > lbl.winfo_screenwidth():
            x = self.widget.master.winfo_screenwidth() - (textWidth / lineCount) - 20
        
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
        tk.Menu.__init__(self, parent, tearoff = 0, bg = bg, fg = fg, activebackground = abg, activeforeground = afg, relief = "flat")

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

#region NOT USED!   This window blur functionality is adapted from: https://github.com/Peticali/PythonBlurBehind
# # Source material from the source linked above credited the following sources: https://github.com/Opticos/GWSL-Source/blob/master/blur.py , https://www.cnblogs.com/zhiyiYo/p/14659981.html , https://github.com/ifwe/digsby/blob/master/digsby/src/gui/vista.py
# if platform.system() == 'Windows':
#     from ctypes.wintypes import  DWORD, BOOL, HRGN, HWND
#     user32 = ctypes.windll.user32
#     dwm = ctypes.windll.dwmapi

#     class ACCENTPOLICY(ctypes.Structure):
#         _fields_ = [
#             ("AccentState", ctypes.c_uint),
#             ("AccentFlags", ctypes.c_uint),
#             ("GradientColor", ctypes.c_uint),
#             ("AnimationId", ctypes.c_uint)
#         ]

#     class WINDOWCOMPOSITIONATTRIBDATA(ctypes.Structure):
#         _fields_ = [
#             ("Attribute", ctypes.c_int),
#             ("Data", ctypes.POINTER(ctypes.c_int)),
#             ("SizeOfData", ctypes.c_size_t)
#         ]

#     class DWM_BLURBEHIND(ctypes.Structure):
#         _fields_ = [
#             ('dwFlags', DWORD), 
#             ('fEnable', BOOL),  
#             ('hRgnBlur', HRGN), 
#             ('fTransitionOnMaximized', BOOL) 
#         ]

#     class MARGINS(ctypes.Structure):
#         _fields_ = [("cxLeftWidth", ctypes.c_int),
#                     ("cxRightWidth", ctypes.c_int),
#                     ("cyTopHeight", ctypes.c_int),
#                     ("cyBottomHeight", ctypes.c_int)
#                     ]

#     SetWindowCompositionAttribute = user32.SetWindowCompositionAttribute
#     SetWindowCompositionAttribute.argtypes = (HWND, WINDOWCOMPOSITIONATTRIBDATA)
#     SetWindowCompositionAttribute.restype = ctypes.c_int

# def ExtendFrameIntoClientArea(HWND):
#     margins = MARGINS(-1, -1, -1, -1)
#     dwm.DwmExtendFrameIntoClientArea(HWND, ctypes.byref(margins))

# def Win7Blur(HWND, Acrylic):
#     if Acrylic == False:
#         DWM_BB_ENABLE = 0x01
#         bb = DWM_BLURBEHIND()
#         bb.dwFlags = DWM_BB_ENABLE
#         bb.fEnable = 1
#         bb.hRgnBlur = 1
#         dwm.DwmEnableBlurBehindWindow(HWND, ctypes.byref(bb))
#     else:
#         ExtendFrameIntoClientArea(HWND)

# def HEXtoRGBAint(HEX:str):
#     alpha = HEX[7:]
#     blue = HEX[5:7]
#     green = HEX[3:5]
#     red = HEX[1:3]

#     gradientColor = alpha + blue + green + red
#     return int(gradientColor, base=16)

# def blur(hwnd, hexColor = False, Acrylic = False, Dark = False):
#     accent = ACCENTPOLICY()
#     accent.AccentState = 3 #Default window Blur #ACCENT_ENABLE_BLURBEHIND

#     gradientColor = 0
    
#     if hexColor != False:
#         gradientColor = HEXtoRGBAint(hexColor)
#         accent.AccentFlags = 2 #Window Blur With Accent Color #ACCENT_ENABLE_TRANSPARENTGRADIENT
    
#     if Acrylic:
#         accent.AccentState = 4 #UWP but LAG #ACCENT_ENABLE_ACRYLICBLURBEHIND
#         if hexColor == False: #UWP without color is translucent
#             accent.AccentFlags = 2
#             gradientColor = HEXtoRGBAint('#12121240') #placeholder color
    
#     accent.GradientColor = gradientColor
    
#     data = WINDOWCOMPOSITIONATTRIBDATA()
#     data.Attribute = 19 #WCA_ACCENT_POLICY
#     data.SizeOfData = ctypes.sizeof(accent)
#     data.Data = ctypes.cast(ctypes.pointer(accent), ctypes.POINTER(ctypes.c_int))
    
#     SetWindowCompositionAttribute(int(hwnd), data)
    
#     if Dark: 
#         data.Attribute = 26 #WCA_USEDARKMODECOLORS
#         SetWindowCompositionAttribute(int(hwnd), data)

# def BlurLinux(WID): #may not work in all distros (working in Deepin)
#     import os

#     c = "xprop -f _KDE_NET_WM_BLUR_BEHIND_REGION 32c -set _KDE_NET_WM_BLUR_BEHIND_REGION 0 -id " + str(WID)
#     os.system(c)

# def GlobalBlur(HWND, hexColor = False, Acrylic = False, Dark = False):
    # release = platform.release()
    # system = platform.system()

    # if system == 'Windows':
    #     if release == 'Vista': 
    #         Win7Blur(HWND, Acrylic)
    #     else:
    #         release = int(float(release))
    #         if release == 10 or release == 8 or release == 11: #idk what windows 8.1 spits, if is '8.1' int(float(release)) will work...
    #             blur(HWND, hexColor, Acrylic, Dark)
    #         else:
    #             Win7Blur(HWND, Acrylic)
    
    # if system == 'Linux':
    #     BlurLinux(HWND)

    # if system == 'Darwin':
    #     print("Unfortunately window blur is not supported on MacOS")
#endregion

#region Utils
def isInt(input):
    try:
        int(input)
        return True
    except ValueError:
        return False

def isFloat(input):
    try:
        float(input)
        return True
    except ValueError:
        return False

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

    if hasPIL:
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
    else:
        print("PIL not installed. Cannot set image from path.")

def resizeImage(img, size, keep_aspect_ratio = True):
    """resize image using pillow
    Args:
        img (PIL.Image): pillow image object
        size(int or tuple(in, int)): width of image or tuple of (width, height)
        keep_aspect_ratio(bool): maintain aspect ratio relative to width
    Returns:
        (PIL.Image): pillow image
    """

    if hasPIL:
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

        img = img.resize(size, resample = PImage.Resampling.LANCZOS)

        return img
    else:
        print("PIL not installed. Cannot set image from path.")

def mixImages(background_img, foreground_img):
    """Paste an image on top of another image
    Args:
        background_img: pillow image in background
        foreground_img: pillow image in foreground
    Returns:
        pillow image
    """
    
    if hasPIL:
        background_img = background_img.convert('RGBA')
        foreground_img = foreground_img.convert('RGBA')

        img_w, img_h = foreground_img.size
        bg_w, bg_h = background_img.size
        offset = ((bg_w - img_w) // 2, (bg_h - img_h) // 2)
        background_img.paste(foreground_img, offset, mask = foreground_img)

        return background_img
    else:
        print("PIL not installed. Cannot set image from path.")

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

def colorToRGB(color):
    """Convert color names or hex notation to RGB,
    Args:
        color (str): color e.g. 'white' or '#333' or formats like #rgb or #rrggbb
    Returns:
        (3-tuple): tuple of format (r, g, b) e.g. it will return (255, 0, 0) for solid red
    """

    if color is None:
        return None

    if isinstance(color, (tuple, list)):
        if len(color)  ==  3:
            r, g, b = color
            color = r, g, b
        return color
    else:
        return ImageColor.getcolor(color, 'RGB')

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

    if hasPIL:
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
    else:
        print("PIL not installed. Cannot set image from path.")

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
    
    if hasPIL:
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
    else:
        print("PIL not installed. Cannot set image from path.")

def applyGradient(img, gradient = 'vertical', colors = None, keep_transparency = True):
    """
    A gradient color for a pillow image
    Args:
        img: pillow image
        gradient (str): vertical, horizontal, diagonal, radial
        colors (iterable): 2-colors for the gradient
        keep_transparency (bool): keep original transparency
    """
    
    if hasPIL:
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
    else:
        print("PIL not installed. Cannot set image from path.")

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

def colorRGB(r,g,b):
    '''r,g,b are intensities of r(ed), g(reen), and b(lue).
    Each value MUST be an integer in the interval [0,255]
    Returns color specifier string for the resulting color'''
    return "#%02x%02x%02x" % (r,g,b)

def remap(value, min1, max1, min2, max2) -> float:
    return min2 + (value - min1) * (max2 - min2) / (max1 - min1)

def remapClamped(value, min1, max1, min2, max2) -> float:
    return clamp(min2 + (value - min1) * (max2 - min2) / (max1 - min1), min2, max2)

def clamp(value, minimum, maximum) -> float:
    return max(minimum, min(value, maximum))

def lerpColor(color1, color2, amount):
    r = int(lerp(amount, color1[0], color2[0]))
    g = int(lerp(amount, color1[1], color2[1]))
    b = int(lerp(amount, color1[2], color2[2]))
    return (r, g, b)

def lerp(val, a, b) -> float:
    return a + (b - a) * val

def inverseLerp(val, a, b) -> float:
    return (val - a) / (b - a)

def gaussian(x, a, b, c, d = 0):
    return a * math.exp(-(x - b) ** 2 / (2 * c ** 2)) + d

# Get the color from a gradient using a number from 0 to 1
def getGradientColor(val, gradient):
    col = gradient[int(max(0, min(1, val)) * (len(gradient) - 1))]
    return (col[0] * 255, col[1] * 255, col[2] * 255)

# https://en.wikipedia.org/wiki/Fast_inverse_square_root
def fastInverseSqrt(number):
    threehalfs = 1.5
    x2 = number * 0.5
    y = number
    
    packed_y = struct.pack('f', y)
    i = struct.unpack('i', packed_y)[0]  # evil floating point bit level hacking
    i = 0x5f3759df - (i >> 1)            # what the fuck?
    packed_i = struct.pack('i', i)
    y = struct.unpack('f', packed_i)[0]  # treat int bytes as float
    
    y = y * (threehalfs - (x2 * y * y))  # newtons method
    return y
#endregion

# Example and test code
if __name__ == "__main__":
    win = DEGraphWin("This is a window", showScrollbar = True)
    # win.setFrostedGlass(True)
    
    with win:

        Label("This is a label", font = "Verdana 24 bold underline")
        
        with Flow():
            with Stack(padx = 10):
                my_label_text = "This text changes"
                my_label = Label(my_label_text)

                def change_that_text():
                    if (askYesNo(message = "Change that text?")):
                        my_label.text = "OMG it changed"
                Button("Change the above text", textFont = "Veranda 12 italic", command = change_that_text)
                Button("(Also changes that text)", command = change_that_text)
                
                with Flow():
                    
                    Label("Look, this label counts upwards:")

                    counting_label = Label("0")
                    
                    # It wasn't working in this example (it works in other examples for some reason) so I just commented it out
                    # @repeat(1)
                    # def update_label():
                    #     new_number = int(counting_label.text) + 1
                    #     counting_label.text = str(new_number)
            
            with Stack(padx = 10):
                Message("Below is a combination of a stack and two flows, forming a grid", width=140, borderwidth=1, relief=tk.SUNKEN)
                
                def yes_no_cancel():
                    response = askYesNoCancel(message = "Is this better than Kivy?")
                    if response is True:
                        showInfo(message = "You pressed yes (based)")
                    elif response is False:
                        showWarning(message = "You pressed no (not based)")
                    elif response is None:
                        showError(message = "You pressed cancel")
                        
                Button("Yes / no / cancel", command = yes_no_cancel)
            
        with Flow():
            edit = TextBox(width = 100, height = 50, text = "edit me")
            
            def read_edit_box():
                showInfo(message = "Edit box says: " + edit.text)
            
            Button("<- read edit box", command = read_edit_box)
            
            editInt = TextBox(width = 100, height = 50, inputType = 'int', text = "69")
            editFloat = TextBox(width = 100, height = 50, inputType = 'float', text = "4.20")
        
        
        with Stack(padx=2, pady=2, borderwidth=1, relief=tk.SUNKEN):
        
            Label("Browse dialogs", font = "Verdana 10 underline")
            
            with Stack(borderwidth=1, relief=tk.SUNKEN):
                file_label = Label("No file or directory picked", font = "Verdana 12 bold")
        
            with Flow():
                def pick_file():
                    with askOpenFile() as file:
                        file_label.text = file.name
                Button("Pick file", command = pick_file)
                
                def pick_dir():
                    file_label.text = askDirectory()
                Button("Pick directory", command = pick_dir)
        
        with Flow():
            integer_label = Label("No integer entered yet")
    
            def enter_integer():
                integer = askInteger("Integer", "Write an integer in the box")
                integer_label.text = str(integer)
    
            Button("Enter integer", command = enter_integer)
                
        
        with Stack(padx=2, pady=2, borderwidth=1, relief=tk.SUNKEN):
        
            Label("Scrolled text", font = "Verdana 10 underline")
        
            scrollText = ScrollableText("\n".join(["line "+str(i) for i in range(1,20)]), width=50, height=0)

            CheckBox("Scrolled text is editable?", checked = True, font = "Verdana 10 bold")
            def check(checked):
                scrollText.editable = checked
                
        with Stack(padx=2, pady=2, borderwidth=1, relief=tk.SUNKEN):
        
            Label("Radio buttons", font = "Verdana 10 underline")
            
            def show_number():
                if (set.number == 0):
                    showInfo(message = "No radio button selected")
                else:
                    showInfo(message = "The selected radio button is: " + str(set.number))
            Button("What number is it?", command = show_number)
                
            with Flow():
            
                with Stack():
                
                    with RadioButtonGroup() as set:
                        RadioButton(1, "one")
                        RadioButton(2, "two")
                        RadioButton(3, "three")
                        def val(value):
                            radio_label.text = "Radio button: " + str(value)
                        
                with Stack():
                                
                    radio_label = Label("No radio button checked")
                    
                    
                            
        with Flow():
            Label("This is a spin box:")
    
            def spin():
                spin_label.text = str(spinner.value)
    
            spinner = Spinner(values=(1, 2, 4, 8), command = spin)
    
            spin_label = Label("1")
            
        with Flow():
            Label("These are scale bars:")
    
            def scale(value):
                scale_bar_2.value = 100-int(value)
    
            ScaleBar(from_=0, to=100, command = scale)
    
            scale_bar_2 = ScaleBar(from_=0, to=100, enabled=False)
            
        with Flow():
            Label("This is an options menu:")
            def opt(option):
                print(option)
    
            OptionsMenu("one", "two", "three", command = opt)
                
        Label("This is a list box")
        list_box = ListBox(height=4, values=["one", "two", "three", "four"])
        def read_list():
            print(list_box.selection)
    
        listButton = Button("list", command = read_list)
    
        ContextMenu(listButton, ["one", "two", "three"], callback = read_list)
    
        Tooltip(listButton, "This is a tooltip")
    
        with Flow():
            Label("This", font = "Verdana 10 bold")
            AutofitLabel("is", font = "Verdana 10 bold")
            AutoWrappingLabel("a", font = "Verdana 10 bold")
            Label("thing", font = "Verdana 10 bold")
            Label("haha", font = "Verdana 10 bold")
            Label("lol", font = "Verdana 4 italic")
    
            bar = ProgressBar(start = 0, end = 100, value = 60, width = 100, height = 10, suffix = "%", color = (0, 0, 0), backgroundColor = (255, 0, 0))
            bar.setValue(25)
    
        Label("Graph:")
        with Stack():
            graph = Graph(
                minX=-1.0,
                maxX=1.0,
                minY=0.0,
                maxY=2.0,
                xTicks=0.2,
                yTicks=0.2,
                width=500,
                height=400
            )
            graph.grid(row=0, column=0)
            # create an initial line
            line_0 = [(x/10, x/10) for x in range(10)]
            graph.plotLine(line_0)
    
        # Label("Image: ")
        # Image(100, 100, "Screenshot 2022-10-20 113914.png")

        Label("Plot:")
        with Stack():
            plt = Plot(100, 100, colorRGB(10, 100, 60))
            
        for i in range(100):
            plt.plot(i, 10, colorRGB(255, 0, 0))