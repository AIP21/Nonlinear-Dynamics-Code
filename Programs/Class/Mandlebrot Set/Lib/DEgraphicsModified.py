# DEgraphics.py
'''Object-oriented graphics library that modifies the
   original graphics.py module with added functionality,
   particularly for the DE NonLinear Dynamics course,
   creating a standalone window called a DEGraphWin.

   The original library was designed to make it very easy
   for novice programmers to experiment with computer graphics
   in an object-oriented fashion, as written by John Zelle for
   use with the book "Python Programming: An Introduction to
   Computer Science" (Franklin, Beedle & Associates).

   LICENSE: This is open-source software released under the
   terms of the GPL (http://www.gnu.org/licenses/gpl.html).

   PLATFORMS: The package is a wrapper around Tkinter and customTKinter and
   should run on any platform where both Tkinter and customTKinter are available.

   Latest version modified October 2022 by Alexander IP to add:
        Transitioned from tkinter to customTKinter, this allows for a modern GUI and more graphics features. https://github.com/TomSchimansky/CustomTkinter
        Lots of small changes, like renaming a few things for clarity and cleaning up code
        
        Added labels to GraphicsObject, so any widget can have be easily labeled
        
        DEGraphFrame - (not fully working yet...) A frame to contain widgets within its own local coordinates
        
        ModernButton - A new, more modern button. Uses the customTKinter library's button
   
        lerp, invlerp, remap - Some utility functions

        hsvToRgb - Converts hsv to rgb
        
   Modified June 2020 by JS Iwanski
   to add:
        Button - gives appearance of being clicked,
        and sets up SimpleButton as a subclass of Button,
        for compatability with previous versions that had
        only a SimpleButton class.

   Modified in February/March 2020 by JS Iwanski
   to add:
        IntEntry, DblEntry, SimpleButton, DropDown, Slider,
        zooming with aspect ratio maintained on DEGraphWin,
        borders and border coloring on DEGraphWin,
        titleBar on/off on DEGraphWin,
        exact screen positioning on DEGraphWin
   Originally modified in 2018 by JS Iwanski
   to add:
        DEGraphWin (eliminated original GraphWin rather than extend it)
   See original graphics.py for other version information.
'''

import colorsys
import time
import os
import sys

try:
    import customtkinter as ctk
except:
    print("This version of DEgraphics uses the newer version of TKinter, called customTkinter, please install this package with the command: 'pip install customtkinter'")
    print("Installing customTKinter now...")
    os.system("pip install customtkinter")
    import customtkinter as ctk

try:  # import as appropriate for 2.x vs. 3.x
    import tkinter as tk
except:
    import Tkinter as tk

##################  Module Exceptions  ##################
class GraphicsError(Exception):
    '''Generic error class for graphics module exceptions'''
    pass


OBJ_ALREADY_DRAWN = "Object currently drawn"
UNSUPPORTED_METHOD = "Object doesn't support operation"
BAD_OPTION = "Illegal option value"

##################  Global variables and functions  ##################
# For zooming on DEGraphWin, in or out
ZOOM_IN = "in"
ZOOM_OUT = "out"

_root = ctk.CTk()
_root.withdraw()

_update_lasttime = time.time()

def update(rate=None):
    global _update_lasttime
    if rate:
        now = time.time()
        pauseLength = 1/rate-(now-_update_lasttime)
        if pauseLength > 0:
            time.sleep(pauseLength)
            _update_lasttime = now + pauseLength
        else:
            _update_lasttime = now

    _root.update()

def delay(timeToDelay):
    time.sleep(timeToDelay)

