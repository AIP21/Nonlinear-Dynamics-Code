from random import random
import numpy as np
import logging

try:
    import kivy
except:
    logging.error("Kivy not installed! Logistic Explorer uses Kivy for its GUI... Trying to install it now through pip")
    
    import os
    os.system("""python -m pip install "kivy[base]" kivy_examples""")

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, Line
from kivy.uix.textinput import TextInput
from kivy.uix.slider import Slider
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.stencilview import StencilView
from kivy.uix.actionbar import ActionBar, ActionView, ActionPrevious, ActionButton
from kivy.core.window import Window
from kivy.graphics import Rectangle, RoundedRectangle
from kivy.config import Config
from kivy.clock import Clock

# Set kivy config
Config.set("graphics", "width", "1920")
Config.set("graphics", "height", "1080")
Config.set('kivy','window_icon','appIcon.png')
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

#region Widget Classes
# The bifurcation diagram widget
class BifurcationDiagram(Widget):
    #region User options
    selectedR = 2 # The selected R value
    
    targetTransientCount = 100 # The target number of transient iterations to render to
    transientCount = 100 # The current numberm of transient iterations used for drawing the bifurcation diagram
    #endregion
    
    # Trick GC into not clearing all the label/point objects being created
    labels = []
    points = []
    
    # User input variables
    panValue = 0
    zoom = 1
    startedInside = False
    dragging = False

    def __init__(self, cobwebDiag, timeseries, **kwargs):
        super(BifurcationDiagram, self).__init__(**kwargs) # Call super constructor
        
        # Assign references to the other widgets (for setting selected R value)
        self.cobwebDiag = cobwebDiag
        self.timeseries = timeseries
                
        # Redraw the widget if resized or moved
        self.bind(size = self.redrawCallback, pos = self.redrawCallback)

        # Clock.schedule_interval(self.updateCallback, 0.0333)
    
    # Callback to render this every frame
    def updateCallback(self, dt):
        if self.transientCount < self.targetTransientCount:
            self.transientCount += 1
            
            self.draw()
    
    # Resize callback, redraws this widget
    def redrawCallback(self, instance, value):
        self.draw() 
        
    #region Input
    def on_touch_down(self, touch):
        # The user clicked inside of this widget
        if self.collide_point(*touch.pos):
            self.startedInside = True
            
            if touch.is_double_tap:
                self.slidingR = True
            else:
                self.slidingR = False
            
            # Check if scrolling with scroll wheel
            if touch.is_mouse_scrolling:
                if touch.button == 'scrolldown':
                    self.zoom = min(1, self.zoom * 1.1)
                elif touch.button == 'scrollup':
                    self.zoom = max(0.1, self.zoom / 1.1)
            elif not touch.is_mouse_scrolling and not self.slidingR:
                # Not scrolling, so get panning input
                self.panStart = touch.pos[0]
                self.panValStart = self.panValue
            
            self.draw()
            
            # Propogate the touch event to this widget's children
            super().on_touch_down(touch)
        else:
            self.startedInside = False
    
    def on_touch_move(self, touch):
        if self.startedInside:
            if self.slidingR:
                self.dragging = False
                self.setSelectedR(max(0.01, min(3.99, remap(57, self.width - 10, self.rStart, self.rEnd, self.localizeX(touch.pos[0])))))
            else:
                self.dragging = True
            
            if self.dragging:
                self.panValue = self.panValStart + (touch.pos[0] - self.panStart)
                
                # Snap to previous pan value
                if abs(self.panValStart - self.panValue) < 5:
                    self.panValue = self.panValStart
                    
                # Snap to original pan value
                if abs(self.panValue) < 5:
                    self.panValue = 0
            
            # Redraw
            self.draw()
            
            # Propogate the touch event to this widget's children
            super().on_touch_move(touch)
    
    def on_touch_up(self, touch):
        if self.startedInside:
            if self.dragging or self.slidingR: # If dragging or sliding R then set that state to false
                self.dragging = False
                self.slidingR = False
            elif not touch.is_mouse_scrolling: # If not scrolling or dragging then select an R value
                self.setSelectedR(max(0.01, min(3.99, remap(57, self.width - 10, self.rStart, self.rEnd, self.localizeX(touch.pos[0])))))
            
            self.draw()
                
            self.startedInside = False
            
            # Propogate the touch event to this widget's children
            super().on_touch_up(touch)
    #endregion
    
    # Set the selected R value and update other widgets on this change
    def setSelectedR(self, val):
        # Snap the selected R value to an interval of 0.5
        for i in range(0, 8): # I would've used modulo but couldn't be bothered with fiddling with constants for half an hour
            if i != 0:
                interval = i / 2.0
                if abs(interval - val) < 0.025:
                    val = interval
        
        # Prevent the selected R value from crashing the program
        if val != 4 and val != 0:
            # logging.info("Selected R: {}".format(val))
            self.selectedR = val
            self.cobwebDiag.selectedR = val
            self.timeseries.selectedR = val
            self.draw()
            self.cobwebDiag.draw()
            self.timeseries.draw()
    
    # Localize an x value to this widget's local coordinates
    def localizeX(self, x):
        return self.x + x
        
    # Localize an y value to this widget's local coordinates
    def localizeY(self, y):
        return self.y + y
    
    # Draw the widget
    def draw(self):
        # Draw onto the canvas
        with self.canvas:
            self.canvas.clear() # Clear the canvas for new drawing
            
            self.labels.clear() # Clear the labels list
            self.points.clear() # Clear the points list
            
            # Cache some frequently used values (yes, I am optimizing this because it involves dividing... oPtImIzAtIoN)
            self.halfWidth = self.width / 2
            self.halfHeight = self.height / 2
            self.padding = [55, 55, 10, 28] # Padding for axes, labels, and the title
            w = (self.width - (self.padding[0] + self.padding[2])) / 2 # Half of the width of the padded space
                        
            # Duct tape for a bug I didn't want to deal with
            if self.zoom == 1:
                self.panValue = 0
            
            # Clamp the pan value so it doesn't go out of bounds (and crash the program)
            self.panValue = min((w / self.zoom) - w, max(w - (w / self.zoom), self.panValue))
            
            # View area info
            viewCenter = w - (self.panValue * self.zoom) # Center of the viewing area
            viewSize = w * self.zoom # Half of the width of the viewing area
            
            # Get the R start and end values using widget's width and the user pan and zoom
            self.rStart = remap(0, w * 2, 0, 4, viewCenter - viewSize)
            self.rEnd = remap(0, w * 2, 0, 4, viewCenter + viewSize)
            
            # print("rStart = {}, rEnd = {}, panValue = {}, zoom = {}, w = {}, minPan = {}, maxPan = {}".format(self.rStart, self.rEnd, self.panValue, self.zoom, w, (w / self.zoom) - w, w - (w / self.zoom)))

            # Background color
            Color(0.5, 0.5, 0.5)
            RoundedRectangle(pos = self.pos, size = self.size)
            
            #region Draw view box (used for debugging, that's why it is commented out)
            # xSides = [viewCenter - viewSize, viewCenter + viewSize]
            
            # sideL = pad[0] + xSides[0]
            # sideR = pad[0] + xSides[1]
            # top = self.height - pad[3]
            # bottom = pad[1]
            # sideMHoriz = pad[0] + viewCenter
            # sideMVert = pad[1] + (h / 2)
            
            # lineL = [(sideL, bottom), (sideL, top)]
            # lineR = [(sideR, bottom), (sideR, top)]
            # lineTop = [(sideL, top), (sideR, top)]
            # lineBottom = [(sideL, bottom), (sideR, bottom)]
            # lineCenterVert = [(sideMHoriz, bottom), (sideMHoriz, top)]
            # lineCenterHoriz = [(sideL, sideMVert), (sideR, sideMVert)]
            
            # Color(1, 0, 0)
            # self.labels.append(Line(points = lineL))
            # Color(0, 1, 0)
            # self.labels.append(Line(points = lineR))
            # Color(0, 0, 1)
            # self.labels.append(Line(points = lineBottom))
            # Color(1, 1, 1)
            # self.labels.append(Line(points = lineTop))
            # Color(0.5, 0.5, 1)
            # self.labels.append(Line(points = lineCenterVert))
            # Color(1, 0.5, 0.5)
            # self.labels.append(Line(points = lineCenterHoriz))
            #endregion
            
            # Draw the axes
            self.drawAxes()

            # Draw the bifurcation diagram
            self.drawBifurcationDiagram()
            
            # Title and it's container
            Color(0.78, 0.78, 0.78)
            RoundedRectangle(pos = (self.x , self.y + self.height - 24), size = (160, 24))
            Rectangle(pos = (self.x, self.y + self.height - 24), size = (10, 12))
            Rectangle(pos = (self.x + 150, self.y + self.height - 12), size = (10, 12))
            Color(0.1, 0.1, 0.1)
            self.labels.append(Label(center = (self.x + 80, self.y + self.height - 12), color = (0.15, 0.15, 0.15), text = "Bifurcation Diagram"))
        
    # Draw the axes
    def drawAxes(self):
        # Axis lines
        Color(1, 1, 1)
        Line(points = ((self.localizeX(50), self.localizeY(50)), (self.localizeX(self.width - 10), self.localizeY(50))), width = 1.25)
        Line(points = ((self.localizeX(50), self.localizeY(50)), (self.localizeX(50), self.localizeY(self.height - 30))), width = 1.25)
        
        # Draw axis labels
        self.labels.append(Label(center = ((self.width / 2) + 30, 22.5), text = "R"))
        self.labels.append(Label(center = (18, (self.height / 2) + 12.5), text = "X[sub]t[/sub]", markup = True))
        
        # Draw axis values
        # X-axis (R)
        # rEnd is doubled to get double the precision (labeling [0, 0.5, 1.0, 1.5] instead of just [0, 1])
        # rEnd also has one added to it because range's end is exclusive
        for x in np.arange(self.rStart, self.rEnd * 2 + 1):
            xVal = float(x) / 2 # Return the doubled value back to normal
            label = Label(center = (remap(self.rStart, self.rEnd, 55, self.width - 10, xVal), 45), text = str(round(xVal, 2)), font_size = 13)
            self.labels.append(label)
        
        # Y-axis (xt)
        # The end range is quadrupled to get four times the precision (labeling [0, 0.25, 0.5, 0.75, 1.0] instead of just [0, 1])
        # The end range also has one added to it because range's end is exclusive
        for y in range(0, 5):
            yVal = y / 4 # Return the quadrupled value back to normal
            label = Label(center = (38, remap(0, 1, 60, self.height - 33, yVal)), text = str(round(yVal, 2)), font_size = 13)
            self.labels.append(label)
    
    # Draw the bifurcation diagram
    def drawBifurcationDiagram(self):
        # Define some constants used by the bifurcation algorithm
        currentR = self.rStart
        stepFudge = 1 # Changes the resolution of the diagram. Increasing the fudge above 1 lowers the resulting resolution but makes it faster, below 0 has the opposite effect
        rStep = ((self.rEnd - self.rStart) / (self.width - (self.padding[0] + self.padding[2]))) * stepFudge
        
        Color(0.98, 0.49, 0.09)
        while currentR <= self.rEnd: # Keep looping until R is >= rEnd
            y = random() # Get a random starting point between 0 and 1
            
            for i in range(self.transientCount): # Iterate the transient values
                y = currentR * y * (1 - y)
            
            self.points.append(Rectangle(pos = (round(remap(self.rStart, self.rEnd, 56, self.width - 20, currentR)), round(remap(0, 1, 60, self.height - 40, y))), size = (2, 2)))
                        
            currentR += rStep # Step the R value a small bit
        
        # Draw selected R value line
        Color(0.21, 0.54, 0.27)
        Line(points = [(remap(self.rStart, self.rEnd, 55, self.width - 20, self.selectedR), 60), (remap(self.rStart, self.rEnd, 55, self.width - 20, self.selectedR), self.height - 40)], width = 1.175)
    
