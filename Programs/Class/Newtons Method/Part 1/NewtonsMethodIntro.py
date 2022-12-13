import logging as Log
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
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

import numpy as np

# Set kivy config
Config.set("graphics", "width", "1920")
Config.set("graphics", "height", "1080")
Config.set('kivy','window_icon','appIcon.png')
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

# A 2D Graph. Inherits from StencilView in order to more easily keep the drawn lines inside of the widget's bounds
class Graph2D(StencilView):
    # The selected R value
    selectedR = 2
    
    # Trick GC into not clearing all the label/line objects being created
    labels = []
    lines = []
        
    # The number of tick marks on an axis (only one side), must be an even number
    totalTicks = 5
     
    # User input variables
    panPositionRaw = (0, 0)
    panPosition = (0, 0)
    panDiff = (0, 0)
    zoom = 1.0
    startedInside = False
    
    def __init__(self, function, title, subtitle = None, scalePercent = 100, initialZoom = 1.0, initialPanPosition = (0.0, 0.0), **kwargs):
        super(Graph2D, self).__init__(**kwargs) # Call super constructor
        
        # Set variables
        self.title = title
        self.subtitle = subtitle
        self.f = function
        self.scale = scalePercent
        self.zoom = initialZoom
        self.panPosition = initialPanPosition
        
        # Redraw the widget if resized
        self.bind(pos = self.resizeMoveCallback, size = self.resizeMoveCallback)
        
        self.draw()
    
    # Callback for resizing or moving this widget
    def resizeMoveCallback(self, instance, value):
        self.draw()
    
    # Draw the plot
    def draw(self):
        # Update the pan position
        self.panPosition = (self.panPositionRaw[0] + self.panDiff[0], self.panPositionRaw[1] + self.panDiff[1])
        
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
            self.graphFunction()
            
            # Title and it's container
            Color(0.78, 0.78, 0.78)
            str = self.title
            labelWidth = 12 * len(str)
            RoundedRectangle(pos = (self.localizeXSt(-self.halfWidth), self.localizeYSt(self.halfHeight - 24)), size = (labelWidth, 24))
            Rectangle(pos = (self.localizeXSt(-self.halfWidth), self.localizeYSt(self.halfHeight - 24)), size = (10, 12))
            Rectangle(pos = (self.localizeXSt(labelWidth - 10 - self.halfWidth), self.localizeYSt(self.halfHeight - 12)), size = (10, 12))
            Color(0.1, 0.1, 0.1)
            self.labels.append(Label(center = (self.localizeXSt((labelWidth / 2) - self.halfWidth), self.localizeYSt(self.halfHeight - 12)), color = (0.15, 0.15, 0.15), text = self.title))
            
            if self.subtitle != None:
                # Selected R value label
                Color(0.78, 0.78, 0.78)
                str = self.subtitle
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
            self.draw()

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
            self.draw()
            
            # Propogate the touch to child widgets
            return super().on_touch_move(touch)
        
    def on_touch_up(self, touch):
        if self.startedInside: # Check if the input started inside of this widget
            if not touch.is_mouse_scrolling:
                # Not scrolling, so get panning input
                self.panPositionRaw = (self.panPositionRaw[0] + self.panDiff[0], self.panPositionRaw[1] + self.panDiff[1])
                self.panDiff = (0, 0)
            
            # Redraw the widget
            self.draw()
            
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
        scale = self.scale * self.zoom
        
        # Get the start X and end X from the width using the input offset and scale
        startX = -(self.halfWidth / scale) - (self.panPosition[0] / scale)
        endX = (self.halfWidth / scale) - (self.panPosition[0] / scale)
        xRange = abs(endX - startX)
        
        # if xRange % 10 == 0:
        #     xTicks = 10
        # elif xRange % 5 == 0:
        #     xTicks = 
        # elif xRange % 4 == 0:
        #     xTicks = 4
        # else:
        #     xTicks = 2
        
        xTicks = 0.5
        
       
        # print(xTicks) 
                
        # Grid lines
        Color(0.3, 0.3, 0.3)
        halfWidthRounded = round(self.halfWidth)
        halfHeightRounded = round(self.halfHeight)
        
        # Vertical lines
        # for pixelX in np.arange(-self.halfWidth, self.halfWidth, 1):
        #     xTick = remap(-self.halfWidth, self.halfWidth, startX, endX, pixelX)
        #     if xTick % xTicks <= 0.01:
        #         Line(points = [self.localizeXSt(pixelX), self.localizeYSt(-self.halfHeight), self.localizeXSt(pixelX), self.localizeYSt(self.halfHeight)], width = 1, cap = 'none')
            
        
        # for xTick in range(-halfWidthRounded, halfWidthRounded, xTicks):
        #     xVal = remap(-halfWidthRounded, halfWidthRounded, startX, endX, xTick)
        #     if xTick != -self.halfWidth and xTick != 0 and xTick != self.halfWidth:
        #         Line(points = [self.localizeX(xVal), self.localizeYSt(-self.halfHeight), self.localizeX(xVal), self.localizeYSt(self.halfHeight)], width = 1, cap = 'none')
        
        #region Axis labels
        # for xTick in range(-halfWidthRounded, halfWidthRounded, xTicks * 2):
        #     xVal = remap(-halfWidthRounded, halfWidthRounded, startX, endX, xTick)
            
        #     # Get an edge offset to prevent it from going off the screen if its the first or last label
        #     edgeOffset = 22 if (xTick == -self.halfWidth) else -20 if (xTick == self.halfWidth) else 0
        
        #     labelStr = str(round(xVal, 2))
                                        
        #     # White rectangle behind the label to make reading easier
        #     strLenBoxSize = len(labelStr) * 4.5 # Use the length of the string to get the blocker's size
        #     Color(0.4, 0.4, 0.4)
        #     Rectangle(pos = (self.localizeX((xTick + edgeOffset) - strLenBoxSize), self.localizeY(-28)), size = (strLenBoxSize * 2, 20))
                                
        #     # Label
        #     Color(1.0, 1.0, 1.0)
        #     self.labels.append(Label(center = (self.localizeX(xTick  + edgeOffset), self.localizeY(-18)), text = labelStr))

        # for yTick in range(-halfHeightRounded, halfHeightRounded, yTicks * 2):
        #     yVal = remap(-halfHeightRounded, halfHeightRounded, startX, endX, yTick)
            
        #     # Get an edge offset to prevent it from going off the screen if its the first or last label
        #     edgeOffset = 16 if (yTick == 0) else -16 if (yTick == self.height) else 0
            
        #     if yTick != self.halfHeight:
        #         labelStr = str(round(yVal, 2))
                
        #         # White box behind the label to make reading easier
        #         strLenBoxSize = len(labelStr) * 4.5 # Use the length of the string to get the blocker's size
        #         Color(0.4, 0.4, 0.4)
        #         Rectangle(pos = (self.localizeX(((len(labelStr) / 2) * -10 - 5) - strLenBoxSize), self.localizeYSt((yTick + edgeOffset) - 10)), size = (strLenBoxSize, 20))
                
        #         Color(1.0, 1.0, 1.0)
        #         self.labels.append(Label(center = (self.localizeX((len(labelStr) / 2) * -10 - 5), self.localizeYSt(yTick + edgeOffset)), text = labelStr))
        #endregion
        
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
    def graphFunction(self):
        scale = self.scale * self.zoom

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
        halfWidthRounded = round(self.halfWidth)
        for x in range(-halfWidthRounded, halfWidthRounded, 5):
            # Evaluate the function using the remapped x pixel value
            y = self.f(remapX(x)) * scale
                        
            # Get and localize the point
            point = (self.localizeXSt(x), self.localizeY(y))
            
            # Add the point to the list of points to draw
            funcPoints.append(point)
        
        # Draw the function line
        self.lines.append(Line(points = funcPoints, width = 1.5, cap = 'none'))
        #endregion
        
        dummyToFixEndRegionVisualBug = None
        
    def doNewtonsMethod(self):
        with self.canvas.after:
            self.canvas.after.clear()
            
            Color(0, 0, 0)
            self.blah = Line(points = [(0, 0), (10, 10)], width = 5)

class Root(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        funcGraph = Graph2D(function = f, title = "Function Graph")
        self.add_widget(funcGraph)
        
        newtonsMethodButton = Button(pos = (10, 10), size = (50, 20), text = "Perform Newton's Method")
        newtonsMethodButton.bind(on_press = funcGraph.doNewtonsMethod)
        self.add_widget(newtonsMethodButton)
        

class NewtonsMethodExplorer(App):
    def build(self):
        return Root()

#region Utils
def f(x):
    return pow(x - 2, 2) - 2

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
    Log.basicConfig(format="%(asctime)s %(message)s", encoding="utf-8", level=Log.DEBUG)
    NewtonsMethodExplorer().run()