##################  Graphics classes  ##################
class DEGraphWin(ctk.CTk):
    '''A DEGraphWin is a toplevel window for displaying graphics. It
       stores its current custom coordinates, default coordinates,
       size in pixels (width,height), two forms of coordinate axes,
       and various display characteristics of those axes.

       This is a modern revision of DEGraphWin, using the customTKinter library.
       darkLightBehavior: Whether or not to use the system dark/light mode, or a set value. "System" (default), "Dark", "Light"
       colorTheme: The accent color to use for UI elements. "blue" (default), "green", "dark-blue"
       useHiDPI: Whether or not to use the scale percentage in the display settings of your settings app. (default is false because it might mess with things, I don't know if it fully works yet)
       '''

    def __init__(self, title="Dwight-Englewood graphics window",
                 defCoords=[-10, -10, 10, 10], margin=[0, 0],
                 axisType=0, axisColor='black',
                 width=600, height=600,
                 offsets=[0, 0], autoflush=False,
                 hasTitlebar=True,
                 hThickness=0, hBGColor="blue",
                 borderWidth=0,
                 darkLightBehavior="System",
                 colorTheme="blue",
                 useHiDPI=False):

        # Modes: "System" (standard), "Dark", "Light"
        ctk.set_appearance_mode(darkLightBehavior)
        # Themes: "blue" (standard), "green", "dark-blue"
        ctk.set_default_color_theme(colorTheme)

        # Deactivate high-dpi scaling (the scale % in the display settings of your settings app)
        if not useHiDPI:
            ctk.deactivate_automatic_dpi_awareness()

        super().__init__()

        assert type(title) == type(""), "Title must be a string"
        self.title(title)
        self.protocol("WM_DELETE_WINDOW", self.close)

        self.frame = ctk.CTkFrame(self, width=width, height=height,
                                  highlightthickness=hThickness, highlightbackground=hBGColor,
                                  bd=borderWidth)
        self.frame.pack(fill="both", expand=True)
        
        self.canvas = self.frame.canvas

        # if does not have the title bar, no controls on it, and window
        # is not resizeable nor is it movable
        if hasTitlebar == False:
            self.overrideredirect(True)  # removes title bar
            #self.wm_attributes('-type', 'splash')

        # implements the width, height, and where the window opens with respect
        # to the top-left corner of the screen, as dictated by offsets
        #   offsets[0]: how far from left edge of screen (in pixels)
        #   offsets[1]: how far from top edge of screen (in pixels)
        self.geometry('%dx%d+%d+%d' % (width, height, offsets[0], offsets[1]))
        self.canvas.pack()

        # margin = [h,v], where
        #          h : left and right margins as percentage of total width
        #          v : top and bottom margins as percentage of total height
        # (in other words, h and v should be between 0 and 0.5)

        # axisType:
        #     0 - classic x-y axes
        #     1 - 'box' axis around window

        self.axisType = axisType
        self.axesDrawn = False
        self.axisColor = axisColor
        self.margin = margin

        # zoomBox is a Rectangle that will be drawn when
        # a zoom IN is requested, and then undrawn.
        self.zoomBox = Rectangle(Point(0, 0), Point(0, 0))
        self.zoomBoxColor = 'black'

        # default coordinates that we can return to
        self.defaultCoords = defCoords

        # default background color is black
        self.foreground = "black"

        self.title = title
        self.height = int(height)
        self.width = int(width)
        self.resizable(0, 0)
        self.items = []
        self.mouseX = None
        self.mouseY = None
        self.canvas.bind("<Button-1>", self._onClick)
        self.canvas.bind_all("<Key>", self._onKey)
        self.autoflush = autoflush
        self._mouseCallback = None
        self.trans = None
        self.closed = False

        self.currentCoords = []
        # really hacky way of fixing a bug with custom coords... it works though!
        self.setCoords(defCoords[0], 0 * defCoords[1],
                       0 * defCoords[2], defCoords[3])

        # axes will store two sets of axes:
        #    0 - classic x-y axes (2)
        #    1 - box axes around edges (4)
        self.axes = []
        self.updateAxes(self.axisType, 'dotted')
        self.currentAxes = self.axes[self.axisType]

        self.lift()
        self.lastKey = ""
        if autoflush:
            _root.update()

    def __repr__(self):
        if self.isClosed():
            return "<Closed DEGraphWin>"
        else:
            return "DEGraphWin('{}', {}, {})".format(self.title(),
                                                     self.getWidth(),
                                                     self.getHeight())

    def __str__(self):
        return repr(self)

    def __checkOpen(self):
        if self.closed:
            raise GraphicsError("window is closed")

    def _onKey(self, evnt):
        self.lastKey = evnt.keysym

    def clear(self):
        '''clears drawn elements on the DEGraphWin'''
        self.canvas.delete("all")
        self.redraw()

    def setTitle(self, newTitle):
        '''change the title to newTitle'''
        self.title(newTitle)

    def setBackground(self, color):
        '''Set background color of the window'''
        self.__checkOpen()
        self.config(bg=color)
        self.__autoflush()

    def close(self):
        '''Close the window'''
        if self.closed:
            return
        self.closed = True
        self.destroy()
        self.__autoflush()

    def isClosed(self):
        return self.closed

    def isOpen(self):
        return not self.closed

    def __autoflush(self):
        if self.autoflush:
            _root.update()

    def plot(self, x, y, color="black"):
        '''Set pixel (x,y) to the given color'''
        self.__checkOpen()
        xs, ys = self.toScreen(x, y)
        self.canvas.create_line(xs, ys, xs+1, ys, fill=color)
        self.__autoflush()

    def plotPixel(self, x, y, color="black"):
        '''Set pixel raw (ind. of window coordinates) pixel (x,y) to color'''
        self.__checkOpen()
        self.canvas.create_line(x, y, x+1, y, fill=color)
        self.__autoflush()

    def flush(self):
        '''Update drawing to the window'''
        self.__checkOpen()
        self.update_idletasks()

    def getMouse(self):
        '''Wait for mouse click and return Point object from the click'''
        self.update()      # flush any prior clicks
        self.mouseX = None
        self.mouseY = None
        while self.mouseX == None or self.mouseY == None:
            self.update()
            if self.isClosed():
                raise GraphicsError("getMouse in closed window")
            time.sleep(.1)  # give up thread
        x, y = self.toWorld(self.mouseX, self.mouseY)
        self.mouseX = None
        self.mouseY = None
        return Point(x, y)

    def checkMouse(self):
        '''Return last mouse click or None if mouse has
        not been clicked since last call'''
        if self.isClosed():
            raise GraphicsError("checkMouse in closed window")
        self.update()
        if self.mouseX != None and self.mouseY != None:
            x, y = self.toWorld(self.mouseX, self.mouseY)
            self.mouseX = None
            self.mouseY = None
            return Point(x, y)
        else:
            return None

    def getKey(self):
        '''Wait for user to press a key and return it as a string'''
        self.lastKey = ""
        while self.lastKey == "":
            self.update()
            if self.isClosed():
                raise GraphicsError("getKey in closed window")
            time.sleep(.1)  # give up thread

        key = self.lastKey
        self.lastKey = ""
        return key

    def checkKey(self):
        '''Return last key pressed or None if no key pressed since last call'''
        if self.isClosed():
            raise GraphicsError("checkKey in closed window")
        self.update()
        key = self.lastKey
        self.lastKey = ""
        return key

    def getHeight(self):
        '''Return the height of the window'''
        return self.height

    def getWidth(self):
        '''Return the width of the window'''
        return self.width

    def toScreen(self, x, y):
        trans = self.trans
        if trans:
            return self.trans.screen(x, y)
        else:
            return x, y

    def toWorld(self, x, y):
        trans = self.trans
        if trans:
            return self.trans.world(x, y)
        else:
            return x, y

    def setMouseHandler(self, func):
        self._mouseCallback = func

    def _onClick(self, e):
        self.mouseX = e.x
        self.mouseY = e.y
        if self._mouseCallback:
            self._mouseCallback(Point(e.x, e.y))

    def addItem(self, item):
        self.items.append(item)

    def delItem(self, item):
        self.items.remove(item)

    def redraw(self):
        for item in self.items[:]:
            item.undraw()
            item.draw(self)
        self.update()

    def toggleAxes(self):
        '''toggles axes from shown to hidden and vice-versa'''
        if self.axesDrawn:  # already drawn, so undraw
            for i in range(len(self.currentAxes)):
                self.currentAxes[i].undraw()
        else:  # not drawn, so draw 'em
            for i in range(len(self.currentAxes)):
                self.currentAxes[i].setFill(self.axisColor)
                self.currentAxes[i].draw(self)
        self.axesDrawn = not self.axesDrawn

    def updateAxes(self, axType, axisStyle):
        '''updates coordinate axes for current scaling'''
        # 0. get rid of old axes
        # first undraw 'em (if drawn)
        if self.axesDrawn:
            for i in range(len(self.currentAxes)):
                self.currentAxes[i].undraw()
        # then empty the list
        while len(self.axes) > 0:
            waste = self.axes.pop()

        # 1. store necessary variables
        xm = self.currentCoords[0]
        xM = self.currentCoords[2]
        ym = self.currentCoords[1]
        yM = self.currentCoords[3]

        # 2. take care of classic axes
        xAxis = Line(Point(xm, 0), Point(xM, 0), axisStyle)
        yAxis = Line(Point(0, ym), Point(0, yM), axisStyle)
        axes_classic = [xAxis, yAxis]
        self.axes.append(axes_classic)

        # 3. take care of box axes
        hTop = Line(Point(xm, yM - 0.1*(yM-ym)),
                    Point(xM, yM - 0.1*(yM-ym)), axisStyle)
        hBot = Line(Point(xm, ym + 0.1*(yM-ym)),
                    Point(xM, ym + 0.1*(yM-ym)), axisStyle)
        vLef = Line(Point(xm + 0.1*(xM-xm), ym),
                    Point(xm + 0.1*(xM-xm), yM), axisStyle)
        vRgt = Line(Point(xM - 0.1*(xM-xm), ym),
                    Point(xM - 0.1*(xM-xm), yM), axisStyle)
        axes_box = [hTop, hBot, vLef, vRgt]
        self.axes.append(axes_box)

        # 4. update axis style
        self.axisType = axType
        self.currentAxes = self.axes[self.axisType]

        # 5. redraw axes if necessary
        if self.axesDrawn:
            for i in range(len(self.currentAxes)):
                self.currentAxes[i].setFill(self.axisColor)
                self.currentAxes[i].draw(self)

    def setDefaultCoords(self, newDefault):
        self.defaultCoords = newDefault

    def setCoords(self, x1, y1, x2, y2):
        # force x1 < x2 and y1 < y2
        if x1 > x2:
            temp = x1
            x1 = x2
            x2 = temp
        if y1 > y2:
            temp = y1
            y1 = y2
            y2 = temp

        width = abs(x2 - x1)
        height = abs(y2 - y1)

        self.currentCoords = [x1, y1, x2, y2]

        # calculate new x,y values incorporating margins
        newx1 = x1 - self.margin[0] * width
        newx2 = x2 + self.margin[0] * width
        newy1 = y1 - self.margin[1] * height
        newy2 = y2 + self.margin[1] * height

        # call parent setCoords
        # self.setCoords(newx1,newy1,newx2,newy2)
        self.trans = Transform(self.width, self.height,
                               newx1, newy1, newx2, newy2)
        self.redraw()

    def zoom(self, whichWay=ZOOM_IN, keepRatio=False):
        '''permits zooming IN or zooming OUT (back to default)'''
        if whichWay == ZOOM_IN:
            if not keepRatio:
                #print("Click on " + self.title + " to input one corner of the zoom box")
                pt1 = self.getMouse()
                #print("Click on " + self.title + " to input the opposite corner of the zoom box")
                pt2 = self.getMouse()

                # if the second point results in a degenerate area,
                # must re-select the second point.
                while (pt1.getX() == pt2.getX()) or (pt1.getY() == pt2.getY()):
                    #print("Click on " + self.title + " to input the opposite corner of the zoom box")
                    pt2 = self.getMouse()

                # form the zoomBox - shows the zoom area graphically to user
                self.zoomBox = Rectangle(pt1, pt2)
                self.zoomBox.setOutline(self.zoomBoxColor)
                self.zoomBox.draw(self)
                self.update()
                self.getMouse()

                # ask if they are sure they want this zoom
                #doyouwanttozoom = input("Is this the zoom you want? (type 'y' or 'n')")
                # while not(doyouwanttozoom == 'y' or doyouwanttozoom == 'n'):
                #     doyouwanttozoom = input("Please type 'y' or 'n': ")
                doyouwanttozoom = 'y'
                if doyouwanttozoom == 'y':
                    # erase the zoomBox
                    self.zoomBox.undraw()
                    # erase the window
                    self.clear()
                    x1 = min(pt1.x, pt2.x)
                    x2 = max(pt1.x, pt2.x)
                    y1 = min(pt1.y, pt2.y)
                    y2 = max(pt1.y, pt2.y)
                    self.setCoords(x1, y1, x2, y2)
                    # print("Zoomed in to [" + '{:03.4f}'.format(self.currentCoords[0])
                    #       + "," + '{:03.4f}'.format(self.currentCoords[1])
                    #       + "," + '{:03.4f}'.format(self.currentCoords[2])
                    #       + "," + '{:03.4f}'.format(self.currentCoords[3]) + "]")
                else:
                    self.zoomBox.undraw()
            else:  # we will maintain the original aspect ratio
                # will use the zoom width only, and set height accordingly
                pt1 = self.getMouse()
                temp = self.getMouse()
                while pt1.getX() == temp.getX():
                    temp = self.getMouse()
                # AR is width:height, so dx/dy = width/height
                # or dy = dx (height/width)
                x1 = min(pt1.x, temp.x)
                x2 = max(pt1.x, temp.x)
                tempy1 = pt1.y
                ratio = self.height/self.width
                if temp.y > pt1.y:  # go UP
                    tempy2 = tempy1 + (x2-x1)*ratio
                else:              # go DOWN
                    tempy2 = tempy1 - (x2-x1)*ratio
                y1 = min(tempy1, tempy2)
                y2 = max(tempy1, tempy2)
                pt1 = Point(x1, y1)
                pt2 = Point(x2, y2)
                # form the zoomBox - shows the zoom area graphically to user
                self.zoomBox = Rectangle(pt1, pt2)
                self.zoomBox.setOutline(self.zoomBoxColor)
                self.zoomBox.draw(self)
                self.update()
                self.getMouse()
                self.zoomBox.undraw()

                # ask if they are sure they want this zoom
                #doyouwanttozoom = input("Is this the zoom you want? (type 'y' or 'n')")
                # while not(doyouwanttozoom == 'y' or doyouwanttozoom == 'n'):
                #     doyouwanttozoom = input("Please type 'y' or 'n': ")
                doyouwanttozoom = 'y'
                if doyouwanttozoom == 'y':
                    # erase the zoomBox
                    self.zoomBox.undraw()
                    # erase the window
                    self.clear()
                    x1 = min(pt1.x, pt2.x)
                    x2 = max(pt1.x, pt2.x)
                    y1 = min(pt1.y, pt2.y)
                    y2 = max(pt1.y, pt2.y)
                    self.setCoords(x1, y1, x2, y2)
                    # print("Zoomed in to [" + '{:03.4f}'.format(self.currentCoords[0])
                    #       + "," + '{:03.4f}'.format(self.currentCoords[1])
                    #       + "," + '{:03.4f}'.format(self.currentCoords[2])
                    #       + "," + '{:03.4f}'.format(self.currentCoords[3]) + "]")
                else:
                    self.zoomBox.undraw()
        elif whichWay == ZOOM_OUT:
            # zooms back to defaultCoords
            # print("Zooming OUT to [" + '{:03.4f}'.format(self.defaultCoords[0])
            #           + "," + '{:03.4f}'.format(self.defaultCoords[1])
            #           + "," + '{:03.4f}'.format(self.defaultCoords[2])
            #           + "," + '{:03.4f}'.format(self.defaultCoords[3]) + "]")
            x1 = self.defaultCoords[0]
            y1 = self.defaultCoords[1]
            x2 = self.defaultCoords[2]
            y2 = self.defaultCoords[3]

            # erase the window
            self.clear()
            self.setCoords(x1, y1, x2, y2)
            self.update()

