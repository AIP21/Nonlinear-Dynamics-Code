import random
from Lib.NewDEGraphics import *
from Lib.transform import *
from Lib.playsound import playsound
from tkinter.font import Font
import os

class IFSExplorer:
    PLAY_SOUNDS = True
    
    UI_IMAGES = {}
    UI_SOUNDS = {}
    
    WIDTH = 600
    HEIGHT = 750
    
    PLOT_SIZE = 600
    
    transforms = []
    pixelFont = None
    
    initialTransforms = []
    initialTransforms.append(IFS_Transform(xScale = 0.5, yScale = 0.5,
                                    theta = 0.0, phi = 0.0,
                                    h = 0.0, k = 0.0,
                                    p = 1, c = (255, 0, 0)))
    # initialTransforms.append(IFS_Transform(xScale = 0.5, yScale = 0.5,
    #                                 theta = 0.0, phi = 0.0,
    #                                 h = 0.5, k = 0.0,
    #                                 p = 1, c = (0, 255 ,0)))
    # initialTransforms.append(IFS_Transform(xScale = 0.5, yScale = 0.5,
    #                                 theta = 0.0, phi = 0.0,
    #                                 h = 0.0, k = 0.5, # h = 0.25 ???
    #                                 p = 1, c = (0, 0, 255)))
    
    pixels = []

    point = (random.random() * 10000000.0, random.random() * 10000000.0)

    minX = 10000000
    maxX = -10000000
    minY = 10000000
    maxY = -10000000
    
    drawPadding = [10, 10]
        
    def __init__(self):
        self.initImagesAndSounds(os.path.dirname(os.path.realpath(__file__)))
        
        self.win = DEGraphWin("IFS Explorer", self.WIDTH, self.HEIGHT, scale = 1) # 0.25
        
        # self.win.hideTitlebar()
        self.win.update_idletasks()
        
        self.pixelFont = Font(family = "Small Fonts", size = 70)
        
        self.initializePixels()
        
        # Create the Controls Window
        self.createControlsWindow()
        
        self.win.geometry("%dx%d" % (self.WIDTH + 1, self.HEIGHT + 1))
        self.win.update_idletasks()
        self.win.geometry("%dx%d" % (self.WIDTH - 1, self.HEIGHT - 1))
        self.win.update_idletasks()
        
        # UI stuff
        with self.win:
            with Stack():
                # Create the canvas and plot for drawing the IFS                
                with Canvas(width = self.PLOT_SIZE):
                    self.plot = Plot(self.WIDTH, self.HEIGHT - 150)
                
                # Create the IFS Config Panel
                self.createIFSControlPanel()
                
                # Plot the IFS
                self.plotIFS()
    
    #region GUI
    # Create the IFS Control Panel
    def createIFSControlPanel(self):
        with Flow():            
            with Stack(width = 15):
                newButton = ImageButton(self.getImage("button up"), self.getImage("button down"), width = 30, height = 30, command = self.newTransform, pressCommand = self.clickDown)
                
                removeButton = ImageButton(self.getImage("button up"), self.getImage("button down"), width = 30, height = 30, command = self.newTransform, pressCommand = self.clickDown)

                saveButton = ImageButton(self.getImage("button up"), self.getImage("button down"), width = 30, height = 30, command = self.newTransform, pressCommand = self.clickDown)
                
                loadButton = ImageButton(self.getImage("button up"), self.getImage("button down"), width = 30, height = 30, command = self.newTransform, pressCommand = self.clickDown)
                
                clearButton = ImageButton(self.getImage("button up"), self.getImage("button down"), width = 30, height = 30, command = self.newTransform, pressCommand = self.clickDown)
            
            separator = Separator(width = 1, height = 100, horizontalSpacing = 5, verticalSpacing = 0)
            
            self.transformsScrollArea = HorizontalScrollView(width = self.WIDTH - 15)
            with self.transformsScrollArea:
                for i in range(len(self.initialTransforms)):
                    self.transforms.append(TransformGUI(i, self.initialTransforms[i], self.plotIFS))
    
    # Create the controls window
    def createControlsWindow(self):
        pass
        # with Stack(bg = 'green'):
        #     # Label("Controls", font = self.pixelFont)
            
        #     # ButtonImage(image = self.getImage("power button up"), pressedImage = self.getImage("power button down"), width = 40, height = 40, command = self.quit)
        
        #     Button("Clear", command = self.plot.clear)
            
        #     # with Stack():
        #     self.ifsConfigWin = IFSConfigPanel(self)
    #endregion
    
    #region Transform management
    def clearTransforms(self):
        self.transforms = []
    
    def newTransform(self):
        self.clickUp()
        
        with self.transformsScrollArea:
            self.transforms.append(TransformGUI(len(self.transforms), IFS_Transform(), self.plotIFS))
    
    def removeTransform(self, index):
        self.transforms.pop(index)
        
        for i in range(len(self.transforms)):
            self.transforms[i].index = i
    
    def getTransforms(self):
        return self.transforms
    
    def saveToJSON(self):
        print("saveToJSON: NOT YET IMPLEMENTED")
        
    def loadToJSON(self):
        print("loadToJSON: NOT YET IMPLEMENTED")
    #endregion
    
    #region Sounds
    def clickDown(self):
        # if self.PLAY_SOUNDS:
        #     playsound(self.getSound("click down"), False)
        
        pass
    
    def clickUp(self):
        if self.PLAY_SOUNDS:
            playsound(self.getSound("click up"), False)
    #endregion

    #region Drawing
    # Plot the IFS
    def plotIFS(self):
        self.initializePixels()
        self.plot.clear()
            
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
            self.pixels[remappedPt[0]][remappedPt[1]] = colorRGB(*randTransform.color())
        else: # If not, just update the min/max values
            if newPt[0] < self.minX:
                self.minX = newPt[0]
            if newPt[0] > self.maxX:
                self.maxX = newPt[0]
            if newPt[1] < self.minY:
                self.minY = newPt[1]
            if newPt[1] > self.maxY:
                self.maxY = newPt[1]
        
        # Update the current point
        self.point = newPt
    
    # Remap the point to stay within the screen size and within the border padding
    def remapPoint(self, point):
        return (int(lerp(self.drawPadding[0], self.PLOT_SIZE - self.drawPadding[0], point[0])), self.PLOT_SIZE - 1 - int(lerp(self.drawPadding[0], self.PLOT_SIZE - self.drawPadding[0], point[1])))

    # Initialize the pixels array
    def initializePixels(self):
        self.pixels = []
        for x in range(self.PLOT_SIZE):
            col = []
            
            for y in range(self.HEIGHT):
                col.append('white')
            
            self.pixels.append(col)
    #endregion
    
    #region UI Images and Sounds
    # Load every image the local data path
    # These are pixel art images of the UI elements
    def initImagesAndSounds(self, path):
        for file in os.listdir(path + "/Data"):
            fileStr = str(file)
            
            if fileStr.endswith(".png"):
                sizeStartInd = fileStr.find("_") + 1
                sizeEndInd = fileStr.find(".")
                xInd = fileStr.find("x", sizeStartInd)
                
                width = int(fileStr[sizeStartInd:xInd])
                height = int(fileStr[xInd + 1:sizeEndInd])
                
                fileName = fileStr[:sizeStartInd - 1]
                
                self.UI_IMAGES[fileName] = (path + "\Data\\" + file, width, height)
            elif fileStr.endswith(".wav"):
                endInd = fileStr.find(".")
                
                fileName = fileStr[:endInd]
                
                self.UI_SOUNDS[fileName] = path + "\Data\\" + file
            
        print("Loaded " + str(len(self.UI_IMAGES)) + " images")
        print("Loaded " + str(len(self.UI_SOUNDS)) + " sounds")
        
        print(self.UI_SOUNDS)
    
    # Get an image path by name
    def getImage(self, name):
        return self.UI_IMAGES[name][0]
    
    # Get a sound path by name
    def getSound(self, name):
        return self.UI_SOUNDS[name]
    #endregion
    
    # Quit the program
    def quit(self):
        exit()