# The 2D plot part of the Cobweb Diagram. Inherits from StencilView in order to more easily keep the drawn lines inside of the widget's bounds
class Plot2D(StencilView):
    # The selected R value
    selectedR = 2
    
    # Trick GC into not clearing all the label/line objects being created
    labels = []
    lines = []
        
    # The scale to start off with
    initialScale = 100
        
    # The total tick marks on an axis (left + right side - middle tick), must be an even number
    totalTicks = 8
     
    # User input variables
    panPositionRaw = (0, 0)
    panPosition = (0, 0)
    panDiff = (0, 0)
    zoom = 1
    startedInside = False
    
    def __init__(self, **kwargs):
        super(Plot2D, self).__init__(**kwargs) # Call super constructor
    
    # Draw the plot with a title and a subtitle
    def drawPlot(self, title, drawSubtitle, selectedR, x0, iterations):
        # Update the selected R value
        self.selectedR = selectedR
        
        # Update the number of iterations to do
        self.iterations = iterations
        
        # Update the x0 value
        self.x0 = x0
        
        # Update the pan position
        self.panPosition = (self.panPositionRaw[0] + self.panDiff[0], self.panPositionRaw[1] + self.panDiff[1])
        
        # Update the title and whether or not to draw the subtitle
        self.title = title
        self.drawSubtitle = drawSubtitle
        
        # Draw onto the canvas
        with self.canvas:
            self.canvas.clear() # Clear the canvas for new drawing
            
            self.labels.clear() # Clear the labels list
            self.lines.clear() # Clear the lines list
            
            # Cache some frequently used values
            self.halfWidth = self.width / 2
            self.halfHeight = self.height / 2

            # Background color
            Color(0.5, 0.5, 0.5)
            RoundedRectangle(pos = self.pos, size = self.size)

            # Axes
            self.drawAxes()
            
            # Function graph
            self.graphFunction(x0)
            
            # Title and it's container
            Color(0.78, 0.78, 0.78)
            RoundedRectangle(pos = (self.localizeXSt(-self.halfWidth), self.localizeYSt(self.halfHeight - 24)), size = (140, 24))
            Rectangle(pos = (self.localizeXSt(-self.halfWidth), self.localizeYSt(self.halfHeight - 24)), size = (10, 12))
            Rectangle(pos = (self.localizeXSt(130 - self.halfWidth), self.localizeYSt(self.halfHeight - 12)), size = (10, 12))
            Color(0.1, 0.1, 0.1)
            self.labels.append(Label(center = (self.localizeXSt(70 - self.halfWidth), self.localizeYSt(self.halfHeight - 12)), color = (0.15, 0.15, 0.15), text = title))
            
            if drawSubtitle:
                # Selected R value label
                Color(0.78, 0.78, 0.78)
                str = "R = {}".format(round(self.selectedR, 5))
                labelWidth = 12 * len(str)
                RoundedRectangle(pos = (self.localizeXSt(self.halfWidth - labelWidth), self.localizeYSt(self.halfHeight - 24)), size = (labelWidth, 24))
                Rectangle(pos = (self.localizeXSt(self.halfWidth - 10), self.localizeYSt(self.halfHeight - 24)), size = (10, 12))
                Rectangle(pos = (self.localizeXSt(self.halfWidth - labelWidth), self.localizeYSt(self.halfHeight - 12)), size = (10, 12))
                Color(0.1, 0.1, 0.1)
                self.labels.append(Label(center = (self.localizeXSt(self.halfWidth - labelWidth / 2), self.localizeYSt(self.halfHeight - 12)), color = (0.15, 0.15, 0.15), text = str))
    
    #region Input
    def on_touch_down(self, touch):
        # Check if the input is inside this widget
        if self.collide_point(*touch.pos):
            self.startedInside = True
            
            # Check if scrolling with scroll wheel
            if touch.is_mouse_scrolling:
                if touch.button == 'scrolldown':
                    self.zoom = self.zoom / 1.1
                    self.panPosition = (self.panPosition[0] / 1.1, self.panPosition[1] / 1.1)
                elif touch.button == 'scrollup':
                    self.zoom = self.zoom * 1.1
                    self.panPosition = (self.panPosition[0] * 1.1, self.panPosition[1] * 1.1)
            else:
                # Not scrolling, so get panning input
                self.startPos = touch.pos
            
            # Redraw the widget
            self.drawPlot(self.title, self.drawSubtitle, self.selectedR, self.x0, self.iterations)

            # Propogate the touch to child widgets
            return super().on_touch_down(touch)
        else:
            self.startedInside = False
        
    def on_touch_move(self, touch):
        if self.startedInside: # Check if the input started inside of this widget
            if not touch.is_mouse_scrolling:
                # Not scrolling, so get panning input
                self.panDiff = (touch.pos[0] - self.startPos[0], touch.pos[1] - self.startPos[1])
            
            # Redraw the widget
            self.drawPlot(self.title, self.drawSubtitle, self.selectedR, self.x0, self.iterations)
            
            # Propogate the touch to child widgets
            return super().on_touch_move(touch)
        
    def on_touch_up(self, touch):
        if self.startedInside: # Check if the input started inside of this widget
            if not touch.is_mouse_scrolling:
                # Not scrolling, so get panning input
                self.panPositionRaw = (self.panPositionRaw[0] + self.panDiff[0], self.panPositionRaw[1] + self.panDiff[1])
                self.panDiff = (0, 0)
            
            # Redraw the widget
            self.drawPlot(self.title, self.drawSubtitle, self.selectedR, self.x0, self.iterations)
            
            self.startedInside = False
            
            # Propogate the touch to child widgets
            return super().on_touch_up(touch)
    #endregion

    # Localize an x value to this widget's local coordinates incorporating user input (offset and scale)
    def localizeX(self, x) -> int:
        return round(self.pos[0] + self.halfWidth + x + self.panPosition[0])
    
    # Localize an y value to this widget's local coordinates incorporating user input (offset and scale)
    def localizeY(self, y) -> int:
        return round(self.pos[1] + self.halfHeight + y + self.panPosition[1])
    
    # Localize a stationary x value to this widget's local coordinates
    def localizeXSt(self, x) -> int:
        return round(self.pos[0] + self.halfWidth + x)
    
    # Localize a stationary y value to this widget's local coordinates
    def localizeYSt(self, y) -> int:
        return round(self.pos[1] + self.halfHeight + y)
    
    # Draw the plot axes
    def drawAxes(self):
        # scale = scatterProperties[1] + self.initialScale
        
        # If totalTicks is odd, fix it by adding one to it
        # if self.totalTicks % 2 != 0:
        #     self.totalTicks = self.totalTicks + 1
        
        # xRange = (-scale + (scatterProperties[0][0] * scale), scale + (scatterProperties[0][0] * scale)) 
        # yRange = (-scale + (scatterProperties[0][1] * scale), scale + (scatterProperties[0][1] * scale)) 
        
        # xTicks = self.width / self.totalTicks
        # yTicks = self.height / self.totalTicks
        
        # print("x {}, y {}".format(xRange, yRange))
        
        # Grid lines
        # Color(0.5, 0.5, 0.5)   
        # for xTick in np.arange(0, self.width, xTicks):
        #     xVal = remap(0, self.width,xRange[0], xRange[1], xTick)
        #     if xTick != 0 and xTick != self.width and xTick != self.halfWidth:
        #         Line(points = [self.localizeX(xVal), self.localizeYSt(0), self.localizeX(xVal), self.localizeYSt(self.height)], width = 1, cap = 'none')

        # for yTick in np.arange(yRange[0], yRange[1], yTicks):
        #     yVal = remap(0, self.height, yRange[0], yRange[1], yTick)
        #     if yTick != 0 and yTick != self.height and yTick != self.halfHeight:
        #         Line(points = [self.localizeXSt(0), self.localizeY(yVal), self.localizeXSt(self.width), self.localizeY(yVal)], width = 1, cap = 'none')
        
        # # Axis labels
        # for xTick in np.arange(0, self.width, yTicks * 2):
        #     xVal = remap(0, self.width, xRange[0], xRange[1], xTick)
            
        #     # Get an edge offset to prevent it from going off the screen if its the first or last label
        #     edgeOffset = 22 if (xTick == 0) else -20 if (xTick == self.width) else 0
        
        #     labelStr = str(round(xVal, 2))
                                        
        #     # White rectangle behind the label to make reading easier
        #     strLenBoxSize = len(labelStr) * 4.5 # Use the length of the string to get the blocker's size
        #     Color(0.4, 0.4, 0.4)
        #     Rectangle(pos = (self.localizeX((xTick + edgeOffset) - strLenBoxSize), self.localizeY(self.halfHeight - 18 - 10)), size = (strLenBoxSize * 2, 20))
                                
        #     # Label
        #     Color(1.0, 1.0, 1.0)
        #     self.labels.append(Label(center = (self.localizeX(xTick  + edgeOffset), self.localizeY(self.halfHeight - 18)), text = labelStr))

        # for yTick in np.arange(0, self.height, yTicks * 2):
            # yVal = remap(0, self.height, yRange[0], yRange[1], yTick)
            
            # # Get an edge offset to prevent it from going off the screen if its the first or last label
            # edgeOffset = 16 if (yTick == 0) else -16 if (yTick == self.height) else 0
            
            # if yTick != self.halfHeight:
            #     labelStr = str(round(yVal, 2))
                
            #     # White box behind the label to make reading easier
            #     strLenBoxSize = len(labelStr) * 4.5 # Use the length of the string to get the blocker's size
            #     Color(0.4, 0.4, 0.4)
            #     Rectangle(pos = (self.localizeX(self.halfWidth + (((len(labelStr) / 2) * -10 - 5) - strLenBoxSize)), self.localizeYSt((yTick + edgeOffset) - 10)), size = (strLenBoxSize, 20))
                
            #     Color(1.0, 1.0, 1.0)
            #     self.labels.append(Label(center = (self.localizeX(self.halfWidth + ((len(labelStr) / 2) * -10 - 5)), self.localizeYSt(yTick + edgeOffset)), text = labelStr))
        
        # Axis names
        Color(1.0, 1.0, 1.0)
        self.labels.append(Label(center = (self.localizeXSt(self.halfWidth - 8), self.localizeY(10)), text = "x"))
        self.labels.append(Label(center = (self.localizeX(10), self.localizeYSt(self.halfHeight - 8)), text = "y"))
        
        # Zero label
        zeroLabelPos = (self.localizeX(-11.5), self.localizeY(-14))
        self.labels.append(Label(center = zeroLabelPos, text = "0"))

        # Axis lines
        Line(points = [self.localizeX(0), self.localizeYSt(-self.halfHeight), self.localizeX(0), self.localizeYSt(self.halfHeight)], width = 1, cap = 'none')
        Line(points = [self.localizeXSt(-self.halfWidth), self.localizeY(0), self.localizeXSt(self.halfWidth), self.localizeY(0)], width = 1, cap = 'none')
    
    # Graphing the function
    def graphFunction(self, x0):
        scale = self.initialScale * self.zoom

        #region Graph the function
        Color(0.98, 0.49, 0.09)

        # Get the x range from the width using the input offset and scale
        startX = -(self.halfWidth / scale) - (self.panPosition[0] / scale)
        endX = (self.halfWidth / scale) - (self.panPosition[0] / scale)
        
        # Make remapping an x coordinate slightly faster to type out
        def remapX(val):
            return remap(-self.halfWidth, self.halfWidth, startX, endX, val)
        
        # Used to store point values
        funcPoints = []
        
        # Iterate for every x pixel value        
        for x in range(round(-self.halfWidth), round(self.halfWidth), 5):
            # Evaluate the function using the remapped x pixel value
            y = f(self.selectedR, remapX(x)) * scale
                        
            # Get and localize the point
            point = (self.localizeXSt(x), self.localizeY(y))
            
            # Add the point to the list of points to draw
            funcPoints.append(point)
        
        # Draw the function line
        self.lines.append(Line(points = funcPoints, width = 1.5, cap = 'none'))
        #endregion
        
        #region Cobweb Diagram
        # Draw the steady state line
        Color(0.37, 0.25, 0.65)
        ssPtA = (self.localizeXSt(-self.halfWidth), self.localizeY(remapX(-self.halfWidth) * scale))
        ssPtB = (self.localizeXSt(self.halfWidth), self.localizeY(remapX(self.halfWidth) * scale))
        self.lines.append(Line(points = (ssPtA, ssPtB), width = 1))
                            
        # Used to store cobweb line points
        cobwebPoints = []
        lastPoint = (x0, f(self.selectedR, x0))
        cobwebPoints.append((self.localizeX(x0 * scale), self.localizeY(0)))
        cobwebPoints.append((self.localizeX(lastPoint[0] * scale), self.localizeY(lastPoint[1] * scale)))
        
        # Iterate for the cobweb diagram
        for i in range(0, self.iterations - 1):
            ptA = (lastPoint[1], lastPoint[1])
            cobwebPoints.append((self.localizeX(ptA[0] * scale), self.localizeY(ptA[1] * scale)))
            
            ptB = (lastPoint[1], f(self.selectedR, lastPoint[1]))
            cobwebPoints.append((self.localizeX(ptB[0] * scale), self.localizeY(ptB[1] * scale)))
            lastPoint = ptB
        
        # Draw the cobweb line
        Color(0.17, 0.43, 0.70)
        self.lines.append(Line(points = cobwebPoints, width = 1.25, cap = 'none'))
        
        #endregion
        
        dummyToFixEndRegionVisualBug = 1