class DEGraphFrame(ctk.CTkFrame):
    '''NOT WORKING (and i dont wanna fix it)  
       A DEGraphFrame is a frame for displaying graphics. It is NOT a window, this is a Frame that is placed inside of a window. It
       stores its current custom coordinates, default coordinates,
       size in pixels (width,height), two forms of coordinate axes,
       and various display characteristics of those axes.
       '''

    def __init__(self, parentWindow: DEGraphWin, fill="both",
                 defCoords=[-10, -10, 10, 10], margin=[0, 0],
                 axisType=0, axisColor='black',
                 width=600, height=600,
                 cornerRadius="default_theme",
                 hThickness=0, hBGColor="blue",
                 autoflush=False,
                 borderWidth=0):
        super().__init__(parentWindow, width=width, height=height, corner_radius=cornerRadius,
                         highlightthickness=hThickness, highlightbackground=hBGColor,
                         bd=borderWidth)

        self.parent = parentWindow

        self.pack(fill=fill, expand=True)

        self.canvas.pack()

        # margin = [h,v], where
        #          h : left and right margins as percentage of total width
        #          v : top and bottom margins as percentage of total height
        # (in other words, h and v should be between 0 and 0.5)

        # axisType:
        #     0 - classic x-y axes
        #     1 - 'box' axis around window

        self.axisType = axisType
        self.axesDrawn = False
        self.axisColor = axisColor
        self.margin = margin

        # zoomBox is a Rectangle that will be drawn when
        # a zoom IN is requested, and then undrawn.
        self.zoomBox = Rectangle(Point(0, 0), Point(0, 0))
        self.zoomBoxColor = 'black'

        # default coordinates that we can return to
        self.defaultCoords = defCoords

        # default background color is black
        self.foreground = "black"

        self.height = int(height)
        self.width = int(width)
        self.items = []
        self.mouseX = None
        self.mouseY = None
        self.canvas.bind("<Button-1>", self._onClick)
        self.canvas.bind_all("<Key>", self._onKey)
        self.autoflush = autoflush
        self._mouseCallback = None
        self.trans = None

        self.currentCoords = []
        # really hacky way of fixing a bug with custom coords... it works though!
        self.setCoords(defCoords[0], 0 * defCoords[1],
                       0 * defCoords[2], defCoords[3])

        # axes will store two sets of axes:
        #    0 - classic x-y axes (2)
        #    1 - box axes around edges (4)
        self.axes = []
        self.updateAxes(self.axisType, 'dotted')
        self.currentAxes = self.axes[self.axisType]

        self.lift()
        self.lastKey = ""
        if autoflush:
            _root.update()

    def __repr__(self):
        if self.parent.isClosed():
            return "<Closed Parent Window>"
        else:
            return "DEGraphFrame('{}', {}, {})".format(self.parent.title() + "-Frame",
                                                       self.getWidth(),
                                                       self.getHeight())

    def __str__(self):
        return repr(self)

    def __checkOpen(self):
        if self.parent.closed:
            raise GraphicsError("Parent window is closed")

    def _onKey(self, evnt):
        self.lastKey = evnt.keysym

    def clear(self):
        '''Clears drawn elements on the frame'''
        self.canvas.delete("all")
        self.dele
        self.redraw()

    def setBackground(self, color):
        '''Set background color of the frame'''
        self.__checkOpen()
        self.config(bg=color)
        self.__autoflush()

    def isClosed(self):
        return self.parent.closed

    def isOpen(self):
        return not self.parent.closed

    def __autoflush(self):
        if self.autoflush:
            self.parent.__autoflush()

    def plot(self, x, y, color="black"):
        '''Set pixel (x,y) to the given color'''
        self.__checkOpen()
        xs, ys = self.toScreen(x, y)
        self.canvas.create_line(xs, ys, xs+1, ys, fill=color)
        self.__autoflush()

    def plotPixel(self, x, y, color="black"):
        '''Set pixel raw (ind. of window coordinates) pixel (x,y) to color'''
        self.__checkOpen()
        self.canvas.create_line(x, y, x+1, y, fill=color)
        self.__autoflush()

    def getMouse(self):
        '''Wait for mouse click and return Point object from the click'''
        self.update()      # flush any prior clicks
        self.mouseX = None
        self.mouseY = None
        while self.mouseX == None or self.mouseY == None:
            self.update()
            if self.isClosed():
                raise GraphicsError(
                    "GetMouse called in frame with closed parent window")
            time.sleep(.1)  # give up thread
        x, y = self.toWorld(self.mouseX, self.mouseY)
        self.mouseX = None
        self.mouseY = None
        return Point(x, y)

    def checkMouse(self):
        '''Return last mouse click or None if mouse has
        not been clicked since last call'''
        if self.isClosed():
            raise GraphicsError(
                "CheckMouse called in frame with closed parent window")
        self.update()
        if self.mouseX != None and self.mouseY != None:
            x, y = self.toWorld(self.mouseX, self.mouseY)
            self.mouseX = None
            self.mouseY = None
            return Point(x, y)
        else:
            return None

    def getKey(self):
        '''Wait for user to press a key and return it as a string'''
        self.lastKey = ""
        while self.lastKey == "":
            self.update()
            if self.isClosed():
                raise GraphicsError(
                    "GetKey called in frame with closed parent window")
            time.sleep(.1)  # give up thread

        key = self.lastKey
        self.lastKey = ""
        return key

    def checkKey(self):
        '''Return last key pressed or None if no key pressed since last call'''
        if self.isClosed():
            raise GraphicsError(
                "CheckKey called in frame with closed parent window")
        self.update()
        key = self.lastKey
        self.lastKey = ""
        return key

    def getHeight(self):
        '''Return the height of the frame'''
        return self.height

    def getWidth(self):
        '''Return the width of the frame'''
        return self.width

    def toScreen(self, x, y):
        trans = self.trans
        if trans:
            x2, y2 = self.parent.toScreen(x, y)
            return self.trans.screen(x2, y2)  # this might not be needed...
        else:
            return x, y

    def toWorld(self, x, y):
        trans = self.trans
        if trans:
            # this might not be needed...
            return self.trans.world(self.parent.toWorld(x, y))
        else:
            return x, y

    def setMouseHandler(self, func):
        self._mouseCallback = func

    def _onClick(self, e):
        self.mouseX = e.x
        self.mouseY = e.y
        if self._mouseCallback:
            self._mouseCallback(Point(e.x, e.y))

    def addItem(self, item):
        self.items.append(item)

    def delItem(self, item):
        self.items.remove(item)

    def redraw(self):
        for item in self.items[:]:
            item.undraw()
            item.draw(self)
        self.update()

    def toggleAxes(self):
        '''Toggles axes from shown to hidden and vice-versa'''
        if self.axesDrawn:  # already drawn, so undraw
            for i in range(len(self.currentAxes)):
                self.currentAxes[i].undraw()
        else:  # not drawn, so draw 'em
            for i in range(len(self.currentAxes)):
                self.currentAxes[i].setFill(self.axisColor)
                self.currentAxes[i].draw(self)
        self.axesDrawn = not self.axesDrawn

    def updateAxes(self, axType, axisStyle):
        '''Updates coordinate axes for current scaling'''
        # 0. get rid of old axes
        # first undraw 'em (if drawn)
        if self.axesDrawn:
            for i in range(len(self.currentAxes)):
                self.currentAxes[i].undraw()
        # then empty the list
        while len(self.axes) > 0:
            waste = self.axes.pop()

        # 1. store necessary variables
        xm = self.currentCoords[0]
        xM = self.currentCoords[2]
        ym = self.currentCoords[1]
        yM = self.currentCoords[3]

        # 2. take care of classic axes
        xAxis = Line(Point(xm, 0), Point(xM, 0), axisStyle)
        yAxis = Line(Point(0, ym), Point(0, yM), axisStyle)
        axes_classic = [xAxis, yAxis]
        self.axes.append(axes_classic)

        # 3. take care of box axes
        hTop = Line(Point(xm, yM - 0.1*(yM-ym)),
                    Point(xM, yM - 0.1*(yM-ym)), axisStyle)
        hBot = Line(Point(xm, ym + 0.1*(yM-ym)),
                    Point(xM, ym + 0.1*(yM-ym)), axisStyle)
        vLef = Line(Point(xm + 0.1*(xM-xm), ym),
                    Point(xm + 0.1*(xM-xm), yM), axisStyle)
        vRgt = Line(Point(xM - 0.1*(xM-xm), ym),
                    Point(xM - 0.1*(xM-xm), yM), axisStyle)
        axes_box = [hTop, hBot, vLef, vRgt]
        self.axes.append(axes_box)

        # 4. update axis style
        self.axisType = axType
        self.currentAxes = self.axes[self.axisType]

        # 5. redraw axes if necessary
        if self.axesDrawn:
            for i in range(len(self.currentAxes)):
                self.currentAxes[i].setFill(self.axisColor)
                self.currentAxes[i].draw(self)

    def setDefaultCoords(self, newDefault):
        self.defaultCoords = newDefault

    def setCoords(self, x1, y1, x2, y2):
        # force x1 < x2 and y1 < y2
        if x1 > x2:
            temp = x1
            x1 = x2
            x2 = temp
        if y1 > y2:
            temp = y1
            y1 = y2
            y2 = temp

        width = abs(x2 - x1)
        height = abs(y2 - y1)

        self.currentCoords = [x1, y1, x2, y2]

        # calculate new x,y values incorporating margins
        newx1 = x1 - self.margin[0] * width
        newx2 = x2 + self.margin[0] * width
        newy1 = y1 - self.margin[1] * height
        newy2 = y2 + self.margin[1] * height

        # call parent setCoords
        # self.setCoords(newx1,newy1,newx2,newy2)
        self.trans = Transform(self.width, self.height,
                               newx1, newy1, newx2, newy2)
        self.redraw()

    def zoom(self, whichWay=ZOOM_IN, keepRatio=False):
        '''Permits zooming IN or zooming OUT (back to default)'''
        if whichWay == ZOOM_IN:
            if not keepRatio:
                #print("Click on " + self.title + " to input one corner of the zoom box")
                pt1 = self.getMouse()
                #print("Click on " + self.title + " to input the opposite corner of the zoom box")
                pt2 = self.getMouse()

                # if the second point results in a degenerate area,
                # must re-select the second point.
                while (pt1.getX() == pt2.getX()) or (pt1.getY() == pt2.getY()):
                    #print("Click on " + self.title + " to input the opposite corner of the zoom box")
                    pt2 = self.getMouse()

                # form the zoomBox - shows the zoom area graphically to user
                self.zoomBox = Rectangle(pt1, pt2)
                self.zoomBox.setOutline(self.zoomBoxColor)
                self.zoomBox.draw(self)
                self.update()
                self.getMouse()

                # ask if they are sure they want this zoom
                #doyouwanttozoom = input("Is this the zoom you want? (type 'y' or 'n')")
                # while not(doyouwanttozoom == 'y' or doyouwanttozoom == 'n'):
                #     doyouwanttozoom = input("Please type 'y' or 'n': ")
                doyouwanttozoom = 'y'
                if doyouwanttozoom == 'y':
                    # erase the zoomBox
                    self.zoomBox.undraw()
                    # erase the window
                    self.clear()
                    x1 = min(pt1.x, pt2.x)
                    x2 = max(pt1.x, pt2.x)
                    y1 = min(pt1.y, pt2.y)
                    y2 = max(pt1.y, pt2.y)
                    self.setCoords(x1, y1, x2, y2)
                    # print("Zoomed in to [" + '{:03.4f}'.format(self.currentCoords[0])
                    #       + "," + '{:03.4f}'.format(self.currentCoords[1])
                    #       + "," + '{:03.4f}'.format(self.currentCoords[2])
                    #       + "," + '{:03.4f}'.format(self.currentCoords[3]) + "]")
                else:
                    self.zoomBox.undraw()
            else:  # we will maintain the original aspect ratio
                # will use the zoom width only, and set height accordingly
                pt1 = self.getMouse()
                temp = self.getMouse()
                while pt1.getX() == temp.getX():
                    temp = self.getMouse()
                # AR is width:height, so dx/dy = width/height
                # or dy = dx (height/width)
                x1 = min(pt1.x, temp.x)
                x2 = max(pt1.x, temp.x)
                tempy1 = pt1.y
                ratio = self.height/self.width
                if temp.y > pt1.y:  # go UP
                    tempy2 = tempy1 + (x2-x1)*ratio
                else:              # go DOWN
                    tempy2 = tempy1 - (x2-x1)*ratio
                y1 = min(tempy1, tempy2)
                y2 = max(tempy1, tempy2)
                pt1 = Point(x1, y1)
                pt2 = Point(x2, y2)
                # form the zoomBox - shows the zoom area graphically to user
                self.zoomBox = Rectangle(pt1, pt2)
                self.zoomBox.setOutline(self.zoomBoxColor)
                self.zoomBox.draw(self)
                self.update()
                self.getMouse()
                self.zoomBox.undraw()

                # ask if they are sure they want this zoom
                #doyouwanttozoom = input("Is this the zoom you want? (type 'y' or 'n')")
                # while not(doyouwanttozoom == 'y' or doyouwanttozoom == 'n'):
                #     doyouwanttozoom = input("Please type 'y' or 'n': ")
                doyouwanttozoom = 'y'
                if doyouwanttozoom == 'y':
                    # erase the zoomBox
                    self.zoomBox.undraw()
                    # erase the window
                    self.clear()
                    x1 = min(pt1.x, pt2.x)
                    x2 = max(pt1.x, pt2.x)
                    y1 = min(pt1.y, pt2.y)
                    y2 = max(pt1.y, pt2.y)
                    self.setCoords(x1, y1, x2, y2)
                    # print("Zoomed in to [" + '{:03.4f}'.format(self.currentCoords[0])
                    #       + "," + '{:03.4f}'.format(self.currentCoords[1])
                    #       + "," + '{:03.4f}'.format(self.currentCoords[2])
                    #       + "," + '{:03.4f}'.format(self.currentCoords[3]) + "]")
                else:
                    self.zoomBox.undraw()
        elif whichWay == ZOOM_OUT:
            # zooms back to defaultCoords
            # print("Zooming OUT to [" + '{:03.4f}'.format(self.defaultCoords[0])
            #           + "," + '{:03.4f}'.format(self.defaultCoords[1])
            #           + "," + '{:03.4f}'.format(self.defaultCoords[2])
            #           + "," + '{:03.4f}'.format(self.defaultCoords[3]) + "]")
            x1 = self.defaultCoords[0]
            y1 = self.defaultCoords[1]
            x2 = self.defaultCoords[2]
            y2 = self.defaultCoords[3]

            # erase the window
            self.clear()
            self.setCoords(x1, y1, x2, y2)
            self.update()

