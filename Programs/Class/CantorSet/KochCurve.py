from math import *
from Lib.NewDEGraphics import *
from tkinter import Toplevel

class KochCurve:
    width = 1200
    height = 800
    canvasPercent = 0.666

    targetLevel = 5
    angle = 60
    rotation = 0
    drawSnowflake = False
    drawInsideOut = False
    polygonSides = 3
    levelBasedColoring = False
    
    colors = ['red', 'orange', 'yellow', 'green', 'blue', 'indigo', 'violet']
    
    currentPoints = []
    position = (0, 0)

    curvePolygons = []
    
    colorWidgets = []

    def __init__(self):
        self.win = DEGraphWin("Koch Curve", self.width, self.height, showScrollbar = False, debugMode = True)
                
        with self.win:
            with Flow(width = self.width, height = self.height):
                self.createDrawCanvas()
                
                Separator(1, self.height, 10, 0, (0, 0, 0))
                
                self.createControlPanel()
                
        self.win.update()
        self.win.mainloop()
    
    #region UI
    def createDrawCanvas(self):
        canvasWidth = self.width * self.canvasPercent
        
        self.canvas = Canvas(width = canvasWidth, height = self.height)
        # self.canvas.setInteractCallback(self.redrawCanvas)
        with self.canvas:
            # Create curve polygons
            for i in range(0, 10):
                self.curvePolygons.append(Polygon([(0, 0), (0, self.height), (canvasWidth, self.height)], color = 'red', outline = 'black', shouldPanZoom = True))
            
            self.drawKochCurve()
                
            # Create bottom left info panel
            infoPanelPadding = 33
            self.infoPanel = RoundedRectangle(infoPanelPadding, infoPanelPadding, 200, 100, 10, color = 'white', outline = 'black')
            self.infoPanel.draw()
            
            self.infoTitle = Label("Koch Curve Info", width = 21, justify = 'center', font = 'Arial 15 bold', bg = 'white')
            self.infoTitle.place(x = infoPanelPadding + 3, y = infoPanelPadding + 2)
            
            #region Info Labels
            self.perimeterLabelText = tk.StringVar(value = "Perimeter: ")
            self.perimeterLabel = Label(self.perimeterLabelText, justify = 'left', font = 'Arial 12', bg = 'white')
            Tooltip(self.perimeterLabel, "The perimeter of the Koch Curve")
            self.perimeterLabel.place(x = infoPanelPadding + 10, y = infoPanelPadding + 30)
            
            self.divisionsLabelText = tk.StringVar(value = "Divisions: ")
            self.divisionsLabel = Label(self.divisionsLabelText, justify = 'left', font = 'Arial 12', bg = 'white')
            Tooltip(self.divisionsLabel, "The number of times the Koch Curve is divided. This is equal to 4^targetLevel")
            self.divisionsLabel.place(x = infoPanelPadding + 10, y = infoPanelPadding + 50)
            #endregion
            
            # Reset view button
            self.resetViewButton = Button("Reset View", width = 60, command = self.resetView)
            Tooltip(self.resetViewButton, "Reset the view of the Koch Curve")
            self.resetViewButton.place(x = (self.width * self.canvasPercent) - 60, y = 20)
                    
    def createControlPanel(self):
        panelWidth = self.width * (1.0 - self.canvasPercent)
        itemWidth = panelWidth - 20
        
        with Stack(width = panelWidth, height = self.height):
            with HideableFrame(titleText = "Shape", width = panelWidth):            
                self.targetLevelSlider = Slider(0, 7, self.targetLevel, itemWidth, 30, 1, command = self.setTargetLevel, labelFont = "Arial 12 bold", labelText = "Target Level")
                Tooltip(self.targetLevelSlider, "The target level of the Koch Curve. Purposefully capped at 7 to prevent the program from slowing down too much.")
                
                self.angleSlider = SliderWithTextInput(0, 90, self.angle, itemWidth, 30, 1, self.setAngle, labelFont = "Arial 12 bold", labelText = "Inclination Angle", labelWidth = 100)
                Tooltip(self.angleSlider, "The incination angle of the Koch Curve")
                
                self.rotationSlider = SliderWithTextInput(0, 360, self.rotation, itemWidth, 30, 1, self.setRotation, labelFont = "Arial 12 bold", labelText = "Rotation Angle", labelWidth = 100)
                Tooltip(self.rotationSlider, "The rotation angle of the Koch Curve. Rotates the entire Koch Curve")

            with HideableFrame(titleText = "Appearance", width = panelWidth):
                self.drawSnowflakeToggle = CheckBox(text = "Draw Koch Snowflake", checked = self.drawSnowflake, command = self.setDrawSnowflake)
                Tooltip(self.drawSnowflakeToggle, "Draw the Koch Snowflake instead of the Koch Curve")
                
                self.drawInsideOutToggle = CheckBox(text = "Draw Inside Out", checked = self.drawInsideOut, command = self.setDrawInsideOut)
                Tooltip(self.drawInsideOutToggle, "Draw the Koch Snowflake inside out (cool looking)")
                self.drawInsideOutToggle.disable()
                
                self.polygonSidesSlider = Slider(3, 10, self.polygonSides, itemWidth, 30, 1, command = self.setPolygonSides, labelFont = "Arial 12 bold", labelText = "Polygon Sides")
                Tooltip(self.polygonSidesSlider, "The number of sides of the polygon that the Koch Curve is drawn as")
                self.polygonSidesSlider.disable()

            with HideableFrame(titleText = "Colors", width = panelWidth):
                self.levelBasedColoringToggle = CheckBox(text = "Level-Based Coloring", checked = self.levelBasedColoring, command = self.setLevelBasedColoring)
                Tooltip(self.levelBasedColoringToggle, "Color each level of the Koch Curve a different color")
                
                with HideableFrame(titleText = "Edit Colors", width = panelWidth, depth = 1):
                    self.colorWidgets = []
                    
                    Label("TODO: MAKE THIS WORK", font = "Arial 12 bold")
                    
                    # a = (100, 25, 40)
                    # b = (35, 150, 200)
                    
                    # i = 0
                    # for color in self.colors:
                    #     i += 1
                    #     self.colorWidgets.append(ColorWidget("#" + str(i), (lerpColor(a, b, i / len(self.colors))), panelWidth, 50))
                
            with HideableFrame(titleText = "Effects", width = panelWidth):
                Label("TODO: MAKE THIS WORK", font = "Arial 12 bold")  
            
            with Flow():
                self.helpButton = Button("Help", width = 60, command = self.showHelp)
                Tooltip(self.helpButton, "Open the help window")
                
                name = Label("By: Alexander Irausquin-Petit", font = "Arial 12 bold")
                
                self.quitButton = Button(text = "Quit", color = (240, 75, 75), width = 60, height = 40, cornerRadius = 10, command = exit)
                Tooltip(self.quitButton, "Quit the program (duh)")
    #endregion
    
    #region Callbacks
    # Target level slider callback
    def setTargetLevel(self, value):
        self.targetLevel = self.targetLevelSlider.value
        
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
        self.polygonSides = self.polygonSidesSlider.getValue()
        
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
        self.rotation = self.rotationSlider.getValue()
        
        self.drawKochCurve()
    
    # Reset view callback
    def resetView(self):
        self.canvas.resetView()
    
    # Show help callback
    def showHelp(self):
        pass
    #endregion
    
    #region Calculation and Drawing
    # Draw Koch Curve
    def drawKochCurve(self):
        self.position = (0, 0)
        self.currentPoints = []
        self.calculateKochCurve(0, 1.0, self.targetLevel)
        
        totalLength = 0
        divisions = 0
        
        if self.drawSnowflake:
            self.endPt = (0, 0)
            
            currentRotation = 0
            
            # Sum up the total length of the curve
            for i in range(1, len(self.currentPoints)):
                totalLength += sqrt((self.currentPoints[i][0] - self.currentPoints[i - 1][0]) ** 2 + (self.currentPoints[i][1] - self.currentPoints[i - 1][1]) ** 2)
                
                divisions += 1
            
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
                self.curvePolygons[i].draw()

            for i in range(self.polygonSides, len(self.curvePolygons)):
                self.curvePolygons[i].setPoints([])
                self.curvePolygons[i].undraw()
        else:
            newPoints = []
            
            # Convert the points to canvas coordinates
            for i in range(len(self.currentPoints)):
                if i != 0:
                    totalLength += sqrt((self.currentPoints[i][0] - self.currentPoints[i - 1][0]) ** 2 + (self.currentPoints[i][1] - self.currentPoints[i - 1][1]) ** 2)
                    
                    divisions += 1
                
                newPoints.append(self.convertPoint(self.currentPoints[i]))
                newPoints[i] = self.rotatePoint(0, 0, self.rotation, *newPoints[i])
                newPoints[i] = (newPoints[i][0] + ((self.width * self.canvasPercent) / 4), self.height - newPoints[i][1] - (self.height / 2))
                
                
            # Convert the points into an actual polygon
            self.curvePolygons[0].setPoints(self.currentPoints)
            self.curvePolygons[0].draw()
            
            for i in range(1, len(self.curvePolygons)):
                self.curvePolygons[i].setPoints([])
                self.curvePolygons[i].undraw()

        try:
            # Move the polygons under all other objects on the draw canvas
            for i in range(len(self.curvePolygons)):
                if self.curvePolygons[i].isDrawn:
                    self.canvas.tag_lower(self.curvePolygons[i].id, self.infoPanel.id)
            
            self.infoPanel.draw()
        except:
            pass
        
        self.divisionsLabelText.set("Divisions: " + str(divisions))
        self.lengthLabelText.set("Length: " + self.calculateUnit(totalLength))        
    
    # Recursively calculate Koch Curve
    def calculateKochCurve(self, currentAngle, length, level):
        if level == 0:
            newPt = self.projectPosition(currentAngle, length)
            self.currentPoints.extend([self.position, newPt])
            self.position = newPt
        else:
            scaleFactor = 1.0 / (2.0 * (1.0 + cos(radians(self.angle))))
            
            self.calculateKochCurve(currentAngle, length * scaleFactor, level - 1)
            self.calculateKochCurve(currentAngle + self.angle, length * scaleFactor, level - 1)
            self.calculateKochCurve(currentAngle - self.angle, length * scaleFactor, level - 1)
            self.calculateKochCurve(currentAngle, length * scaleFactor, level - 1)    

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