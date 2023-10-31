from math import *
import os
import random
from Lib.NewDEGraphics import *
from tkinter import Toplevel

class KochCurve:
    width = 1200
    height = 800
    canvasPercent = 0.6

    targetLevel = 5
    angle = 60
    rotation = 0
    drawSnowflake = False
    drawInsideOut = False
    polygonSides = 3
    levelBasedColoring = False
    curveBias = 0.0
    randomness = 0.0
    
    colors = ['red', 'orange', 'yellow', 'green', 'blue', 'indigo', 'violet', 'pink', 'brown', 'cyan']
    
    currentPoints = []
    position = (0, 0)

    curvePolygons = []
    
    colorWidgets = []
    
    lines = ""

    def __init__(self):
        # import ctypes
 
        # ctypes.windll.shcore.SetProcessDpiAwareness(1)
        
        self.win = DEGraphWin("Koch Curve", self.width, self.height, showScrollbar = False, debugMode = True)
        # self.win.call('tk', 'scaling', 2)
        
        # Check if its the first time running the program
        self.firstTime = False
        if not os.path.exists("KochCurveData DO NOT OPEN (just kidding you can open it if you want to).txt"):
            self.firstTime = True
        
        # Create the file
        with open("KochCurveData DO NOT OPEN (just kidding you can open it if you want to).txt", "w") as f:
            f.write("THIS IS JUST A PLACEHOLDER FILE! I put the bee movie script in it because funny. This is simply a way for the program to tell if it's the first time running it.\n ... \n")
            
            try:
                import urllib.request  # The library that handles the url stuff

                # This code just fetched the bee movie script from GitHub and puts it in the file (I needed to fill the file with something)
                targetURL = "https://gist.githubusercontent.com/MattIPv4/045239bc27b16b2bcf7a3a9a4648c08a/raw/2411e31293a35f3e565f61e7490a806d4720ea7e/bee%2520movie%2520script"
                for line in urllib.request.urlopen(targetURL):
                    lineStr = line.decode('utf-8')
                    
                    if len(self.lines) < 6000:
                        self.lines += lineStr
                    
                    f.write(lineStr)
            except:
                pass
            
            f.close()
                        
        with self.win:
            with Flow(width = self.width, height = self.height):
                self.createDrawCanvas()
                
                Separator(1, self.height, 10, 0, (0, 0, 0))
                
                self.createControlPanel()
            
            if self.firstTime:
                self.showHelp()
            
            self.temp = tk.Toplevel(self.win)
            self.temp.geometry("0x0+0+0")
            self.temp.overrideredirect(True)

        # self.win.update()
        # self.win.mainloop()
    
    #region UI
    def createDrawCanvas(self):
        canvasWidth = self.width * self.canvasPercent
        
        self.canvas = Canvas(width = canvasWidth, height = self.height, bg = colorRGB(200, 200, 200))
        self.canvas.setInteractionCallback(self.check)
        with self.canvas:
            # Create curve polygons
            for i in range(0, 10):
                self.curvePolygons.append(Polygon([(0, 0), (0, self.height), (canvasWidth, self.height)], color = 'red', outline = 'black', shouldPanZoom = True))
            
            #region Create bottom left info panel
            infoPanelPadding = 33
            self.infoPanel = RoundedRectangle(infoPanelPadding, infoPanelPadding, 200, 80, 10, color = 'white', outline = 'black')
            self.infoPanel.draw()
            
            self.infoTitle = Label("Koch Curve Info", width = 18, justify = 'center', font = 'Arial 13 bold', bg = 'white')
            self.infoTitle.place(x = infoPanelPadding + 7.5, y = infoPanelPadding + 2)
            
            # Info Labels
            self.perimeterLabelText = tk.StringVar(value = "Perimeter: ")
            perimeterLabel = Label(self.perimeterLabelText, justify = 'left', font = 'Arial 12', bg = 'white')
            Tooltip(perimeterLabel, "The perimeter of the Koch Curve. This is equal to (4/3)^targetLevel")
            perimeterLabel.place(x = infoPanelPadding + 10, y = infoPanelPadding + 30)
            
            self.segmentsLabelText = tk.StringVar(value = "Segments: ")
            segmentsLabel = Label(self.segmentsLabelText, justify = 'left', font = 'Arial 12', bg = 'white')
            Tooltip(segmentsLabel, "The number of times the Koch Curve is divided. This is equal to 4^targetLevel")
            segmentsLabel.place(x = infoPanelPadding + 10, y = infoPanelPadding + 50)
            #endregion
            
            # ???
            self.boundingBox = (self.width * self.canvasPercent + 750, self.height - 1000, 1000, 20000)
            self.mysteriousLabel = Text(*self.boundingBox, justify = 'left', text = self.lines, shouldPanZoom = True)
                        
            self.drawKochCurve()
            
            # Reset view button
            self.resetViewButton = Button("Reset View", width = 100, color = (240, 240, 100), backgroundColor = (200, 200, 200), command = self.resetView)
            Tooltip(self.resetViewButton, "Reset the view of the Koch Curve")
            self.resetViewButton.place(x = (self.width * self.canvasPercent) - 120, y = 20)
            
    def createControlPanel(self):
        panelWidth = self.width * (1.0 - self.canvasPercent)
        itemWidth = panelWidth - 20
        
        with Stack(width = panelWidth, height = self.height):
            self.shapeFrame = HideableFrame(titleText = "Shape", width = panelWidth)
            with self.shapeFrame:
                self.targetLevelSlider = SliderWithTextInput(0, 7, self.targetLevel, itemWidth, 30, 1, command = self.setTargetLevel, labelFont = "Arial 12 bold", labelText = "Desired Level")
                Tooltip(self.targetLevelSlider, "The desired level to draw the Koch Curve to. Purposefully capped at 7 to prevent the program from slowing down too much.")
                
                self.angleSlider = SliderWithTextInput(0, 90, self.angle, itemWidth, 30, 1, self.setAngle, labelFont = "Arial 12 bold", labelText = "Inclination Angle", labelWidth = 150)
                Tooltip(self.angleSlider, "The incination angle of the Koch Curve")
                
                self.rotationSlider = SliderWithTextInput(0, 360, self.rotation, itemWidth, 30, 1, self.setRotation, labelFont = "Arial 12 bold", labelText = "Rotation Angle", labelWidth = 100)
                Tooltip(self.rotationSlider, "The rotation angle of the Koch Curve. Rotates the entire Koch Curve")

            self.appearanceFrame = HideableFrame(titleText = "Appearance", width = panelWidth)
            with self.appearanceFrame:
                self.drawSnowflakeToggle = CheckBox(text = "Draw Koch Snowflake", checked = self.drawSnowflake, command = self.setDrawSnowflake)
                Tooltip(self.drawSnowflakeToggle, "Draw the Koch Snowflake instead of the Koch Curve")
                
                self.drawInsideOutToggle = CheckBox(text = "Draw Inside Out", checked = self.drawInsideOut, command = self.setDrawInsideOut)
                Tooltip(self.drawInsideOutToggle, "Draw the Koch Snowflake inside out (cool looking)")
                self.drawInsideOutToggle.disable()
                
                self.polygonSidesSlider = Slider(3, 10, self.polygonSides, itemWidth, 30, 1, command = self.setPolygonSides, labelFont = "Arial 12 bold", labelText = "Snowflake Sides", labelWidth = 150)
                Tooltip(self.polygonSidesSlider, "The number of sides of the polygon that the Koch Curve is drawn as")
                self.polygonSidesSlider.disable()

            self.colorFrame = HideableFrame(titleText = "Colors", width = panelWidth)
            with self.colorFrame:
                # self.levelBasedColoringToggle = CheckBox(text = "Level-Based Coloring", checked = self.levelBasedColoring, command = self.setLevelBasedColoring)
                # Tooltip(self.levelBasedColoringToggle, "Color each level of the Koch Curve a different color")
                
                # self.colorWidget = ColorWidget("Edit Draw Color", colorToRGB(self.colors[0]), self.colorChanged, panelWidth - 30, 30)
                
                self.colorWidgets = []
                                    
                a = (100, 25, 40)
                b = (35, 150, 200)
                
                i = 0
                for color in self.colors:
                    i += 1
                    self.colorWidgets.append(ColorWidget(str(i), colorToRGB(color), self.colorChanged, "Edit color for polygon ", panelWidth - 30, 30)) # (lerpColor(a, b, i / len(self.colors)))
            
            self.effectsFrame = HideableFrame(titleText = "Effects", width = panelWidth)
            with self.effectsFrame:
                self.curveBiasSlider = SliderWithTextInput(0, 1, self.curveBias, itemWidth, 30, 0, command = self.setCurveBias, labelFont = "Arial 12 bold", labelText = "Curve Bias", labelWidth = 100)
                Tooltip(self.curveBiasSlider, "The bias of the Koch Curve. The larger it is the more curved the Koch Curve is")
                
                self.randomnessSlider = SliderWithTextInput(0, 1, self.randomness, itemWidth, 30, 0, command = self.setRandomness, labelFont = "Arial 12 bold", labelText = "Randomness", labelWidth = 100)
                Tooltip(self.randomnessSlider, "Adds some randomness to the Koch Curve")
            
            with Flow(width = panelWidth):
                self.helpButton = Button("Help", color = (75, 150, 75), width = panelWidth * 0.25, command = self.showHelp)
                Tooltip(self.helpButton, "Open the help window")
                
                # Separator
                with Flow(width = panelWidth * 0.433):
                    pass
                
                self.quitButton = Button(text = "Quit", color = (240, 75, 75), width = panelWidth * 0.25, command = self.win.close)
                Tooltip(self.quitButton, "Quit the program (duh)")
    
    # Show a help window with info about the program
    def showHelp(self):
        print("Showing help")
        
        helpBoxes = [
                     ("Welcome to Koch Curve Explorer by Alexander IP! This tour will show you around the program and teach you about the incredible things you can do with it.", self.win, (self.width / 2 - 150, self.height / 2 - 75)),
                     ("If you would like to access this tour again, click this button.", self.helpButton, (-200, 50)),
                     ("If you want to quit the program, click this button.", self.quitButton, (-200, 50)),
                     ("This is the main canvas. Here you will see the Koch Curve and Koch Snowflake. Click and drag to pan the view and scroll to zoom in and out.", self.canvas, ((self.width * self.canvasPercent) / 2 - 150, self.height / 2 - 75)),
                     ("If you ever get lost, just hit this button to recenter your view.", self.resetViewButton, (-200, 50)),
                     ("This panel shows you some information about the currently drawn Koch Curve. Note that it only shows information for one curve, so when drawing a Snowflake it will only show the information for the first curve.", self.infoTitle, (0, 100)),
                     ("This section contain the controls for the shape of the Koch Curve. Click on it to hide it.", self.shapeFrame, (-200, 25)),
                     ("This slider controls the desired level to draw the Koch Curve to. NOTE: All sliders in this program can be controlled by dragging or with the scroll wheel. Some sliders also have text boxes to manually input precise values. (This allows you to go out of the limits of the slider!)", self.targetLevelSlider, (-200, 25)),
                     ("This slider controls the generating angle of the Koch Curve. This is an important slider!", self.angleSlider, (-200, 25)),
                     ("This slider will rotate the entire Koch Curve. This is a less important slider.", self.rotationSlider, (-200, 25)),
                     ("This section contains the controls for the appearance of the Koch Curve. Click on it to hide it.", self.appearanceFrame, (-200, 25)),
                     ("This toggles drawing the Koch Snowflake (a shape made of Koch Curves).", self.drawSnowflakeToggle, (-200, 25)),
                     ("This toggles drawing the Koch Snowflake inside out. It's a pretty cool effect!", self.drawInsideOutToggle, (-200, 25)),
                     ("This slider controls the number of sides that the Koch Snowflake should have.", self.polygonSidesSlider, (-200, 25)),
                     ("This section allows you to change the colors of the Koch Curve and the color of each part of the Koch Snowflake.", self.colorFrame, (-200, -100)),
                    #  ("This toggles coloring polygons based on their level.", self.levelBasedColoringToggle, (-200, 25)),
                    #  ("This is the color of the Koch Curve/Snowflake. Click on it to select a new color.", self.colorWidget, (-200, 25)),
                    #  ("This sub section allows you to change the colors of the Koch Curve.", self.editColorsFrame, (-200, -100)),
                     ("This section contains the controls for the funky effects you can apply to the Koch Curve.", self.effectsFrame, (-200, 25)),
                     ("This slider controls the curve bias. It makes the Koch Curve curl up!", self.curveBiasSlider, (-200, 25)),
                     ("This slider controls the curve randomness. It really messes up the curve...", self.randomnessSlider, (-200, 25)),
                     ("That the end of the tour! If you need to access this tour again, press the green 'help' button on the bottom right corner of the program.", self.win, (self.width / 2 - 150, self.height / 2 - 75))
                     ]
        
        # If a help box is already being shown, then hide it
        try:
            if self.helpBox != None:
                self.helpBox.hide()
                
                # Un-highlight the currently targeted widget (excluding the welcome box)
                if self.helpBoxIndex >= 1:
                    # Check target widget type
                    if isinstance(helpBoxes[self.helpBoxIndex][1], HideableFrame):
                        helpBoxes[self.helpBoxIndex][1].showHideButton.config(highlightthickness = 0)
                    else:
                        helpBoxes[self.helpBoxIndex][1].config(highlightthickness = 0)
        except:
            pass
        
        self.helpBoxIndex = -1
        self.helpBox = None
        
        # Show next help box 
        def nextHelpBox():
            # Un-highlight the last targeted widget (excluding the welcome box)
            if self.helpBoxIndex >= 1:
                # Check target widget type
                if isinstance(helpBoxes[self.helpBoxIndex][1], HideableFrame):
                    helpBoxes[self.helpBoxIndex][1].showHideButton.config(highlightthickness = 0)
                else:
                    helpBoxes[self.helpBoxIndex][1].config(highlightthickness = 0)
            
            # Make sure we still have help boxes to show. If we're done, then destroy the last one
            if self.helpBoxIndex >= len(helpBoxes) - 1:
                self.helpBox.hide()
                return
        
            self.helpBoxIndex += 1
            
            print("Showing help box #" + str(self.helpBoxIndex))
            
            # Destroy old help box
            if self.helpBox != None:
                self.helpBox.hide()
            
            data = helpBoxes[self.helpBoxIndex]
            
            # Highlight the targeted widget (excluding the welcome box)
            if self.helpBoxIndex >= 1:
                # Check target widget type
                if isinstance(data[1], HideableFrame):
                    data[1].showHideButton.config(highlightbackground = "blue")
                    data[1].showHideButton.config(highlightthickness = 2)
                else:
                    data[1].config(highlightbackground = "blue")
                    data[1].config(highlightthickness = 2)
            
            # Next button text
            if self.helpBoxIndex >= len(helpBoxes) - 1:
                self.temp.destroy()
                nextText = "Done"
            else:
                nextText = "Next"
            
            # Create a popup with the text and position it next to the widget with the desired offset
            self.helpBox = Popup(data[1], text = data[0], closeButtonText = nextText, xOffset = data[2][0], yOffset = data[2][1])
            self.helpBox.show()
            self.helpBox.registerCloseCommand(nextHelpBox)
        
        nextHelpBox()
    #endregion
    
    #region Callbacks
    # Target level slider callback
    def setTargetLevel(self, value):
        self.targetLevel = int(value)
        
        self.drawKochCurve()
    
    # Angle callback
    def setAngle(self, value):
        self.angle = float(value)
        
        self.drawKochCurve()
        
    # Draw Koch Snowflake callback
    def setDrawSnowflake(self, value):
        self.drawSnowflake = value
        
        if self.drawSnowflake:
            self.polygonSidesSlider.enable()
            self.drawInsideOutToggle.enable()
        else:
            self.polygonSidesSlider.disable()
            self.drawInsideOutToggle.disable()
        
        self.drawKochCurve()
    
    # Draw Inside Out callback
    def setDrawInsideOut(self, value):
        self.drawInsideOut = value
        
        self.drawKochCurve()
    
    # Polygon sides callback
    def setPolygonSides(self, value):
        self.polygonSides = int(value)
        
        self.drawKochCurve()
    
    # Level-based coloring callback
    def setLevelBasedColoring(self, value):
        self.levelBasedColoring = value
        
        self.drawKochCurve()
        
    # Set colors callback
    def setColors(self, colors):
        self.colors = colors
        
        self.drawKochCurve()
        
    # Set rotation callback
    def setRotation(self, value):
        self.rotation = float(value)
        
        self.drawKochCurve()
    
    # Reset view callback
    def resetView(self):
        self.canvas.resetView()
   
    # Color changed callback
    def colorChanged(self, name, color):
        self.colors[int(name) - 1] = colorRGB(*color)
                
        self.drawKochCurve()
    
    # Curve bias callback
    def setCurveBias(self, value):
        self.curveBias = float(value)
        
        self.drawKochCurve()
        
    # Randomness callback
    def setRandomness(self, value):
        self.randomness = float(value)
        
        self.drawKochCurve()
    
    # ooooh spooky scary function
    def check(self):
        # Check if the bounding box of the mysterious text is visible with the canvas zoom and pan
        if self.canvas.isBoundingBoxVisible(*self.boundingBox):
            self.mysteriousLabel.draw()
            
            print("You found the secret!")
        else:
            # self.mysteriousLabel.undraw()
            self.canvas.delete(self.mysteriousLabel.id)
    #endregion
    
    #region Calculation and Drawing
    # Draw Koch Curve
    def drawKochCurve(self):
        self.position = (0, 0)
        self.currentPoints = []
        self.calculateKochCurve(self.rotation, 1.0, min(7, self.targetLevel))
        
        totalLength = 0
        segments = 0
        
        # Undraw all the old Koch Curve polygons
        for i in range(0, len(self.curvePolygons)):
            self.curvePolygons[i].color = self.colors[min(len(self.colors) - 1, i)]
            self.curvePolygons[i].setPoints([])
            self.curvePolygons[i].undraw()
            self.canvas.delete(self.curvePolygons[i].id)
        
        # Draw the new Koch Curve polygons
        if self.drawSnowflake:
            self.endPt = (0, 0)
            
            currentRotation = self.rotation
            
            # Sum up the total length of the curve
            for i in range(1, len(self.currentPoints)):
                totalLength += sqrt((self.currentPoints[i][0] - self.currentPoints[i - 1][0]) ** 2 + (self.currentPoints[i][1] - self.currentPoints[i - 1][1]) ** 2)
                
                segments += 1
            
            for i in range(self.polygonSides):
                # Rotate every point around the last end point
                if i != 0:
                    rot = 360 / self.polygonSides
                    rot *= 1 if self.drawInsideOut else -1
                    
                    for j in range(len(self.currentPoints)):
                        pt = self.projectPoint(self.currentPoints[j], currentRotation, 1)
                        pt = self.rotatePoint(*self.endPt, rot, *pt)

                        self.currentPoints[j] = pt
                    
                    currentRotation += rot
                
                self.endPt = self.currentPoints[len(self.currentPoints) - 1]
                
                polyPoints = []
                for j in range(len(self.currentPoints)):
                    pt = self.convertPoint(self.currentPoints[j])
                    polyPoints.append((pt[0] + ((self.width * self.canvasPercent) / 4), self.height - pt[1] - (self.height / 2)))
            
                self.curvePolygons[i].setPoints(polyPoints)
                self.curvePolygons[i].setColor(self.colors[i % len(self.colors)])
                self.canvas.addDrawn(self.curvePolygons[i])
                
                # Move the polygons under all other objects on the draw canvas
                try:
                    self.canvas.tag_lower(self.curvePolygons[i].id, self.infoPanel.id)
                except:
                    pass
        else:
            newPoints = []
            
            # Convert the points to canvas coordinates
            for i in range(len(self.currentPoints)):
                if i != 0:
                    totalLength += sqrt((self.currentPoints[i][0] - self.currentPoints[i - 1][0]) ** 2 + (self.currentPoints[i][1] - self.currentPoints[i - 1][1]) ** 2)
                    
                    segments += 1
                
                newPoints.append(self.convertPoint(self.currentPoints[i]))
                # newPoints[i] = self.rotatePoint(0, 0, self.rotation, *newPoints[i])
                newPoints[i] = (newPoints[i][0] + ((self.width * self.canvasPercent) / 4), self.height - newPoints[i][1] - (self.height / 2))
                
            # Convert the converted points into an actual polygon
            self.curvePolygons[0].setPoints(newPoints)
            self.canvas.addDrawn(self.curvePolygons[0])
            
            # Move the polygons under all other objects on the draw canvas
            try:
                self.canvas.tag_lower(self.curvePolygons[0].id, self.infoPanel.id)
            except:
                pass

        # Draw the info panel to keep it above the Koch Curve polygons
        self.infoPanel.draw()
        
        # Set the info text labels
        self.segmentsLabelText.set("Segments: " + str(segments))
        self.perimeterLabelText.set("Perimeter: " + self.calculateUnit((4.0 / 3.0) ** self.targetLevel))
        
        self.canvas.updateInteractibleDrawn()
            
    # Recursively calculate Koch Curve
    def calculateKochCurve(self, currentAngle, length, level):
        if level == 0:
            newPt = self.projectPosition(currentAngle, length)
            self.currentPoints.extend([self.position, newPt])
            self.position = newPt
        else:
            scaleFactor = 1.0 / (2.0 * (1.0 + cos(radians(self.angle)))) * (1.0 + (self.randomness * (random.random() - 0.5)))
            
            # The curve bias makes it curl up
            angleBias = self.curveBias * (1.0 - (length / (2.0 ** self.targetLevel))) * 100
            
            self.calculateKochCurve(currentAngle, length * scaleFactor, level - 1)
            self.calculateKochCurve(currentAngle + self.angle + angleBias * self.curveBias,  length * scaleFactor, level - 1)
            self.calculateKochCurve(currentAngle - self.angle + angleBias, length * scaleFactor, level - 1)
            self.calculateKochCurve(currentAngle, length * scaleFactor , level - 1)    

    # Project the current position in a given direction and length
    def projectPosition(self, directionAngle, length):
        xPt = self.position[0] + length * cos(radians(directionAngle))
        yPt = self.position[1] + length * sin(radians(directionAngle))
        
        return (xPt, yPt)
    
    # Project a point in a given direction and length
    def projectPoint(self, point, directionAngle, length):
        xPt = point[0] + length * cos(radians(directionAngle))
        yPt = point[1] + length * sin(radians(directionAngle))
        
        return (xPt, yPt)
    
    # Convert point to canvas coordinates
    def convertPoint(self, point):
        x, y = point
        drawX = x * self.width * self.canvasPercent * 0.5
        drawY = y * self.height * 0.5
        
        return (drawX, drawY)
    
    # Rotate a point around another point
    def rotatePoint(self, centerX, centerY, angle, toRotateX, toRotateY):
        s = sin(radians(angle))
        c = cos(radians(angle))

        # Translate point back to origin:
        toRotateX -= centerX
        toRotateY -= centerY

        # Rotate point
        newX = toRotateX * c - toRotateY * s
        newY = toRotateX * s + toRotateY * c

        # Translate point back:
        toRotateX = newX + centerX
        toRotateY = newY + centerY
        
        return (toRotateX, toRotateY)
    
    # Raise lised objects above the Koch Curve polygons
    def raiseObjectsAboveCurve(self, canvas, **objects):
        for i in range(len(objects)):
            for j in range(len(self.curvePolygons)):
                canvas.tag_raise(objects[i], self.curvePolygons[j].polygon)
    
    # Calculate a real world unit for a given length
    def calculateUnit(self, length):
        if length < 12:
            return str(round(length, 2)) + " inches"
        elif length < 45 * 12:
            return str(round(length / 12, 2)) + " feet"
        elif length < 160 * 12:
            return str(round(length / (45 * 12), 2)) + " school buses"
        elif length < 5280 * 12:
            return str(round(length / (160 * 12), 2)) + " football fields"
        elif length < 5280 * 12 * 13.4:
            return str(round(length / (5280 * 12), 2)) + " miles"
        elif length < 5280 * 12 * 2802:
            return str(round(length / (5280 * 12 * 13.4), 2)) + " manhattans"
        elif length < 5280 * 12 * 3958.8:
            return str(round(length / (5280 * 12 * 2802), 2)) + " united states"
        elif length < 5280 * 12 * 5764:
            return str(round(length / (5280 * 12 * 3958.8), 2)) + " earths"
        elif length < 5280 * 12 * 865370:
            return str(round(length / (5280 * 12 * 5764), 2)) + " jupiters"
        elif length < 5280 * 12 * 9090000000:
            return str(round(length / (5280 * 12 * 865370), 2)) + " suns"
        elif length < 5280 * 12 * 6.213707e+17:
            return str(round(length / (5280 * 12 * 9090000000), 2)) + " solar systems"
        elif length < 5280 * 12 * 1.5e+21:
            return str(round(length / (5280 * 12 * 6.213707e+17), 2)) + " milky ways"
        elif length < 5280 * 12 * 1.4e+26:
            return str(round(length / (5280 * 12 * 1.5e+21), 2)) + " IP's brains"
        else:
            return str(round(length / (5280 * 12 * 1.4e+26), 2)) + " universes"
    #endregion

if __name__ == '__main__':
    KochCurve()