class Transform:
    '''Internal class for 2-D coordinate transformations'''

    def __init__(self, w, h, xlow, ylow, xhigh, yhigh):
        # w, h are width and height of window
        # (xlow,ylow) coordinates of lower-left [raw (0,h-1)]
        # (xhigh,yhigh) coordinates of upper-right [raw (w-1,0)]
        xspan = (xhigh-xlow)
        yspan = (yhigh-ylow)
        self.xbase = xlow
        self.ybase = yhigh
        self.xscale = xspan/float(w-1)
        self.yscale = yspan/float(h-1)

    def screen(self, x, y):
        # Returns x,y in screen (actually window) coordinates
        xs = (x-self.xbase) / self.xscale
        ys = (self.ybase-y) / self.yscale
        return int(xs+0.5), int(ys+0.5)

    def world(self, xs, ys):
        # Returns xs,ys in world coordinates
        x = xs*self.xscale + self.xbase
        y = self.ybase - ys*self.yscale
        return x, y

# Default values for various item configuration options. Only a subset of
# keys may be present in the configuration dictionary for a given item
DEFAULT_CONFIG = {"fill": "", "outline": "black", "width": "1", "arrow": "none",
                  "text": "", "justify": "center", "font": ("helvetica", 12, "normal")}

class GraphicsObject():
    '''Generic base class for all of the drawable objects'''
    # A subclass of GraphicsObject should override _draw and
    #   and _move methods.

    def __init__(self, options):
        # options is a list of strings indicating which options are
        # legal for this object.

        # When an object is drawn, canvas is set to the DEGraphWin(canvas)
        #    object where it is drawn and id is the TK identifier of the
        #    drawn shape.
        self.win = None
        self.id = None
        self.labelId = None
        self.master = _root
        
        # config is the dictionary of configuration options for the widget.
        config = {}
        for option in options:
            config[option] = DEFAULT_CONFIG[option]
        self.config = config
        
        # Set the appearance mode tracker callback. This allows it to react to dark/light mode changes.
        ctk.AppearanceModeTracker.add(self.set_appearance_mode, self)
        self._appearance_mode = ctk.AppearanceModeTracker.get_mode()
        
        # Configure the label
        labelConfig = {}
        labelConfig["text"] = ""
        labelConfig["font"] = ("", "", "")
        labelConfig["fill"] = ""
        self.labelOffsetX = -5
        self.labelOffsetY = 0
        self.labelConfig = labelConfig
        
    def set_appearance_mode(self, mode_string):
        if mode_string.lower() == "dark":
            self._appearance_mode = 1
        elif mode_string.lower() == "light":
            self._appearance_mode = 0

        self._draw()

    def setFill(self, color):
        '''Set interior color to "color"'''
        self._reconfig("fill", ctk.ThemeManager.single_color(ctk.ThemeManager.theme["color"]["window_bg_color"], self._appearance_mode) if color == "default_theme" else color)

    def setOutline(self, color):
        '''Set outline color to "color"'''
        self._reconfig("outline", color)

    def setWidth(self, width):
        '''Set line weight to "width"'''
        self._reconfig("width", width)
        
    def isDrawn(self):
        if self.win:
            return True
        else:
            return False

    def draw(self, win):
        '''Draw the object in graphwin, which should be a DEGraphWin object.
        A GraphicsObject may only be drawn into one window.
        Raises an error if attempt made to draw an object that is already visible.'''

        if self.win and not self.win.isClosed():
            raise GraphicsError(OBJ_ALREADY_DRAWN)
        if win.isClosed():
            raise GraphicsError("Can't draw to closed window")
        self.win = win
        self.id = self._draw(win, self.config)
        if self.labelConfig["text"] != "":
            self.labelId = self._drawLabel(win, self.labelConfig)
        else:
            self.labelId = None
        
        win.addItem(self)
        if win.autoflush:
            _root.update()
        return self

    # Label stuff
    def setLabel(self, label, offsetX = 0, offsetY = 0, color = "default_theme", font = "default_theme", size = 16, style = "normal"):
        '''Set this widget's label.
        'offsetX' and 'offsetY' indicates how much to offset the label in the x and y directions, relative to the center of this widget.
        The offsets are in PIXEL coordinates so a good starting point for figuring out offsets is like -20 for the x, -20 for the y.
        '''
        self.setLabelText(label)
        self.setLabelFont(font)
        self.setLabelSize(size)
        self.setLabelStyle(style)
        self.setLabelColor(color)
        self.setLabelOffset(offsetX, offsetY)
    
    def setLabelOffset(self, offsetX, offsetY):
        '''Set this widget's label's offset.
        'offsetX' and 'offsetY' indicates how much to offset the label in the x and y directions, relative to the center of this widget.
        The offsets are in PIXEL coordinates so a good starting point for figuring out offsets is like -20 for the x, -20 for the y.'''
        self.labelOffsetX = offsetX
        self.labelOffsetY = offsetY
        
    def setLabelText(self, text):
        self._reconfig("text", text, True)

    def getLabelText(self):
        return self.labelConfig["text"]
    
    def setLabelFont(self, font):
        if font in ['helvetica', 'arial', 'courier', 'times roman', 'verdana', 'comic sans', 'papyrus', 'default_theme']:
            ignored, s, b = self.labelConfig['font']
            self._reconfig("font", (ctk.ThemeManager.theme["text"]["font"] if font == "default_theme" else font, s, b), True)
        else:
            raise GraphicsError(BAD_OPTION)

    def setLabelSize(self, size):
        if 5 <= size <= 36:
            f, ignored, b = self.labelConfig['font']
            self._reconfig("font", (f, ctk.ThemeManager.theme["text"]["size"] if size == "default_theme" else size, b), True)
        else:
            raise GraphicsError(BAD_OPTION)

    def setLabelStyle(self, style):
        if style in ['bold', 'normal', 'italic', 'bold italic']:
            f, s, ignored = self.labelConfig['font']
            self._reconfig("font", (f, s, style), True)
        else:
            raise GraphicsError(BAD_OPTION)

    def setLabelColor(self, color):
        self._reconfig("fill", ctk.ThemeManager.single_color(ctk.ThemeManager.theme["color"]["text"], self._appearance_mode) if color == "default_theme" else color, True)
    
    def _drawLabel(self, win, config):   
        p = self.anchor
        x, y = win.toScreen(p.x + self.labelOffsetX, p.y + self.labelOffsetY)
        return win.canvas.create_text(x, y, config)

    def undraw(self):
        '''Undraw the object (i.e. hide it). Returns silently if the
        object is not currently drawn.'''

        if not self.win:
            return
        if not self.win.isClosed():
            self.win.canvas.delete(self.id)
            self.win.canvas.delete(self.labelId)
            self.win.delItem(self)
            if self.win.autoflush:
                _root.update()
        self.win = None
        self.id = None
        self.labelId = None

    def move(self, dx, dy):
        '''Move object dx units in x direction
           and dy units in y direction'''

        self._move(dx, dy)
        win = self.win
        if win and not win.isClosed():
            trans = win.trans
            if trans:
                x = dx / trans.xscale
                y = -dy / trans.yscale
            else:
                x = dx
                y = dy
            self.win.move(self.id, x, y)
            if win.autoflush:
                _root.update()

    def _reconfig(self, option, setting, label = False):
        # Internal method for changing configuration of the object
        # Raises an error if the option does not exist in the config
        #    dictionary for this object
        # Edit the label config if the label flag is set to true
        if label:
            if option not in self.labelConfig:
                raise GraphicsError(UNSUPPORTED_METHOD)
            options = self.labelConfig
            options[option] = setting
            if self.win and not self.win.isClosed():
                self.win.itemconfig(self.labelId, options)
                if self.win.autoflush:
                    _root.update()
        else:
            if option not in self.config:
                raise GraphicsError(UNSUPPORTED_METHOD)
            options = self.config
            options[option] = setting
            if self.win and not self.win.isClosed():
                self.win.itemconfig(self.id, options)
                if self.win.autoflush:
                    _root.update()

    def _draw(self, win, options):
        '''draws appropriate figure on canvas with options provided
           returns Tk id of item drawn'''
        pass  # must override in subclass

    def _move(self, dx, dy):
        '''updates internal state of object to move it dx,dy units'''
        pass  # must override in subclass

