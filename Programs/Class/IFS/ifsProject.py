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
    
    UI_SCALING = 0.25
    WIDTH = 600
    HEIGHT = 850
    PIX_WIDTH = 600 #int(600 * UI_SCALING)
    PIX_HEIGHT = 600 #int(600 * UI_SCALING)
        
    MAX_TRANSFORMS = 10
    transforms = []
    transformGUIS = []
    
    pixelFont = None
    
    initialTransforms = []
    
    # Sierpinski Triangle
    initialTransforms.append(IFS_Transform(xScale = 0.5, yScale = 0.5,
                                    theta = 0, phi = 0,
                                    h = 0.0, k = 0.0,
                                    p = 1, c = (255, 0, 0)))
    initialTransforms.append(IFS_Transform(xScale = 0.5, yScale = 0.5,
                                    theta = 0, phi = 0,
                                    h = 0.0, k = 0.5,
                                    p = 1, c = (0, 255 ,0)))
    initialTransforms.append(IFS_Transform(xScale = 0.5, yScale = 0.5,
                                    theta = 0.0, phi = 0.0,
                                    h = 0.5, k = 0,
                                    p = 1, c = (0, 0, 255)))
    
    # FERN???
    # initialTransforms.append(IFS_Transform(xScale = 1/3, yScale = 1/3,
    #                                 theta = -14, phi = -14,
    #                                 h = 0.0, k = 0.0,
    #                                 p = 1, c = (255, 0, 0)))
    # initialTransforms.append(IFS_Transform(xScale = 4.5/12, yScale = 4.5/12,
    #                                 theta = 48, phi = 48,
    #                                 h = 0.0, k = 2/12,
    #                                 p = 1, c = (0, 255 ,0)))
    # initialTransforms.append(IFS_Transform(xScale = 1/100, yScale = 1/6,
    #                                 theta = 0.0, phi = 0.0,
    #                                 h = 0.0, k = 0.5/12, # h = 0.25 ???
    #                                 p = 1, c = (0, 0, 255)))
    # initialTransforms.append(IFS_Transform(xScale = 10/12, yScale = 10/12, # Stem
    #                                 theta = 0.0, phi = 0.0,
    #                                 h = 0.0, k = 2/12, # h = 0.25 ???
    #                                 p = 1, c = (0, 0, 255)))
    
    pixels = []

    point = (random.random() * 10000000.0, random.random() * 10000000.0)

    minX = None
    maxX = None
    minY = None
    maxY = None
    
    drawPadding = [10, 10]
    
    transformsScrollArea = None
        
    def __init__(self):
        self.initImagesAndSounds(os.path.dirname(os.path.realpath(__file__)))
        
        self.win = DEGraphWin("IFS Explorer", self.WIDTH + 10, self.HEIGHT + 10, scale = 0.25, debugMode = True, edgePadding = [5, 5, 5, 5])
        
        # self.win.hideTitlebar()
        self.win.update_idletasks()
        
        self.pixelFont = Font(family = "Small Fonts", size = 70, weight = NORMAL)
        
        self.win.setPrimaryFont(self.pixelFont)
        
        self.initializePixels()
        
        # Create the Controls Window
        self.createControlsWindow()
                
        # UI stuff
        with self.win:
            self.mainStack = Stack(width = self.WIDTH, height = self.HEIGHT)
            with self.mainStack:
                # Create the header
                Image(self.WIDTH, 100, self.getImage("header"))
                
                # Create the canvas and plot for drawing the IFS                
                with Canvas(width = self.WIDTH, height = self.PIX_HEIGHT):
                    img = GraphicsImage(self.WIDTH / 2, self.PIX_HEIGHT / 2, PhotoImage(file = self.getImage("warning panel")), shouldPanZoom = False)
                    img.resizeImage(self.WIDTH, self.PIX_HEIGHT)
                    img.draw()
                    
                    self.plot = Plot(self.WIDTH - 40, self.PIX_HEIGHT - 40, self.WIDTH, self.PIX_HEIGHT)
                
                # Create the IFS Config Panel
                self.createIFSControlPanel()
                
                # Plot the IFS
                self.plotIFS()
    
    #region GUI
    # Create the IFS Control Panel
    def createIFSControlPanel(self):
        self.bottomPanel = Flow(width = self.WIDTH, height = 100)
        with self.bottomPanel:
            buttonsPanel = Canvas(width = 50, height = 100)
            
            with buttonsPanel:
                img = GraphicsImage(15 / 2, 50, PhotoImage(file = self.getImage("warning panel")), shouldPanZoom = False)
                img.resizeImage(50, 100)
                img.draw()
            
                newButton = ImageButton(self.getImage("button up"), self.getImage("button down"), width = 40, height = 40, command = self.newTransform, pressCommand = self.clickDown)
                
                # saveButton = ImageButton(self.getImage("button up"), self.getImage("button down"), width = 40, height = 40, command = self.saveTransforms, pressCommand = self.clickDown)
                
                # loadButton = ImageButton(self.getImage("button up"), self.getImage("button down"), width = 40, height = 40, command = self.loadTransforms, pressCommand = self.clickDown)
                
                # clearButton = ImageButton(self.getImage("button up"), self.getImage("button down"), width = 40, height = 40, command = self.clearTransforms, pressCommand = self.clickDown)
            
            Separator(width = 1, height = 100, horizontalSpacing = 5, verticalSpacing = 0)
            
            self.transformsScrollArea = HorizontalScrollView(width = self.WIDTH - 15)
            
            # Add initial transforms
            for i in range(len(self.initialTransforms)):
                gui = TransformGUI(i, 124, 143, self.initialTransforms[i], self.plotIFS, self.getImage("panel big"))
                self.transformsScrollArea.add_widget(gui)
                self.transforms.append(gui)
            
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
        for gui in self.transforms:
            self.transformsScrollArea.remove_widget(gui)
        
        self.transforms = []
    
    def newTransform(self):
        self.clickUp()
                
        if len(self.transforms) < self.MAX_TRANSFORMS:
            gui = TransformGUI(len(self.transforms) - 1, 124, 143, IFS_Transform(0, 0, 0, 0, 0, 0, 1, (255, 0, 0)), self.plotIFS, self.getImage("panel big"))
            self.transformsScrollArea.add_widget(gui)
            self.transforms.append(gui)
    
    def removeTransform(self, index):
        print("removeTransform: NOT YET IMPLEMENTED")
        
        return
        
        self.transforms.pop(index)
        
        for i in range(len(self.transforms)):
            self.transforms[i].index = i
    
    def saveTransforms(self):
        print("saveTransforms: NOT YET IMPLEMENTED")
    
    def loadTransforms(self):
        print("loadTransforms: NOT YET IMPLEMENTED")
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
        randTransform = self.initialTransforms[random.randint(0, len(self.initialTransforms) - 1)]
        
        # Transform the current point and keep it as a new point
        newPt = randTransform.transformPoint(self.point[0], self.point[1])
        
        # Should we plot this point by adding it to the pixels array?
        if shouldPlot: 
            # Remap the new point to be within the screen
            remappedPt = self.remapPoint(newPt)
            
            # Set the pixel at this screen position to the color of the transformation
            self.pixels[remappedPt[0]][remappedPt[1]] = colorRGB(*randTransform.color)
        elif self.maxX == None:
            # If this is the first point, set the min/max values to this point
            self.minX = newPt[0]
            self.maxX = newPt[0]
            self.minY = newPt[1]
            self.maxY = newPt[1]
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
        x = point[0]
        y = point[1]
        
        # Scale to pixel coords
        x = int(lerp(self.drawPadding[0], self.PIX_WIDTH - self.drawPadding[0], x))
        y = self.PIX_HEIGHT - int(lerp(self.drawPadding[1], self.PIX_HEIGHT - self.drawPadding[1], y))
        
        return (x, y)

    # Initialize the pixels array
    def initializePixels(self):
        self.pixels = []
        for x in range(self.PIX_WIDTH):
            col = []
            
            for y in range(self.PIX_HEIGHT):
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

