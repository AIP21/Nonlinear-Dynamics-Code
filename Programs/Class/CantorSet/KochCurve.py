from math import *
from Lib.NewDEGraphics import *

class KochCurve:
    width = 600
    height = 600

    targetLevel = 4
    angle = 60
    
    currentPoints = []
    position = (0, 0)

    def __init__(self):
        self.win = DEGraphWin("Koch Curve", self.width, self.height, showScrollbar = False)
        
        with self.win:
            self.stack = Stack()
            with self.stack:
                self.targetLevelSlider = Slider(0, 10, self.targetLevel, self.width, 30, 1)
                self.targetLevelSlider.setInputCallback(self.setTargetLevel)
                
                self.angleSlider = SliderWithTextInput(0, 90, self.angle, self.width, 30, 1, self.setAngle, labelText = "Angle: ")
                
                self.canvas = Canvas(width = self.width, height = self.height)
                with self.canvas:
                    # Draw base line
                    self.line = Line(0, self.height, self.width, self.height, 'black')
                    self.line.draw()
                    
                    # Create curve polygon
                    self.curvePolygon = Polygon([(0, 0), (0, self.height), (self.width, self.height)], 'red', outline = 'black')
                    self.drawKochCurve()
        
        self.win.update()
        self.win.mainloop()

    # Draw Koch Curve
    def drawKochCurve(self):
        self.position = (0, 0)
        self.currentPoints = []
        self.calculateKochCurve(0, 1.0, self.targetLevel)
        
        # Convert the points to canvas coordinates
        for i in range(len(self.currentPoints)):
            self.currentPoints[i] = self.convertPoint(self.currentPoints[i])
        
        # Convert the points into an actual polygon
        self.curvePolygon.setPoints(self.currentPoints)
        self.curvePolygon.draw()
    
    # Recursively calculate Koch Curve
    def calculateKochCurve(self, currentAngle, length, level):
        if level == 0:
            newPt = self.projectPoint(currentAngle, length)
            self.currentPoints.extend([self.position, newPt])
            self.position = newPt
        else:
            scaleFactor = 1.0 / (2.0 * (1.0 + cos(radians(self.angle))))
            
            self.calculateKochCurve(currentAngle, length * scaleFactor, level - 1)
            self.calculateKochCurve(currentAngle + self.angle, length * scaleFactor, level - 1)
            self.calculateKochCurve(currentAngle - self.angle, length * scaleFactor, level - 1)
            self.calculateKochCurve(currentAngle, length * scaleFactor, level - 1)    

    def projectPoint(self, directionAngle, length):
        xPt = self.position[0] + length * cos(radians(directionAngle))
        yPt = self.position[1] + length * sin(radians(directionAngle))
        
        return (xPt, yPt)

    # Target level slider callback
    def setTargetLevel(self, value):
        self.targetLevel = self.targetLevelSlider.value
        
        self.drawKochCurve()
    
    # Angle callback
    def setAngle(self, value):
        self.angle = float(value)
        
        self.drawKochCurve()
        
    # Convert point to canvas coordinates
    def convertPoint(self, point):
        x, y = point
        drawX = x * self.width
        drawY = (1 - y) * self.height
        
        return (drawX, drawY)

if __name__ == '__main__':
    KochCurve()