##################  Geometry classes  ##################
class Point(GraphicsObject):
    def __init__(self, x, y):
        GraphicsObject.__init__(self, ["outline", "fill"])
        self.setFill = self.setOutline
        self.x = float(x)
        self.y = float(y)

    def __repr__(self):
        return "Point({}, {})".format(self.x, self.y)

    def _draw(self, win, options):
        x, y = win.toScreen(self.x, self.y)
        return win.canvas.create_rectangle(x, y, x+1, y+1, options)

    def _move(self, dx, dy):
        self.x = self.x + dx
        self.y = self.y + dy

    def clone(self):
        other = Point(self.x, self.y)
        other.config = self.config.copy()
        return other

    def equals(self, otherPoint):
        return (self.x == otherPoint.x) and (self.y == otherPoint.y)

    def getX(self): return self.x
    def getY(self): return self.y

class _BBox(GraphicsObject):
    ''' Internal base class for objects represented by bounding box (opposite corners). Line segment is a degenerate case.'''

    def __init__(self, p1, p2, options=["outline", "width", "fill"]):
        GraphicsObject.__init__(self, options)
        self.p1 = p1.clone()
        self.p2 = p2.clone()
        self.anchor = Point((p1.getX() + p2.getX()) / 2, (p1.getY() + p2.getY()) / 2)

    def _move(self, dx, dy):
        self.p1.x = self.p1.x + dx
        self.p1.y = self.p1.y + dy
        self.p2.x = self.p2.x + dx
        self.p2.y = self.p2.y + dy

    def getP1(self): return self.p1.clone()

    def getP2(self): return self.p2.clone()

    def getCenter(self):
        p1 = self.p1
        p2 = self.p2
        return Point((p1.x+p2.x)/2.0, (p1.y+p2.y)/2.0)

