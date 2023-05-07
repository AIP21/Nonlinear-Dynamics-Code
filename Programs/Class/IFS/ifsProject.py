import random
from Lib.NewDEGraphics import *
from Lib.transform import *

class IFSExplorer:
    WIDTH = 800
    HEIGHT = 400
    PLOT_SIZE = WIDTH // 2

    pixels = []

    point = (random.random() * 10000000.0, random.random() * 10000000.0)

    transforms = []
    transforms.append(IFS_Transform(xScale = 0.5, yScale = 0.5,
                                    theta = 0.0, phi = 0.0,
                                    h = 0.0, k = 0.0,
                                    p = 1, c = 'red'))
    transforms.append(IFS_Transform(xScale = 0.5, yScale = 0.5,
                                    theta = 0.0, phi = 0.0,
                                    h = 0.5, k = 0.0,
                                    p = 1, c = 'blue'))
    transforms.append(IFS_Transform(xScale = 0.5, yScale = 0.5,
                                    theta = 0.0, phi = 0.0,
                                    h = 0.0, k = 0.5, # h = 0.25 ???
                                    p = 1, c = 'green'))

    minX = 10000000
    maxX = -10000000
    minY = 10000000
    maxY = -10000000
    
    drawPadding = [10, 10]
    
    def __init__(self):
        win = DEGraphWin("IFS Explorer", self.WIDTH, self.HEIGHT)

        # Initialize the pixels array
        for x in range(self.PLOT_SIZE):
            col = []
            
            for y in range(self.HEIGHT):
                col.append('white')
            
            self.pixels.append(col)
        
        # UI stuff
        with win:
            with Flow():
                
                # Create the canvas and plot for drawing the IFS                
                with Canvas(width = self.PLOT_SIZE):
                    self.plot = Plot(self.PLOT_SIZE, self.PLOT_SIZE, self.PLOT_SIZE, self.PLOT_SIZE)
                    
                    # Plot the IFS
                    self.plotIFS()
                
                # Create the GUI
                self.createControlPanel()
    
    # Create the control panel
    def createControlPanel(self):
        with Stack(bg = 'blue'):
            Label("Controls")
            
            # for i in range(len(self.transforms)):
            #     self.

    def plotIFS(self):
        for i in range(100000):
                self.iterate(False)
            
        print("MinX: " + str(self.minX))
        print("MaxX: " + str(self.maxX))
        print("MinY: " + str(self.minY))
        print("MaxY: " + str(self.maxY))
        
        for i in range(10000):
            self.iterate(True)
        
        print("Done iterating")
        
        self.plot.plotBulk(0, 0, self.pixels)

    # Iterate the IFS system
    def iterate(self, shouldPlot):
        # Choose a random transformation for this iteration
        randTransform = self.transforms[random.randint(0, len(self.transforms) - 1)]
        
        # Transform the current point and keep it as a new point
        newPt = randTransform.transformPoint(self.point[0], self.point[1])
        
        # Should we plot this point by adding it to the pixels array?
        if shouldPlot: 
            # Remap the new point to be within the screen
            remappedPt = self.remapPoint(newPt)

            # Set the pixel at this screen position to the color of the transformation
            self.pixels[remappedPt[0]][remappedPt[1]] = randTransform.color
        else: # If not, just update the min/max values
            if newPt[0] < self.minX:
                self.minX = newPt[0]
            if newPt[0] > self.maxX:
                self.maxX = newPt[0]
            if newPt[1] < self.minY:
                self.minY = newPt[1]
            if newPt[1] > self.maxY:
                self.maxY = newPt[1]
        
        # Updat the current point
        self.point = newPt
    
    # Remap the point to stay within the screen size and within the border padding
    def remapPoint(self, point):
        return (int(lerp(self.drawPadding[0], self.PLOT_SIZE - self.drawPadding[0], point[0])), self.PLOT_SIZE - 1 - int(lerp(self.drawPadding[0], self.PLOT_SIZE - self.drawPadding[0], point[1])))

#region Utils
def remap(value, low1, high1, low2, high2):
    return low2 + (value - low1) * (high2 - low2) / (high1 - low1)

def lerp(a, b, t):
    return a + (b - a) * t
#endregion 

if __name__ == "__main__":
    IFSExplorer()