from colorsys import hsv_to_rgb
import math
from Lib.DEgraphicsModified import *


class QuadraticExplorer:
    topBarHeight = 100
    width = 700
    height = width + topBarHeight
    drawHeight = width

    xOffset = 684
    yOffset = 400

    padding = 20
    
    # UI Colors
    controlsAreaColor_Dark = color_rgb(45, 45, 45)
    controlsAreaColor_Light = color_rgb(189, 189, 189)
    equationAreaColor_Dark = color_rgb(61, 61, 61)
    equationAreaColor_Light = color_rgb(92, 92, 92)

    # UI elements (or as tkinter calls it, wIdGeTs)
    mainWindow = None
    drawFrame = None
    graphBtn = None
    aEntry = None
    bEntry = None
    cEntry = None
    scaleEntry = None
    
    a = -1.0
    b = 1.0
    c = 1.0
    scale = 1.0

    halfWidth = int(width / 2)
    halfHeight = int(height / 2)
    halfDrawHeight = halfHeight - topBarHeight
    halfTopBarHeight = int(topBarHeight / 2)

    def main(self):
        # Init the main window and its UI elements
        self.initWindowElements()

        # Initialize the main loop on the main window, this waits until the window is closed. Were not adding close behavior here because it is handled by the window.
        self.mainWindow.mainloop()

    # UI element initialization
    def initWindowElements(self):
        # Creat the main window object
        self.mainWindow = DEGraphWin(defCoords=[-self.halfWidth, -self.halfHeight, self.halfWidth, self.halfHeight],
                                     offsets=[self.xOffset - (self.width / 2),
                                              self.yOffset - (self.height / 2)],
                                     width=self.width,
                                     height=self.height,
                                     hThickness=0,
                                     hasTitlebar=True, darkLightBehavior="System", colorTheme = "blue")
        self.mainWindow.autoflush = True
        
        # Set the custom close protocol
        self.mainWindow.protocol("WM_DELETE_WINDOW", self.close)
        
        # Draw the graph axes
        self.mainWindow.clear()
        self.drawAxes(1)
        self.mainWindow.redraw()
        
        # Create the control elements (top bar panel)
        self.initControlsElements()

    def initControlsElements(self):
        # Controls are background
        controlsArea = Rectangle(Point(-self.halfWidth, self.halfHeight), Point(self.halfWidth, self.halfHeight - self.topBarHeight))
        controlsAreaColor = self.controlsAreaColor_Dark if controlsArea._appearance_mode == 1 else self.controlsAreaColor_Light
        controlsArea.setFill(controlsAreaColor)
        controlsArea.setOutline(controlsAreaColor)
        controlsArea.draw(self.mainWindow)

        ### Draw the sections of the controls area
        sectionSize = self.width / 5

        # Graph button
        self.graphBtn = ModernButton(Point(self.localizeX(sectionSize / 2), self.localizeY(self.topBarHeight / 2 - 15)),
                                     width = 50, 
                                     height = 50,
                                     backdropColor = controlsAreaColor,
                                     labelText = "Graph",
                                     textFont = ("arial", 16, "normal"),
                                     action = self.graph)
        self.graphBtn.activate()
        self.graphBtn.draw(self.mainWindow)
        
        # Graph button
        self.graphBtn = ModernButton(Point(self.localizeX(sectionSize / 2), self.localizeY(self.topBarHeight / 2 + 25)),
                                     width = 50,
                                     height = 20,
                                     backdropColor = controlsAreaColor,
                                     labelText = "Clear",
                                     textFont = ("arial", 10, "normal"),
                                     action = self.mainWindow.clear)
        self.graphBtn.activate()
        self.graphBtn.draw(self.mainWindow)

        # Equation area
        equationArea = Rectangle(Point(self.localizeX(sectionSize), self.localizeY(0)),
                                 Point(self.localizeX(self.width - sectionSize), self.localizeY(self.topBarHeight)))
        equationAreaColor = self.equationAreaColor_Dark if equationArea._appearance_mode == 1 else self.equationAreaColor_Light
        equationArea.setFill(equationAreaColor)
        equationArea.setOutline(equationAreaColor)
        equationArea.draw(self.mainWindow)
        
        # Divider between controls area and draw area
        divider = Line(Point(-self.halfWidth, self.halfHeight - self.topBarHeight + 1), Point(self.halfWidth, self.halfHeight - self.topBarHeight + 1))
        divider.setOutline(ctk.ThemeManager.single_color(ctk.ThemeManager.theme["color"]["text"], divider._appearance_mode))
        divider.draw(self.mainWindow)

        # Equation text and number entries
        equationCenter = self.localizeX((self.width / 2))
        equationHeight = self.localizeY(self.topBarHeight / 2)

        # Label this section as Equation
        equationLabel = Text(
            Point(equationCenter, self.localizeY(20)), "Equation")
        equationLabel.setStyle("bold")
        equationLabel.draw(self.mainWindow)

        # Equation text, showing the quadratic equation
        equationText = Text(
            Point(equationCenter, equationHeight), "y = ___ x² + ___ x + ___")
        equationText.setSize(16)
        equationText.draw(self.mainWindow)

        # Equation value entries
        self.aEntry = DblEntry(Point(equationCenter - 63, equationHeight), 40, backdropColor = equationAreaColor, defaultValue = self.a)
        self.aEntry.draw(self.mainWindow)
        self.aEntry.getValue()

        self.bEntry = DblEntry(Point(equationCenter + 22, equationHeight), 40, backdropColor = equationAreaColor, defaultValue = self.b)
        self.bEntry.draw(self.mainWindow)
        self.bEntry.getValue()

        self.cEntry = DblEntry(Point(equationCenter + 98, equationHeight), 40, backdropColor = equationAreaColor, defaultValue = self.c)
        self.cEntry.draw(self.mainWindow)
        self.cEntry.getValue()

        # Scale entry
        self.scaleEntry = DblEntry(Point(self.localizeX(self.width - (sectionSize / 2)), self.localizeY(self.topBarHeight / 2)),
                                   60,
                                   span = [0.0001, 1000000],
                                   defaultValue = self.scale,
                                   backdropColor = controlsAreaColor,
                                   errorTextColor = color_rgb(255, 122, 122))
        self.scaleEntry.setLabel("Scale", 0, 23, size = 11)
        self.scaleEntry.draw(self.mainWindow)
        self.scaleEntry.getValue()

    # Graphing the function
    def graph(self):
        # Save the values of all the entries in order to reassign them after clearing the screen, bc clearing the screen resets them for some reason
        self.a = self.aEntry.getValue()
        self.b = self.bEntry.getValue()
        self.c = self.cEntry.getValue()
        self.scale = self.scaleEntry.getValue()
        
        # Clear the main window
        self.mainWindow.clear()
        
        # Set the entry values to the saved values
        self.aEntry.setText(str(self.a))
        self.bEntry.setText(str(self.b))
        self.cEntry.setText(str(self.c))
        self.scaleEntry.setText(str(self.scale))
        
        # Draw axes
        self.drawAxes(self.scale)
        
        vals = [self.width]

        # Calculate the graph's points
        print("Calculating with values: a=", self.a, ", b=", self.b, ", c=", self.c)        
        for i in range(-self.halfWidth, self.halfWidth):
            x = self.remap(-self.halfWidth, self.halfWidth, 5 * -self.scale, 5 * self.scale, i)

            val = self.a * (x * x) + self.b * x + self.c

            vals.append(val)
            
        # Draw the graph's points (as lines)
        lines = []
        lastPoint = None
        for i in range(-self.halfWidth, self.halfWidth):
            val = self.remap(5 * self.scale, 5 * -self.scale, -self.halfHeight, self.halfDrawHeight, -vals[i + self.halfWidth])
            if self.halfDrawHeight < val or -self.halfHeight > val:
                lastPoint = None
            else:
                if lastPoint != None:
                    ln = Line(lastPoint, Point(i, min(self.halfDrawHeight, val)))
                    ln.setWidth(3)
                    # ln.setFill(ctk.ThemeManager.single_color(ctk.ThemeManager.theme["color"]["text"], ln._appearance_mode))
                    ln.setFill(color_rgb(227, 137, 34))
                    ln.draw(self.mainWindow)
                    lines.insert(i, ln)

                lastPoint = Point(i, val)

        for line in lines:
            self.mainWindow.delItem(line)

        lines.clear()
        
        # Find and draw the roots
        self.findAndShowRoots(self.a, self.b, self.c)
        
        # Draw the zoom controls
        self.drawZoomControls()

    # Find the roots and display them on the graph
    def findAndShowRoots(self, a, b, c):
        hasRootA = True
        hasRootB = True
        
        # Plug everything into the quadratic formula
        try:
            rootA = (-b + math.sqrt((b * b) - 4 * a * c)) / (2 * a)
        except ValueError :
            hasRootA = False
        except ZeroDivisionError:
            hasRootA = False
            
        try:
            rootB = (-b - math.sqrt((b * b) - 4 * a * c)) / (2 * a)
        except ValueError :
            hasRootB = False
        except ZeroDivisionError:
            hasRootB = False
        
        # Draw a circle around the roots and label them, 
        if hasRootA:
            rootACoord = self.remap(5 * -self.scale, 5 * self.scale, -self.halfWidth, self.halfWidth, rootA)
            
            rootACircle = Circle(Point(rootACoord, 0 - self.halfTopBarHeight), 5)
            rootACircle.setFill(None)
            # rootACircle.setOutline(ctk.ThemeManager.single_color(ctk.ThemeManager.theme["color"]["text"], rootACircle._appearance_mode))
            rootACircle.setOutline(color_rgb(91, 28, 186))
            rootACircle.setWidth(4)
            rootACircle.draw(self.mainWindow)
            
            rootAStr = str(round(rootA, 2))
            rootAStrLen = len(rootAStr) * 4
            rootALabel = Rectangle(Point(rootACoord - rootAStrLen, 30 - self.halfTopBarHeight), Point(rootACoord + rootAStrLen, 10 - self.halfTopBarHeight))
            # rootALabel.setFill(ctk.ThemeManager.single_color(ctk.ThemeManager.theme["color"]["window_bg_color"], rootALabel._appearance_mode))
            rootALabel.setFill(color_rgb(91, 28, 186))
            rootALabel.setLabel(rootAStr, size = 10, color = color_rgb(255, 255, 255))
            rootALabel.draw(self.mainWindow)
            
            self.mainWindow.delItem(rootACircle)
            self.mainWindow.delItem(rootALabel)
        
        if hasRootB:
            rootBCoord = self.remap(5 * -self.scale, 5 * self.scale, -self.halfWidth, self.halfWidth, rootB)
            
            rootBCircle = Circle(Point(rootBCoord, 0 - self.halfTopBarHeight), 5)
            rootBCircle.setFill(None)
            # rootBCircle.setOutline(ctk.ThemeManager.single_color(ctk.ThemeManager.theme["color"]["text"], rootBCircle._appearance_mode))
            rootBCircle.setOutline(color_rgb(91, 28, 186))
            rootBCircle.setWidth(4)
            rootBCircle.draw(self.mainWindow)
            
            rootBStr = str(round(rootB, 2))
            rootBStrLen = len(rootBStr) * 4
            rootBLabel = Rectangle(Point(rootBCoord - rootBStrLen, 30 - self.halfTopBarHeight), Point(rootBCoord + rootBStrLen, 10 - self.halfTopBarHeight))
            # rootBLabel.setFill(ctk.ThemeManager.single_color(ctk.ThemeManager.theme["color"]["window_bg_color"], rootBLabel._appearance_mode))
            rootBLabel.setFill(color_rgb(91, 28, 186))
            rootBLabel.setLabel(rootBStr, size = 10, color = color_rgb(255, 255, 255))
            rootBLabel.draw(self.mainWindow)
            
            self.mainWindow.delItem(rootBCircle)
            self.mainWindow.delItem(rootBLabel)
        
    # Drawing the axes
    def drawAxes(self, scale):
        xTicks = int(self.halfWidth / 10)
        yTicks = int(self.halfHeight / 10)
        
        # Grid lines
        for xTick in range(-self.halfWidth, self.halfWidth, xTicks):
            if xTick != 0:
                tickLine = Line(Point(xTick, -self.halfHeight), Point(xTick, self.halfDrawHeight))

                if xTick == 0:
                    tickLine.setWidth(3)
                elif xTick % 10 == 0:
                    tickLine.setFill(color_rgb(100, 100, 100))
                else:
                    tickLine.setFill(color_rgb(200, 200, 200))

                tickLine.draw(self.mainWindow)

        for yTick in range(-self.halfHeight, self.halfHeight, yTicks):
            yVal = remap(-self.halfHeight, self.halfHeight, -self.halfHeight - 1, self.halfDrawHeight + 1, yTick)
            tickLine = Line(Point(-self.halfWidth, yVal), Point(self.halfWidth, yVal))

            if yTick == 0:
                tickLine.setWidth(3)
            elif int(yVal) % 10 == 0:
                tickLine.setFill(color_rgb(100, 100, 100))
            else:
                tickLine.setFill(color_rgb(200, 200, 200))

            tickLine.draw(self.mainWindow)

        # Axis labels
        labels = list()
        for xTick in range(-self.halfWidth, self.halfWidth, xTicks * 2):
            if xTick != -self.halfWidth:
                if xTick != 0:
                    labelStr = str(round(self.remap(-self.halfWidth, self.halfWidth, 5 * -scale, 5 * scale, xTick), 2))
                    
                    # White box behind the label to make reading easier
                    strLenBoxSize = len(labelStr) * 4.5 # Use the length of the string to get the blocker's size
                    labelBlocker = Rectangle(Point(xTick - strLenBoxSize, (-18 - self.halfTopBarHeight) - 10), Point(xTick + strLenBoxSize, (-18 - self.halfTopBarHeight) + 10))
                    labelBlocker.setFill(ctk.ThemeManager.single_color(ctk.ThemeManager.theme["color"]["window_bg_color"], labelBlocker._appearance_mode))
                    labelBlocker.setWidth(0)
                    labelBlocker.draw(self.mainWindow)
                    
                    # color_rgb(209, 213, 216)
                    
                    # Label
                    xAxisLabel = Text(Point(xTick, -18 - self.halfTopBarHeight), labelStr)
                    xAxisLabel.draw(self.mainWindow)
                    labels.append(xAxisLabel)

        for yTick in range(-self.halfHeight, self.halfHeight, yTicks * 2):
            if yTick != -self.halfHeight:
                yVal = remap(-self.halfHeight, self.halfHeight, -self.halfHeight, self.halfDrawHeight, yTick)
                    
                if yTick == 0:
                    yAxisLabel = Text(Point(-13, -13 - self.halfTopBarHeight), "0")
                    yAxisLabel.draw(self.mainWindow)
                    labels.append(yAxisLabel)
                else:
                    labelStr = str(round(self.remap(-self.halfHeight, self.halfHeight, 5 * -scale, 5 * scale, yTick), 2))
                    
                    # White box behind the label to make reading easier
                    strLenBoxSize = len(labelStr) * 4.5 # Use the length of the string to get the blocker's size
                    labelBlocker = Rectangle(Point(((len(labelStr) / 2) * -10 - 5) - strLenBoxSize, yVal - 10), Point(((len(labelStr) / 2) * -10 - 5) + strLenBoxSize, yVal + 10))
                    labelBlocker.setFill(ctk.ThemeManager.single_color(ctk.ThemeManager.theme["color"]["window_bg_color"], labelBlocker._appearance_mode))
                    labelBlocker.setWidth(0)
                    labelBlocker.draw(self.mainWindow)
                    
                    yAxisLabel = Text(Point((len(labelStr) / 2) * -10 - 5, yVal), labelStr)
                    yAxisLabel.draw(self.mainWindow)
                    labels.append(yAxisLabel)

        for label in labels:
            self.mainWindow.delItem(label)

        labels.clear()

        # Axis names
        xAxisLabel = Text(Point(self.halfWidth - 14, -10 - self.halfTopBarHeight), "x")
        xAxisLabel.setTextColor(ctk.ThemeManager.single_color(ctk.ThemeManager.theme["color"]["text"], xAxisLabel._appearance_mode))
        xAxisLabel.draw(self.mainWindow)
        yAxisLabel = Text(Point(-10, self.halfDrawHeight - 14), "y")
        yAxisLabel.setTextColor(ctk.ThemeManager.single_color(ctk.ThemeManager.theme["color"]["text"], yAxisLabel._appearance_mode))
        yAxisLabel.draw(self.mainWindow)

        # Axis lines
        yAxis = Line(Point(0, -self.halfHeight), Point(0, self.halfDrawHeight))
        yAxis.setWidth(2)
        yAxis.draw(self.mainWindow)

    # Draw on-graph zoom controls
    def drawZoomControls(self):
        # Zoom panel constants
        zoomPanelHeight = 130
        zoomPanelWidth = 40
        zoomPanelX = 40
        zoomPanelY = 40
        zoomPanelPadding = 10
        
        # Zoom button constants
        zoomButtonSpacing = (zoomPanelHeight - (zoomPanelPadding * 2)) / 3
        zoomButtonSize = zoomPanelWidth - (zoomPanelPadding * 2)
        
        # Draw zoom controls background, I wanna try to round out its corners
        zoomControlBackground = Rectangle(Point(self.halfWidth - zoomPanelX, self.halfDrawHeight - zoomPanelY), Point(self.halfWidth - (zoomPanelX + zoomPanelWidth), self.halfDrawHeight - (zoomPanelY + zoomPanelHeight)))
        zoomPanelColor = ctk.ThemeManager.single_color(ctk.ThemeManager.theme["color"]["window_bg_color"], zoomControlBackground._appearance_mode)
        zoomControlBackground.setFill(zoomPanelColor)
        zoomControlBackground.setWidth(1)
        zoomControlBackground.draw(self.mainWindow)
        
        # Zoom in button
        zoomInButton = ModernButton(Point((self.halfWidth - zoomPanelX - zoomPanelPadding) - zoomButtonSize / 2, (self.halfDrawHeight - zoomPanelY - (zoomPanelHeight / 2) + (zoomPanelHeight / 3))), zoomButtonSize, zoomButtonSize, "+", action = self.zoomIn, backdropColor = zoomPanelColor)
        zoomInButton.draw(self.mainWindow)
        
        # Zoom out button
        zoomOutButton = ModernButton(Point((self.halfWidth - zoomPanelX - zoomPanelPadding) - zoomButtonSize / 2, self.halfDrawHeight - zoomPanelY - (zoomPanelHeight / 2)), zoomButtonSize, zoomButtonSize, "-", action = self.zoomOut, backdropColor = zoomPanelColor)
        zoomOutButton.draw(self.mainWindow)
        
        # Zoom back home button
        zoomHomeButton = ModernButton(Point((self.halfWidth - zoomPanelX - zoomPanelPadding) - zoomButtonSize / 2, (self.halfDrawHeight - zoomPanelY - (zoomPanelHeight / 2) - (zoomPanelHeight / 3))), zoomButtonSize, zoomButtonSize, "=", action = self.zoomHome, backdropColor = zoomPanelColor)
        zoomHomeButton.draw(self.mainWindow)
        
    ### Zoom behavior callbacks
    # Zoom in
    def zoomIn(self):
        # Multiply the scale value by 0.5 and set the text entry's text to this new value
        self.scale = self.scale * 0.5
        self.scaleEntry.setText(str(self.scale))
        
        # Redraw the graph with the new scale
        self.graph()
        
    # Zoom out
    def zoomOut(self):
        # Divide the scale value by 0.5 and set the text entry's text to this new value
        self.scale = self.scale / 0.5
        self.scaleEntry.setText(str(self.scale))
        
        # Redraw the graph with the new scale
        self.graph()
        
    # Zoom back home
    def zoomHome(self):
        # Set the scale value to 1 and set the text entry's text to this new value
        self.scale = 1
        self.scaleEntry.setText(str(self.scale))
        
        # Redraw the graph with the new scale
        self.graph()

    # Custom close behavior callback
    def close(self):
        self.mainWindow.close()
        self.safeExit = True
        exit()

    # Utils
    def hsvToRgb(self, h: float, s: float, v: float):
        t = tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h, s, v))
        return color_rgb(t[0], t[1], t[2])

    def localizeX(self, x) -> float:
        return x - self.halfWidth

    def localizeY(self, y) -> float:
        return self.halfHeight - y

    def lerp(self, a: float, b: float, t: float) -> float:
        """Linearly interpolate on the scale given by a to b, using t as the point on that scale.
        Examples
        --------
            50 == lerp(0, 100, 0.5)
            4.2 == lerp(1, 5, 0.8)
        """
        return (1.0 - t) * a + t * b

    def inverseLerp(self, a: float, b: float, f: float) -> float:
        """Inverse Linar Interpolation, get the fraction between a and b on which v resides.
        Examples
        --------
            0.5 == inv_lerp(0, 100, 50)
            0.8 == inv_lerp(1, 5, 4.2)
        """
        return (f - a) / (b - a)

    def remap(self, min1: float, max1: float, min2: float, max2: float, f: float) -> float:
        """Remap values from one linear scale to another, a combination of lerp and inv_lerp.
        i_min and i_max are the scale on which the original value resides,
        o_min and o_max are the scale to which it should be mapped.
        Examples
        --------
            45 == remap(0, 100, 40, 50, 50)
            6.2 == remap(1, 5, 3, 7, 4.2)
        """
        return self.lerp(min2, max2, self.inverseLerp(min1, max1, f))

if __name__ == "__main__":
    try:
        # Create the object and call its main method
        app = QuadraticExplorer()
        app.main()
    except:
        # If an error (not a safe exit) is encountered, then relaunch
        if not app.safeExit:
            print("Error encountered, relaunching!")
              
            os.system("python3 .\Programs\Class\QuadraticExplorer.py")
            exit()