class Rectangle(_BBox):
    def __init__(self, p1, p2):
        _BBox.__init__(self, p1, p2)

    def __repr__(self):
        return "Rectangle({}, {})".format(str(self.p1), str(self.p2))

    def _draw(self, win, options):
        p1 = self.p1
        p2 = self.p2
        x1, y1 = win.toScreen(p1.x, p1.y)
        x2, y2 = win.toScreen(p2.x, p2.y)
        return win.canvas.create_rectangle(x1, y1, x2, y2, options)

    def clone(self):
        other = Rectangle(self.p1, self.p2)
        other.config = self.config.copy()
        return other

class Oval(_BBox):
    def __init__(self, p1, p2):
        _BBox.__init__(self, p1, p2)

    def __repr__(self):
        return "Oval({}, {})".format(str(self.p1), str(self.p2))

    def clone(self):
        other = Oval(self.p1, self.p2)
        other.config = self.config.copy()
        return other

    def _draw(self, win, options):
        p1 = self.p1
        p2 = self.p2
        x1, y1 = win.toScreen(p1.x, p1.y)
        x2, y2 = win.toScreen(p2.x, p2.y)
        return win.canvas.create_oval(x1, y1, x2, y2, options)

class Circle(Oval):
    def __init__(self, center, radius):
        p1 = Point(center.x-radius, center.y-radius)
        p2 = Point(center.x+radius, center.y+radius)
        Oval.__init__(self, p1, p2)
        self.radius = radius

    def __repr__(self):
        return "Circle({}, {})".format(str(self.getCenter()), str(self.radius))

    def clone(self):
        other = Circle(self.getCenter(), self.radius)
        other.config = self.config.copy()
        return other

    def getRadius(self):
        return self.radius

class Line(_BBox):
    def __init__(self, p1, p2, style='solid'):
        _BBox.__init__(self, p1, p2, ["arrow", "fill", "width"])
        self.setFill(DEFAULT_CONFIG['outline'])
        self.setOutline = self.setFill
        self.style = style

    def __repr__(self):
        return "Line({}, {})".format(str(self.p1), str(self.p2))

    def clone(self):
        other = Line(self.p1, self.p2)
        other.config = self.config.copy()
        return other

    def _draw(self, win, options):
        p1 = self.p1
        p2 = self.p2
        x1, y1 = win.toScreen(p1.x, p1.y)
        x2, y2 = win.toScreen(p2.x, p2.y)
        if self.style == 'dashed':
            return win.canvas.create_line(x1, y1, x2, y2, dash=(10, 5), width=2)
        elif self.style == 'dotted':
            return win.canvas.create_line(x1, y1, x2, y2, dash=(2, 2), width=2)
        return win.canvas.create_line(x1, y1, x2, y2, options)

    def setArrow(self, option):
        if not option in ["first", "last", "both", "none"]:
            raise GraphicsError(BAD_OPTION)
        self._reconfig("arrow", option)

class Polygon(GraphicsObject):
    def __init__(self, *points):
        # if points passed as a list, extract it
        if len(points) == 1 and type(points[0]) == type([]):
            points = points[0]
        self.points = list(map(Point.clone, points))
        GraphicsObject.__init__(self, ["outline", "width", "fill"])

    def __repr__(self):
        return "Polygon"+str(tuple(p for p in self.points))

    def clone(self):
        other = Polygon(*self.points)
        other.config = self.config.copy()
        return other

    def getPoints(self):
        return list(map(Point.clone, self.points))

    def _move(self, dx, dy):
        for p in self.points:
            p.move(dx, dy)

    def _draw(self, win, options):
        args = []
        for p in self.points:
            x, y = win.toScreen(p.x, p.y)
            args.append(x)
            args.append(y)
        args.append(options)
        return win.canvas.create_polygon(*args)

##################  User interface classes  ##################
class Text(GraphicsObject):
    '''A label widget for fixed text'''

    def __init__(self, p, text):
        GraphicsObject.__init__(self, ["justify", "fill", "text", "font"])
        self.setText(text)
        self.anchor = p.clone()
        self.setFill(DEFAULT_CONFIG['outline'])
        self.setOutline = self.setFill

    def __repr__(self):
        return "Text({}, '{}')".format(self.anchor, self.getText())

    def _draw(self, win, options):
        p = self.anchor
        x, y = win.toScreen(p.x, p.y)
        return win.canvas.create_text(x, y, options)

    def _move(self, dx, dy):
        self.anchor.move(dx, dy)

    def clone(self):
        other = Text(self.anchor, self.config['text'])
        other.config = self.config.copy()
        return other

    def setText(self, text):
        self._reconfig("text", text)

    def getText(self):
        return self.config["text"]

    def getAnchor(self):
        return self.anchor.clone()

    def setFace(self, face):
        if face in ['helvetica', 'arial', 'courier', 'times roman', 'verdana', 'comic sans', 'papyrus']:
            f, s, b = self.config['font']
            self._reconfig("font", (face, s, b))
        else:
            raise GraphicsError(BAD_OPTION)

    def setSize(self, size):
        if 5 <= size <= 36:
            f, s, b = self.config['font']
            self._reconfig("font", (f, size, b))
        else:
            raise GraphicsError(BAD_OPTION)

    def setStyle(self, style):
        if style in ['bold', 'normal', 'italic', 'bold italic']:
            f, s, b = self.config['font']
            self._reconfig("font", (f, s, style))
        else:
            raise GraphicsError(BAD_OPTION)

    def setTextColor(self, color):
        self.setFill(color)

class Entry(GraphicsObject):
    '''Widget for getting text input from a user.
    NOTE: Because of the rounded corners being funky, if you changed the window color then set the backdropColor to the color of the window behind this entry.'''

    def __init__(self, center, width, placeholderText = "", backdropColor = None, textColor = "default_theme", font = "default_theme"):
        GraphicsObject.__init__(self, [])
        self.anchor = center.clone()
        self.width = width
        self.text = ctk.StringVar(_root)
        self.placeholderText = placeholderText
        self.fill = "default_theme"
        self.textColor = textColor
        self.font = font
        self.backdropColor = backdropColor
        self.entry = None

    def __repr__(self):
        return "Entry({}, {})".format(self.anchor, self.width)

    def _draw(self, win, options):
        p = self.anchor
        x, y = win.toScreen(p.x, p.y)
        frm = ctk.CTkFrame(win)
        self.entry = ctk.CTkEntry(frm,
                                  width = self.width,
                                  textvariable = self.text,
                                  fg_color = self.fill,
                                  text_color = self.textColor,
                                  text_font = self.font,
                                  bg_color = self.backdropColor,
                                  placeholder_text = self.placeholderText,
                                  justify = 'center')
        self.setText(self.placeholderText)
        self.entry.pack()
        # self.setFill(self.fill)
        self.entry.focus_set()
        return win.canvas.create_window(x, y, window=frm)

    def _move(self, dx, dy):
        self.anchor.move(dx, dy)

    def getAnchor(self):
        return self.anchor.clone()

    def clone(self):
        other = Entry(self.anchor, self.width)
        other.config = self.config.copy()
        other.text = ctk.StringVar()
        other.text.set(self.text.get())
        other.fill = self.fill
        return other

    def setText(self, t):
        self.entry.delete(0, len(self.entry.get()))
        self.entry.insert(0, t)

    def getText(self):
        return self.entry.get()

    def setFill(self, color):
        self.fill = color
        if self.entry:
            self.entry.configure(fg_color=color)

    def _setFontComponent(self, which, value):
        font = list(self.font)
        font[which] = value
        self.font = tuple(font)
        if self.entry:
            self.entry.configure(text_font=self.font)

    def setFace(self, face):
        if face in ['helvetica', 'arial', 'courier', 'times roman']:
            self._setFontComponent(0, face)
        else:
            raise GraphicsError(BAD_OPTION)

    def setSize(self, size):
        if 5 <= size <= 36:
            self._setFontComponent(1, size)
        else:
            raise GraphicsError(BAD_OPTION)

    def setStyle(self, style):
        if style in ['bold', 'normal', 'italic', 'bold italic']:
            self._setFontComponent(2, style)
        else:
            raise GraphicsError(BAD_OPTION)

    def setTextColor(self, color):
        self.textColor = color
        if self.entry:
            self.entry.configure(text_color=color)