class TransformGUI(Stack):
    index = 0
    transform = None

    rInput = None
    sInput = None
    thetaInput = None
    phiInput = None
    hInput = None
    kInput = None
    probabilityInput = None
    colorInput = None
    
    def __init__(self, index, transform, plotCallback, **kwargs):
        self.index = index
        self.transform = transform
        self.plotCallback = plotCallback
        
        super().__init__(relief = 'raised', borderwidth = 2, **kwargs)
        
        self.initUI()
    
    def initUI(self):
        with self:
            Label("Transform: " + str(self.index + 1))
            
            with Flow():
                self.rInput = FloatBox(50, 20, self.transform.getR())
                self.sInput = FloatBox(50, 20, self.transform.getS())
            with Flow():
                self.thetaInput = FloatBox(50, 20, self.transform.getTheta())
                self.phiInput = FloatBox(50, 20, self.transform.getPhi())
            with Flow():
                self.hInput = FloatBox(50, 20, self.transform.getE())
                self.kInput = FloatBox(50, 20, self.transform.getF())
            with Flow():
                self.probabilityInput = FloatBox(50, 20, self.transform.getE())
                self.colorInput = ColorWidget(50, 20, self.transform.getColor(), "", buttonLabelPrefix = "")
                
            updateButton = Button("Update", command = self.updateTransform)

    def updateTransform(self):
        print("Before update " + str(self.transform))
        self.transform = IFS_Transform(self.rInput.value, self.sInput.value, self.thetaInput.value, self.phiInput.value, self.hInput.value, self.kInput.value, self.probabilityInput.value, self.colorInput.color)
        print("After update " + str(self.transform))
        
        self.plotCallback()
    
    def transformPoint(self, x, y):
        return self.transform.transformPoint(x, y)

    def color(self):
        return self.transform.getColor()

    def probability(self):
        return self.transform.getProb()

#region Utils
def remap(value, low1, high1, low2, high2):
    return low2 + (value - low1) * (high2 - low2) / (high1 - low1)

def lerp(a, b, t):
    return a + (b - a) * t
#endregion 

if __name__ == "__main__":
    IFSExplorer()