# The cobweb diagram widget
class CobwebDiagram(Widget):
    # The selected R value
    selectedR = 2
    
    # Cobweb variables
    cobwebIterations = 50
        
    def __init__(self, **kwargs):
        super(CobwebDiagram, self).__init__(**kwargs) # Call super constructor
        
        # Create the 2D Plot widget
        self.plot = Plot2D()
        self.add_widget(self.plot)
        
        # Create a label for the x0 slider
        self.x0Label = Label(text = "x[sub]0[/sub] = 0.20", markup = True)
        self.add_widget(self.x0Label)
        
        # Create the x0 slider widget
        self.x0Slider = Slider(min = 0, max = 100, value = 20)
        self.x0Slider.cursor_size = (20, 20)
        self.add_widget(self.x0Slider)
        
        # Redraw the plot if the x0 slider changes
        self.x0Slider.bind(value = self.x0SliderChangedCallack)
        
        # Resize children and redraw the widget if resized
        self.bind(pos = self.resizeMoveCallback, size = self.resizeMoveCallback)
        
        self.draw()
    
    # Callback for resizing or moving this widget
    def resizeMoveCallback(self, instance, value):
        self.plot.pos = self.pos
        self.plot.size = self.size
        self.x0Slider.pos = (self.x + 70, self.y + 10)
        self.x0Slider.size = (self.width - 70, 20)
        self.x0Label.center = (self.x + 40, self.y + 20)
        self.draw()
    
    # Callback for the x0 slider value change
    def x0SliderChangedCallack(self, instance, value):
        self.x0Label.text = "x[sub]0[/sub] = {}".format(round(self.x0Slider.value_normalized, 2))
        self.draw()
    
    # Draw the 2d plot
    def draw(self):
        self.plot.drawPlot("Cobweb Diagram", True, self.selectedR, self.x0Slider.value_normalized, self.cobwebIterations)