class IntEntry(Entry):
    '''Extension of Entry to get integer input in a desired range.
    NOTE: Because of the rounded corners being funky, if you changed the window color then set the backdropColor to the color of the window behind this entry.'''

    def __init__(self, center, width, span = [0, 10],
                 defaultValue = 0,
                 limitValues = False,
                 backdropColor = None,
                 errorTextColor = 'red'):
        Entry.__init__(self, center, width, placeholderText = str(defaultValue), backdropColor = backdropColor)

        self.errorTextColor = errorTextColor
        self.min = min(int(span[0]), int(span[1]))
        self.max = max(int(span[0]), int(span[1]))
        self.limitValues = limitValues
        self.defaultValue = defaultValue
        
        if self.limitValues:
            self.defaultValue = (self.max + self.min) / 2.0
        else:
            self.defaultValue = defaultValue

    def __repr__(self):
        return "IntEntry({}, {} to {})".format(self.anchor, self.min, self.max)

    def setDefault(self, val):
        '''Updates the default value of the entry field'''
        if not self.limitValues or self.min <= val <= self.max:
            self.defaultValue = val

    def getValue(self):
        # first get the text from the entry object
        text = self.getText()
        # if the text is NOT a number, then
        # return the default value
        if not is_number(text):
            self.setTextColor(self.errorTextColor)
            self.setText(self.defaultValue)
            return self.defaultValue
        else:
            # otherwise, the text IS numeric, so
            # check first that it is in the range of
            # permitted values
            tempVal = int(float(text))
            if not self.limitValues or self.min <= tempVal <= self.max:
                self.setTextColor(ctk.ThemeManager.theme["color"]["text"])
                self.setText(tempVal)
                return tempVal
            else:
                # if it is NOT in the permitted range of values,
                # then return the default value
                self.setTextColor(self.errorTextColor)
                self.setText(self.defaultValue)
                return self.defaultValue

class DblEntry(Entry):
    '''Extension of Entry to get floating point input in a desired range.
    NOTE: Because of the rounded corners being funky, if you changed the window color then set the backdropColor to the color of the window behind this entry.'''

    def __init__(self, center, width, span=[0, 1],
                 defaultValue = 0,
                 limitValues = False,
                 backdropColor = None,
                 errorTextColor='red'):
        Entry.__init__(self, center, width, placeholderText = str(defaultValue),  backdropColor = backdropColor)

        self.errorTextColor = errorTextColor
        self.min = min(span[0], span[1])
        self.max = max(span[0], span[1])
        self.limitValues = limitValues
        self.defaultValue = defaultValue
        self.placeholderText = str(defaultValue)
        
        if self.limitValues:
            self.defaultValue = (self.max + self.min) / 2.0
        else:
            self.defaultValue = defaultValue

    def __repr__(self):
        return "DblEntry({}, {} to {})".format(self.anchor, self.min, self.max)

    def setDefault(self, val):
        '''Updates the default value of the entry field'''
        if not self.limitValues or self.min <= val <= self.max:
            self.defaultValue = val

    def getValue(self):
        # first get the text from the entry object
        text = self.getText()
        # if the text is NOT a number, then
        # return the default value
        if not is_number(text):
            self.setTextColor(self.errorTextColor)
            self.setText(self.defaultValue)
            return self.defaultValue
        else:
            # otherwise, the text IS numeric, so
            # check first that it is in the range of
            # permitted values
            tempVal = float(text)
            if not self.limitValues or self.min <= tempVal <= self.max:
                self.setTextColor(ctk.ThemeManager.theme["color"]["text"])
                self.setText(tempVal)
                return tempVal
            else:
                # if it is NOT in the permitted range of values,
                # then return the default value
                self.setTextColor(self.errorTextColor)
                self.setText(self.defaultValue)
                return self.defaultValue

class Image(GraphicsObject):
    '''GraphicsObject designed to hold an image (pixelmap)'''
    idCount = 0
    imageCache = {}  # tk photoimages go here to avoid GC while drawn

    def __init__(self, p, *pixmap):
        GraphicsObject.__init__(self, [])
        self.anchor = p.clone()
        self.imageId = Image.idCount
        Image.idCount = Image.idCount + 1
        if len(pixmap) == 1:  # file name provided
            self.img = tk.PhotoImage(file=pixmap[0], master=_root)
        else:  # width and height provided
            width, height = pixmap
            self.img = tk.PhotoImage(master=_root, width=width, height=height)

    def __repr__(self):
        return "Image({}, {}, {})".format(self.anchor, self.getWidth(), self.getHeight())

    def _draw(self, win, options):
        p = self.anchor
        x, y = win.toScreen(p.x, p.y)
        self.imageCache[self.imageId] = self.img  # save a reference
        return win.canvas.create_image(x, y, image=self.img)

    def _move(self, dx, dy):
        self.anchor.move(dx, dy)

    def undraw(self):
        try:
            del self.imageCache[self.imageId]  # allow gc of tk photoimage
        except KeyError:
            pass
        GraphicsObject.undraw(self)

    def getAnchor(self):
        return self.anchor.clone()

    def clone(self):
        other = Image(Point(0, 0), 0, 0)
        other.img = self.img.copy()
        other.anchor = self.anchor.clone()
        other.config = self.config.copy()
        return other

    def getWidth(self):
        """Returns the width of the image in pixels"""
        return self.img.width()

    def getHeight(self):
        """Returns the height of the image in pixels"""
        return self.img.height()

    def getPixel(self, x, y):
        '''Returns a list [r,g,b] with the RGB color values for pixel (x,y)
        r,g,b are in range(256)'''

        value = self.img.get(x, y)
        if type(value) == type(0):
            return [value, value, value]
        elif type(value) == type((0, 0, 0)):
            return list(value)
        else:
            return list(map(int, value.split()))

    def setPixel(self, x, y, color):
        '''Sets pixel (x,y) to the given color'''
        self.img.put("{" + color + "}", (x, y))

    def save(self, filename):
        '''Saves the pixmap image to filename.
        The format for the save image is determined
        from the filname extension.'''

        path, name = os.path.split(filename)
        ext = name.split(".")[-1]
        self.img.write(filename, format=ext)

class ModernButton(GraphicsObject):
    '''A button. Calls the provided action when clicked.
    NOTE: Because of the rounded corners being funky, if you changed the window color then set the backdropColor to the color of the window behind this button.'''

    def __init__(self, center, width, height, labelText, action, icon = None, backdropColor = None,color = "default_theme",  textFont = ("Roboto Medium", -16), hoverEffects = True):
        GraphicsObject.__init__(self, [])
        self.anchor = center.clone()
        self.width = width
        self.height = height
        self.labelText = labelText
        self.action = action
        self.icon = icon
        self.backdropColor = backdropColor
        self.color = color
        self.textFont = textFont
        self.hoverEffects = hoverEffects
        self.btn = None

    def __repr__(self):
        return "Button2({}, {})".format(self.x, self.y)

    def _draw(self, win, options):
        frm = ctk.CTkFrame(win)
        p = self.anchor
        x, y = win.toScreen(p.x, p.y)

        self.btn = ctk.CTkButton(master = frm,
                                 width = self.width,
                                 height = self.height,
                                 text = self.labelText,
                                 command = self.action,
                                 image = self.icon,
                                 fg_color = self.color,                                 
                                 bg_color = self.backdropColor,
                                 hover = self.hoverEffects,
                                 text_font = self.textFont,
                                 state = "active")
        self.btn.pack()
        self.btn.focus_set()

        return win.canvas.create_window(x, y, window=frm)

    def _move(self, dx, dy):
        self.anchor.x = self.anchor.x + dx
        self.anchor.y = self.anchor.y + dy

    def activate(self):
        '''Enables this button'''
        if self.btn:
            self.btn.configure(state="active")

    def deactivate(self):
        '''Disables this button'''
        if self.btn:
            self.btn.configure(state="disabled")