class TransformGUI(Canvas):
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
    
    def __init__(self, index, width, height, transform, plotCallback, img, **kwargs):
        self.index = index
        self.plotCallback = plotCallback
        self.width = width
        self.height = height
        
        super().__init__(width = width, height = height, **kwargs)
        
        with self:
            img = GraphicsImage(width / 2, height / 2, PhotoImage(file = img), shouldPanZoom = False)
            img.resizeImage(width - 10, height - 10)
            img.draw()
            
            self.initUI(transform)
            
    
    def initUI(self, transform):
        if transform == None:
            return
        
        self.transform = transform
        
        Text(self.width, 20, 2000, self.height, "dgf", font = ("Small Fonts", 48, BOLD), justify = 'left').draw()

        # Label("Transform: " + str(self.index + 1), font = ("Small Fonts", 48, BOLD), width = 10, height = 10)
        
        # with Flow():
        #     self.rInput = FloatBox(50, 20, self.transform.getR())
        #     self.sInput = FloatBox(50, 20, self.transform.getS())
        # with Flow():
        #     self.thetaInput = FloatBox(50, 20, self.transform.getTheta())
        #     self.phiInput = FloatBox(50, 20, self.transform.getPhi())
        # with Flow():
        #     self.hInput = FloatBox(50, 20, self.transform.getE())
        #     self.kInput = FloatBox(50, 20, self.transform.getF())
        # with Flow():
        #     self.probabilityInput = FloatBox(50, 20, self.transform.getE())
        #     self.colorInput = ColorWidget(50, 20, self.transform.getColor(), "", buttonLabelPrefix = "")
            
        # updateButton = Button("Update", command = self.updateTransform)

    def updateTransform(self):
        print("Before update " + str(self.transform))
        self.transform = IFS_Transform(self.rInput.value, self.sInput.value, self.thetaInput.value, self.phiInput.value, self.hInput.value, self.kInput.value, self.probabilityInput.value, self.colorInput.color)
        print("After update " + str(self.transform))
        
        self.plotCallback()
    
    def setTransform(self, trans):
        self.initUI(trans)
    
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