# The time-series widget
class TimeSeries(Widget):
    # The selected R value
    selectedR = 2
    
    # Time Series variables
    startValue = random()
    timeSeriesIterations = 20
    
    # Padding from the edges [left, bottom, right, top]
    padding = [18, 15, 15, 30]
    
    # Trick GC into not clearing all the label/point objects being created
    labels = []
    points = []
    
    # Input
    startedInside = False
    
    def __init__(self, **kwargs):
        super(TimeSeries, self).__init__(**kwargs) # Call super constructor
                        
        # Redraw the widget if resized or moved
        self.bind(size = self.resizeCallback, pos = self.resizeCallback)
    
    # Resize callback, simply redraws this widget
    def resizeCallback(self, instance, value):
        self.draw() 
        
    #region Input
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.startedInside = True
            
            # Randomize the start value
            self.startValue = random()
           
            # Redraw
            self.draw()
            
            # Propogate the touch event to this widget's children
            super().on_touch_down(touch)
        else:
            self.startedInside = False
    
    def on_touch_move(self, touch):
        if self.startedInside:
            # Randomize the start value
            self.startValue = random()
           
            # Redraw
            self.draw()
            
            # Propogate the touch event to this widget's children
            super().on_touch_move(touch)
    #endregion
    
    # Localize an x value to this widget's local coordinates
    def localizeX(self, x):
        return self.x + x
        
    # Localize an y value to this widget's local coordinates
    def localizeY(self, y):
        return self.y + y
    
    # Draw the widget
    def draw(self):
        # Draw onto the canvas
        with self.canvas:
            self.canvas.clear() # Clear the canvas for new drawing
            
            self.labels.clear() # Clear the labels list
            self.points.clear() # Clear the points list
            
            # Cache some frequently used values (yes, I am optimizing this because it involves dividing... oPtImIzAtIoN)
            self.halfWidth = self.width / 2
            self.halfHeight = self.height / 2
            w = (self.width - (self.padding[0] + self.padding[2])) / 2 # Half of the width of the padded space
                        
            # Background color
            Color(0.5, 0.5, 0.5)
            RoundedRectangle(pos = self.pos, size = self.size)
            
            # Draw the axes
            self.drawAxes()

            # Draw the time series
            self.drawTimeSeries()
            
            # Title and it's container
            Color(0.78, 0.78, 0.78)
            RoundedRectangle(pos = (self.x, self.y + self.height - 24), size = (110, 24))
            Rectangle(pos = (self.x, self.y + self.height - 24), size = (10, 12))
            Rectangle(pos = (self.x + 100, self.y + self.height - 12), size = (10, 12))
            Color(0.1, 0.1, 0.1)
            self.labels.append(Label(center = (self.x + 55, self.y + self.height - 12), color = (0.15, 0.15, 0.15), text = "Time Series"))
            
            # Start value label
            Color(0.78, 0.78, 0.78)
            str = "x[sub]0[/sub] = {}".format(round(self.startValue, 5))
            labelWidth = 5 * len(str)
            RoundedRectangle(pos = (self.localizeX(self.width - labelWidth), self.localizeY(self.height - 24)), size = (labelWidth, 24))
            Rectangle(pos = (self.localizeX(self.width - 10), self.localizeY(self.height - 24)), size = (10, 12))
            Rectangle(pos = (self.localizeX(self.width - labelWidth), self.localizeY(self.height - 12)), size = (10, 12))
            Color(0.1, 0.1, 0.1)
            self.labels.append(Label(center = (self.localizeX(self.width - labelWidth / 2), self.localizeY(self.height - 12)), color = (0.15, 0.15, 0.15), text = str, markup = True))
        
    # Draw the axes
    def drawAxes(self):
        # Axis lines
        Color(1, 1, 1)
        Line(points = ((self.localizeX(self.padding[0]), self.localizeY(self.padding[1])), (self.localizeX(self.width - self.padding[2]), self.localizeY(self.padding[1]))), width = 1.25)
        Line(points = ((self.localizeX(self.padding[0]), self.localizeY(self.padding[1])), (self.localizeX(self.padding[0]), self.localizeY(self.height - self.padding[3]))), width = 1.25)
        
        # Draw axis labels
        self.labels.append(Label(center = (self.localizeX(self.padding[0] / 2), self.localizeY((self.height / 2) + self.padding[1] - self.padding[3] )), text = "X[sub]t[/sub]", markup = True, font_size = 12))
        self.labels.append(Label(center = (self.localizeX(self.width - (self.padding[2] / 2) + 2), self.localizeY(self.padding[1] + 2)), text = "t", font_size = 12))
        
        # Draw axis values
        # X-axis (t)
        for x in range(0, self.timeSeriesIterations, round(self.timeSeriesIterations / 5)):
            label = Label(center = (self.localizeX(remap(0, self.timeSeriesIterations, self.padding[0], self.width - self.padding[2],x)), self.localizeY(self.padding[1] / 2)), text = str(round(x, 2)), font_size = 11)
            self.labels.append(label)
        
        # Y-axis (xt)
        for y in range(0, 2):
            label = Label(center = (self.localizeX(self.padding[0] / 2), self.localizeY(remap(0, 1, self.padding[1], self.height - self.padding[3] - 5, y))), text = str(round(y, 2)), font_size = 11)
            self.labels.append(label)
    
    # Draw the time series
    def drawTimeSeries(self):
        # Set the draw color
        Color(0.98, 0.49, 0.09)
        
        # Variables
        t = 0
        xValue = self.startValue
        lastPoint = None
        step = self.timeSeriesIterations / 20
                
        # Iterate for every pixel in the draw space
        while t <= self.timeSeriesIterations:
            point = (self.localizeX(remap(0, self.timeSeriesIterations, self.padding[0] + 1, self.width - self.padding[2], t)),
                     self.localizeY(remap(0, 1, self.padding[1] + 5, self.height - self.padding[3] - self.padding[1], xValue)))
            
            if lastPoint != None:
                self.points.append(Line(points = [lastPoint, point], width = 1.25, cap = 'none'))
            
            lastPoint = point

            xValue = f(self.selectedR, xValue) # Evaluate the function
            
            t += step # Step t by a set amount