#### A button class that has appearance of being clicked ####
class Button:
    '''A button is a labeled rectangle in a window.
    It is enabled/disabled with the activate()/deactivate()
    methods. The clicked(point) method returns true if the
    button is active while being clicked. Designer can set
    various properties, including:
        > button's color, edge color, and text color
        > button's CLICKED color, edge color, and text color
        > the time delay (seconds) for the click appearance
        > the label (caption) on the button
        > the width of the button's edge
        > the font face and size of the label
        > the position of the top-left corner of the button
        > the button's width and height (in custom coordinates)
        > the window in which the button will be placed'''

    # define the button constructor
    def __init__(self, win, topLeft, width, height,
                 edgeWidth=2, label='button caption',
                 buttonColors=['lightgray', 'black', 'black'],
                 clickedColors=['white', 'red', 'black'],
                 font=('courier', 18), timeDelay=0.25, command=None):
        # buttonColors contains [button BG color, button EDGE color, textcolor]

        self.parent = win

        self.topleft = topLeft
        w, h = width/2.0, height/2.0
        x, y = topLeft.getX() + w, topLeft.getY() - h

        center = topLeft.clone()
        center.move(w, -h)

        self.xmax, self.xmin = x+w, x-w
        self.ymax, self.ymin = y+h, y-h

        # points defining opposing corners of button
        p1 = Point(self.xmin, self.ymin)
        p2 = Point(self.xmax, self.ymax)

        # define the button rectangle
        self.backcolor = buttonColors[0]
        self.backcolorClicked = clickedColors[0]
        self.rect = Rectangle(p1, p2)
        self.rect.setFill(self.backcolor)
        self.edgewidth = edgeWidth
        self.edgecolor = buttonColors[1]
        self.edgecolorClicked = clickedColors[1]
        self.rect.setOutline(self.edgecolor)
        self.rect.setWidth(self.edgewidth)

        # define the button caption
        self.forecolor = buttonColors[2]
        self.forecolorClicked = clickedColors[2]
        self.caption = Text(center, label)
        self.caption.setSize(font[1])
        self.caption.setFace(font[0])
        self.caption.setFill(self.forecolor)

        self.timeDelay = timeDelay

        # draw the button
        self.rect.draw(win)
        self.caption.draw(win)

        # button is created in deactivated state
        self.deactivate()

    def __repr__(self):
        '''basic representation of a simple button'''
        return "Button({})".format(self.topleft)

    def clicked(self, clickPoint):
        '''Returns true if button is clicked on while active,
           and false otherwise'''
        if (self.active and
                self.xmin <= clickPoint.getX() <= self.xmax and
                self.ymin <= clickPoint.getY() <= self.ymax):
            self.appearClicked(self.timeDelay)
            return True
        else:
            return False

    def getCaption(self):
        '''Returns the caption of the button'''
        return self.caption.getText()

    def setCaption(self, newCaption):
        '''Sets the button caption to newCaption'''
        self.caption.setText(newCaption)

    def changeLabelColorTo(self, newColor):
        '''modifies the saved caption color and
           changes the caption color field'''
        self.forecolor = newColor
        self.caption.setFill(newColor)

    def setLabelColor(self, newColor):
        '''changes the caption color to newColor'''
        self.caption.setFill(newColor)

    def changeButtonColorTo(self, newColor):
        '''changes the button BG color and
           changes the BG color field'''
        self.backcolor = newColor
        self.rect.setFill(newColor)

    def setButtonColor(self, newColor):
        '''Sets the background color to newColor'''
        self.rect.setFill(newColor)

    def changeEdgeColorTo(self, newColor):
        '''changes the edge color and
           changes the edge color field'''
        self.edgecolor = newColor
        self.rect.setOutline(newColor)

    def setEdgeColor(self, newColor):
        '''Sets the edge color of the button to newColor'''
        self.rect.setOutline(newColor)

    def appearClicked(self, timeDelay):
        '''gives button appearance of being clicked'''
        self.setEdgeColor(self.edgecolorClicked)
        self.setButtonColor(self.backcolorClicked)
        self.setLabelColor(self.forecolorClicked)
        self.parent.update()
        delay(timeDelay)
        self.setEdgeColor(self.edgecolor)
        self.setButtonColor(self.backcolor)
        self.setLabelColor(self.forecolor)
        self.parent.update()

    def draw(self, win):
        '''draws this simple button on window win'''
        self.rect.draw(win)
        self.caption.draw(win)

    def undraw(self):
        '''undraws (hides) this simple button'''
        self.rect.undraw()
        self.caption.undraw()

    def activate(self):
        '''enables this button'''
        self.caption.setFill(self.forecolor)
        self.rect.setWidth(self.edgewidth)
        self.active = True

    def deactivate(self):
        '''disables this button'''
        self.caption.setFill('darkgrey')
        self.rect.setWidth(1)
        self.active = False

class SimpleButton(Button):
    '''Just like a Button but with no click appearance'''

    def __init__(self, win, topLeft, width, height,
                 edgeWidth=2, label='button caption',
                 buttonColors=['lightgray', 'blue', 'black'],
                 font=('courier', 18)):
        Button.__init__(self, win, topLeft, width, height,
                        edgeWidth=edgeWidth, label=label, buttonColors=buttonColors, font=font)

    def __repr__(self):
        '''basic representation of a simple button'''
        return "SimpleButton({})".format(self.topleft)

    def clicked(self, clickPoint):
        '''Returns true if button is clicked on while active,
           and false otherwise'''
        return self.active and self.xmin <= clickPoint.getX() <= self.xmax and self.ymin <= clickPoint.getY() <= self.ymax

##################  Other tkinter widget classes  ##################
class DropDown(GraphicsObject):
    def __init__(self, topLeft, choices=[], font=('courier', 18), bg='black'):
        GraphicsObject.__init__(self, [])
        self.anchor = topLeft.clone()
        self.text = ctk.StringVar(_root)
        self.text.set("")
        self.fill = "gray"
        self.color = "black"
        self.bgColor = bg
        self.font = font
        self.choices = choices
        self.menu = None

    def __repr__(self):
        return "DropDown({}, {})".format(self.anchor, self.width)

    def _draw(self, win, options):
        frm = ctk.CTkFrame(win)
        self.text.set(self.choices[0])
        self.menu = ctk.CTkComboBox(master=frm, values=self.choices)

        # force the OptionMenu to have a width
        # commensurate with its longest element
        self.width = max([len(choice) for choice in self.choices])
        self.menu.config(width=self.width)

        p = self.anchor
        x, y = win.toScreen(p.x, p.y)

        self.menu.configure(text_font=self.font)
        self.menu.configure(bg_color=self.bgColor)
        menu = self.menu.nametowidget(self.menu.dropdown_menu)
        menu.configure(font=self.font)
        self.menu.pack()
        # self.setFill(self.fill)
        self.menu.focus_set()
        return win.canvas.create_window(x, y, window=frm)

    def _move(self, dx, dy):
        self.anchor.move(dx, dy)

    def setFill(self, color):
        self.fill = color
        if self.menu:
            self.menu.config(bg=color)

    def setTextColor(self, color):
        self.color = color
        if self.menu:
            self.menu.config(fg=color)

    def getChoice(self):
        return self.text.get()

    def setStyle(self, style):
        if style in ['bold', 'normal', 'italic', 'bold italic']:
            self._setFontComponent(2, style)
        else:
            raise GraphicsError(BAD_OPTION)

class Slider(GraphicsObject):
    def __init__(self, p, length, height,
                 min=0, max=10,
                 font=('courier', 18),
                 label="", orient="H",
                 bg='black', fg='black', trColor='gray'):
        GraphicsObject.__init__(self, [])

        self.anchor = p.clone()
        self.fill = "gray"
        self.fg = fg
        self.min = min
        self.trColor = trColor
        self.label = label
        self.font = font

        # take care of orientation: vertical or horizontal
        if orient == "V":
            self.orient = tk.VERTICAL
            self.width = length
            self.height = height
        else:
            self.orient = tk.HORIZONTAL
            self.width = height
            self.height = length
        self.max = max
        self.bgColor = bg
        self.slider = None

    def __repr__(self):
        return "Slider({}, {})".format(self.anchor, self.width)

    def _draw(self, win, options):
        p = self.anchor
        x, y = win.toScreen(p.x, p.y)
        frm = ctk.CTkFrame(win)

        self.slider = ctk.CTkSlider(frm, from_=self.min, to=self.max,
                                    width=self.width, button_length=self.height,
                                    borderwidth=1, fg_color=self.fg,
                                    progress_color=self.trColor,
                                    number_of_steps=10,
                                    orient=self.orient)

        self.slider.pack()
        # self.setFill(self.fill)
        self.slider.focus_set()
        return win.canvas.create_window(x, y, window=frm)

    def _move(self, dx, dy):
        self.anchor.move(dx, dy)

    def setFill(self, color):
        self.fill = color
        if self.slider:
            self.slider.configure(progress_color=color)

    def setTextColor(self, color):
        self.color = color
        if self.slider:
            self.slider.configure(fg_color=color)

    def getValue(self):
        return self.slider.get()

    def setStyle(self, style):
        if style in ['bold', 'normal', 'italic', 'bold italic']:
            self._setFontComponent(2, style)
        else:
            raise GraphicsError(BAD_OPTION)

##################  Text utilities  ##################
# function to determine whether a string s is numeric
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False

##################  Color utilities  ##################
def color_rgb(r, g, b):
    '''r,g,b are intensities of r(ed), g(reen), and b(lue).
    Each value MUST be an integer in the interval [0,255]
    Returns color specifier string for the resulting color'''
    return "#%02x%02x%02x" % (r, g, b)

def hsvToRgb(h, s, v):
    t = tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h, s, v))
    return color_rgb(t[0], t[1], t[2])

##################  Number utilities  ##################
def lerp(a: float, b: float, t: float) -> float:
    """Linearly interpolate on the scale given by a to b, using t as the point on that scale.
    Examples
    --------
        50 == lerp(0, 100, 0.5)
        4.2 == lerp(1, 5, 0.8)
    """
    return (1.0 - t) * a + t * b

def inverseLerp(a: float, b: float, f: float) -> float:
    """Inverse Linar Interpolation, get the fraction between a and b on which v resides.
    Examples
    --------
        0.5 == inv_lerp(0, 100, 50)
        0.8 == inv_lerp(1, 5, 4.2)
    """
    return (f - a) / (b - a)

def remap(min2: float, max1: float, min: float, max2: float, f: float) -> float:
    """Remap values from one linear scale to another, a combination of lerp and inv_lerp.
    i_min and i_max are the scale on which the original value resides,
    o_min and o_max are the scale to which it should be mapped.
    Examples
    --------
        45 == remap(0, 100, 40, 50, 50)
        6.2 == remap(1, 5, 3, 7, 4.2)
    """
    return lerp(min, max2, inverseLerp(min2, max1, f))

# MacOS fix 2
# tk.Toplevel(_root).destroy()

# MacOS fix 1
update()