#endregion

# The root widget, contains the entire GUI. Uses the box layout manager
class Root(BoxLayout):
    def __init__(self, **kwargs):
        super(Root, self).__init__(**kwargs) # Call super constructor
        
        logging.info("Initializing GUI")
        
        # Set main layout orientation to vertical
        self.orientation = 'vertical'
        
        # Create the top bar
        self.createTopBar()
        
        # Create main GUI
        self.createMainGUI()
    
    # Create the top bar and its contained widgets
    def createTopBar(self):
        topBar = ActionBar()
        self.add_widget(topBar)
        
        view = ActionView(use_separator = True, background_color = [0.78, 0.78, 0.78], background_image = '')
        topBar.add_widget(view)
        
        name = ActionPrevious(title = "Logistic Explorer", color = 'black', app_icon = 'appIcon.png', with_previous = False)
        view.add_widget(name)
        
        help = ActionButton(text = "?", color = 'black', font_size = 24)
        help.bind(on_release = self.showHelp)
        view.add_widget(help)
        
        # Create the help popup. Must be at the lowest level to prevent layering issues
        self.helpPopup = Popup(title = 'Help', size_hint = (None, None), size = (650, 400))
        helpText = Label(halign = 'justify', text='''
                         - Click anywhere in the Bifurcation Diagram to select an R value\n
                         - Move the slider in the Cobweb Diagram to change the X[sub]0[/sub]\n
                         - You can pan in both the Cobweb and Bifurcation Diagrams with the mouse\n
                         - You can zoom in both the Cobweb and Bifurcation Diagrams with the scroll wheel\n
                         - Double click and drag in the Bifurcation Diagram to slide through R values (looks cool)\n
                         - Clicking or dragging on the time series will randomize its start value\n
                         - Press the escape key to close, or just press the x button
                         
                         Created by Alexander Irausquin-Petit, 10/2022
                        ''', markup = True)
        self.helpPopup.content = helpText

    # Show the help panel
    def showHelp(self, instance):
        self.helpPopup.open()
    
    # Create the main panel that will contain all the GUI elements
    def createMainGUI(self):
        # Main panel
        self.mainPanel = BoxLayout(orientation = "vertical", padding = [5, 5, 5, 5], spacing = 5.5)
        self.add_widget(self.mainPanel)

        #region Create the main panel widgets
        # Create the upper panel on the top half of the main screen
        self.upperPanel = BoxLayout(orientation = 'horizontal', size_hint = (1.0, 0.5), spacing = 5.5)
        self.mainPanel.add_widget(self.upperPanel)

        #region Create the upper panel widgets
        # Create the controls panel and timeseries widget container on left side of upper panel
        self.leftUpperPanel = BoxLayout(orientation = 'vertical', size_hint = (0.4, 1.0), spacing = 5.5)
        self.upperPanel.add_widget(self.leftUpperPanel)
        
        #region Create the left upper panel widgets
        # Create the timeseries panel on the bottom part of the upper left panel
        self.timeseries = TimeSeries()
        #endregion
        
        # Create the Cobweb Diagram on the right side of the upper panel
        self.cobwebDiag = CobwebDiagram(size_hint = (0.6, 1.0))
        self.upperPanel.add_widget(self.cobwebDiag)
        #endregion
        
        # Create the Bifurcation Diagram on the lower half of the main screen
        self.bifurcationDiag = BifurcationDiagram(cobwebDiag = self.cobwebDiag, timeseries = self.timeseries, size_hint = (1.0, 0.5))
        self.mainPanel.add_widget(self.bifurcationDiag)
        
        # Create the options panel on the top part of the upper left panel
        self.optionsPanel = OptionsPanel(self.cobwebDiag, self.bifurcationDiag, self.timeseries)
        self.leftUpperPanel.add_widget(self.optionsPanel)
        
        # Add the timeseries to the left upper panel AFTER the options panel so that it shows up below it
        self.leftUpperPanel.add_widget(self.timeseries)
        #endregion
        
        logging.info("GUI initialization complete")

# The options panel, as a widget for clarity
class OptionsPanel(BoxLayout):
    def __init__(self, cobweb, bifur, timeSeries, **kwargs):
        super(OptionsPanel, self).__init__(**kwargs) # Call super constructor
        
        # Set up references
        self.cobweb = cobweb
        self.bifur = bifur
        self.timeSeries = timeSeries
        
        # Redraw the widget if resized or moved
        self.bind(size = self.resizeCallback, pos = self.resizeCallback)
        
        self.addWidgets()
    
    # Resize callback, simply redraws this widget
    def resizeCallback(self, instance, value):
        self.draw() 
    
    # Draw the title
    def draw(self):
        with self.canvas.before:
            self.canvas.before.clear() # Clear the canvas for new drawing
            
            # Background color
            Color(0.5, 0.5, 0.5)
            RoundedRectangle(pos = self.pos, size = self.size)
            
            # Title
            Color(0.78, 0.78, 0.78)
            labelWidth = 77
            RoundedRectangle(pos = (self.x, self.y + self.height - 24), size = (labelWidth, 24))
            Rectangle(pos = (self.x, self.y + self.height - 24), size = (10, 12))
            Rectangle(pos = (self.x + labelWidth - 10, self.y + self.height - 12), size = (10, 12))
            Color(0.1, 0.1, 0.1)
            self.title = Label(center = (self.x + labelWidth / 2, self.y + self.height - 12), color = (0.15, 0.15, 0.15), text = "Options", markup = True)
    
    # Populate the options panel with a title and options widgets
    def addWidgets(self):
        #region Text input callbacks
        cobweb = self.cobweb
        bifur = self.bifur
        timeSeries = self.timeSeries
        
        # Cobweb input callback
        def onEnterCobweb(instance):
            cobweb.cobwebIterations = int(instance.text)
            cobweb.draw()
        
        # Bifurcation input callback
        def onEnterBifurcation(instance):
            bifur.transientCount = int(instance.text)
            bifur.draw()
        
        # Time series input callback
        def onEnterTimeSeries(instance):
            timeSeries.timeSeriesIterations = int(instance.text)
            timeSeries.draw()
        #endregion
        
        
        # Create a container for the options widgets in order to give the title some space
        optionsContainer = GridLayout(cols = 3, rows = 2, row_default_height = 40, padding = [10, 20, 10, 10])
        self.add_widget(optionsContainer)
        
        #region Create the options widgets and their labels
        cobwebLabel = Label(text = "Cobweb Diagram\nTransient Iterations", color = 'white', halign = 'center', font_size = 12)
        optionsContainer.add_widget(cobwebLabel)
        timeSeriesLabel = Label(text = "Time Series\nIterations", color = 'white', halign = 'center', font_size = 12)
        optionsContainer.add_widget(timeSeriesLabel)
        bifurcationLabel = Label(text = "Bifurcation Diagram\nTransient Iterations", color = 'white', halign = 'center', font_size = 12)
        optionsContainer.add_widget(bifurcationLabel)
        
        cobwebDiagInput = TextInput(text = "50", multiline = False, input_type = 'number', input_filter = 'int', write_tab = False)
        cobwebDiagInput.bind(on_text_validate = onEnterCobweb)
        optionsContainer.add_widget(cobwebDiagInput)
        timeSeriesInput = TextInput(text = "20", multiline = False, input_type = 'number', input_filter = 'int', write_tab = False)
        timeSeriesInput.bind(on_text_validate = onEnterTimeSeries)
        optionsContainer.add_widget(timeSeriesInput)
        bifurcationDiagInput = TextInput(text = "100", multiline = False, input_type = 'number', input_filter = 'int', write_tab = False)
        bifurcationDiagInput.bind(on_text_validate = onEnterBifurcation)
        optionsContainer.add_widget(bifurcationDiagInput)
        #endregion
        
        dummyToFixEndRegionVisualBug = 1

# Main app
class LogisticExplorerApp(App):
    # Build the structure of this app
    def build(self):
        self.icon = 'appIcon.png' # Set icon
        
        root = Root()
        
        # Change the background color
        Window.clearcolor = (1, 1, 1)
        
        return root

#region Utils
def f(R, x):
    return R * x * (1 - x)

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

def remap(min1: float, max1: float, min2: float, max2: float, f: float) -> float:
    """Remap values from one linear scale to another, a combination of lerp and inv_lerp.
    i_min and i_max are the scale on which the original value resides,
    o_min and o_max are the scale to which it should be mapped.
    Examples
    --------
        45 == remap(0, 100, 40, 50, 50)
        6.2 == remap(1, 5, 3, 7, 4.2)
    """
    return lerp(min2, max2, inverseLerp(min1, max1, f))
#endregion

# Main function        
if __name__ == '__main__':
    logging.basicConfig(format="%(asctime)s %(message)s", encoding="utf-8", level=logging.DEBUG)
    LogisticExplorerApp().run()