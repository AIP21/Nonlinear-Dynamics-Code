import random
import traceback
from Lib.NewDEGraphics import *
from Lib.transform import *
from Lib.playsound import playsound
from tkinter.font import Font
import os
import json

class IFSExplorer:
    PLAY_SOUNDS = True
    
    UI_IMAGES = {}
    UI_SOUNDS = {}
    
    UI_SCALING = 0.25
    WIDTH = 600
    HEIGHT = 850
    
    TOP_BAR_HEIGHT = 100
    BOTTOM_BAR_HEIGHT = 124
    
    PLOT_HEIGHT = WIDTH #HEIGHT - TOP_BAR_HEIGHT - BOTTOM_BAR_HEIGHT
    PIX_WIDTH = int((WIDTH - 64) / (1 / UI_SCALING))
    PIX_HEIGHT = int((PLOT_HEIGHT - 64) / (1 / UI_SCALING))
        
    MAX_TRANSFORMS = 20
    transforms = []
    transformGUIS = []
    
    pixelFont = None
    
    initialTransforms = []
    
    # Initialize transforms
    initialTransforms.append(IFS_Transform(xScale = 0.5, yScale = 0.5,
                                    theta = 0.0, phi = 0.0,
                                    h = 0.0, k = 0.0,
                                    p = 1, c = (255, 0, 0)))
    initialTransforms.append(IFS_Transform(xScale = 0.5, yScale = 0.5,
                                    theta = 0.0, phi = 0.0,
                                    h = 0.0, k = 0.5,
                                    p = 0.1, c = (0, 255, 0)))
    initialTransforms.append(IFS_Transform(xScale = 0.5, yScale = 0.5,
                                    theta = 0.0, phi = 0.0,
                                    h = 0.5, k = 0.0,
                                    p = 1, c = (0, 0, 255)))
    
    # initialTransforms.append(IFS_Transform(xScale = 0.0, yScale = 0.16,
    #                                 theta = 0.0, phi = 0.0,
    #                                 h = 0.0, k = 0.0,
    #                                 p = 0.01, c = (255, 0, 0)))
    # initialTransforms.append(IFS_Transform(xScale = -0.04, yScale = 0.85,
    #                                 theta = 0.85, phi = -0.04,
    #                                 h = 0.0, k = 1.6,
    #                                 p = 0.85, c = (0, 255 ,0)))
    # initialTransforms.append(IFS_Transform(xScale = 0.23, yScale = 0.22,
    #                                 theta = -0.20, phi = -0.26,
    #                                 h = 0.0, k = 1.6,
    #                                 p = 0.07, c = (0, 0, 255)))
    # initialTransforms.append(IFS_Transform(xScale = 0.26, yScale = 0.24,
    #                                 theta = -0.15, phi = 0.28,
    #                                 h = 0.0, k = 0.44,
    #                                 p = 0.07, c = (0, 0, 255)))
    
    pixels = []

    point = (random.random(), random.random())

    minX = None
    maxX = None
    minY = None
    maxY = None
    
    drawPadding = [10, 10]
    
    transformsScrollArea = None
    
    def __init__(self):
        self.initImagesAndSounds(os.path.dirname(os.path.realpath(__file__)))
        
        self.win = DEGraphWin("IFS Explorer", self.WIDTH, self.HEIGHT, scale = self.UI_SCALING, debugMode = True)
        
        # self.win.hideTitlebar()
        self.win.setTransparentColor("#ad0099")
        self.win.update_idletasks()
        
        self.pixelFont = Font(family = "Small Fonts", size = 70, weight = NORMAL)
        
        self.win.setPrimaryFont(self.pixelFont)
        
        self.initializePixels()
        
        # Create the Controls Window
        self.createControlsWindow()
                
        # UI stuff
        with self.win:
            self.mainCanvas = Canvas(width = self.WIDTH, height = self.HEIGHT - self.BOTTOM_BAR_HEIGHT - 26, bg = "#ad0099")

            with self.mainCanvas:
                # Create the header
                headerImg = GraphicsImage(self.WIDTH / 2, self.TOP_BAR_HEIGHT / 2, tk.PhotoImage(file = self.getImage("header")))
                headerImg.resizeImage(self.WIDTH, self.TOP_BAR_HEIGHT)
                headerImg.draw()
                
                # Quit button
                quitButton = GraphicsButton(self.WIDTH - 85, self.TOP_BAR_HEIGHT / 2 - 24, self.getImage("power button up"), self.getImage("power button down"), width = 50, height = 50, command = self.quit, pressCommand = self.clickDown, tooltipText = 'Quit the program')
                quitButton.draw()
                
                # Help button
                helpButton = GraphicsButton(self.WIDTH - 142, self.TOP_BAR_HEIGHT / 2 - 24, self.getImage("help button up"), self.getImage("help button down"), width = 50, height = 50, command = self.help, pressCommand = self.clickDown, tooltipText = 'Open help menu')
                helpButton.draw()
                
                # Create the canvas and plot for drawing the IFS
                plotBackground = GraphicsImage(self.WIDTH / 2, self.TOP_BAR_HEIGHT + self.PLOT_HEIGHT / 2, PhotoImage(file = self.getImage("plot")), shouldPanZoom = False)
                plotBackground.resizeImage(self.WIDTH, self.PLOT_HEIGHT)
                plotBackground.draw()
                
                plotImage = PhotoImage(width = self.PIX_WIDTH, height = self.PIX_HEIGHT)
                plotImage.put(colorRGB(28, 51, 5), to = (0, 0, self.PIX_WIDTH, self.PIX_HEIGHT))
                
                self.plot = GraphicsImage(self.WIDTH / 2, self.TOP_BAR_HEIGHT + self.PLOT_HEIGHT / 2, plotImage, shouldPanZoom = False)
                self.plot.resizeImage(self.WIDTH - 64, self.PLOT_HEIGHT - 64)
                self.plot.draw()
                
                self.plotOverlay = GraphicsImage(self.WIDTH / 2, self.TOP_BAR_HEIGHT + self.PLOT_HEIGHT / 2, PhotoImage(file = self.getImage("plot overlay")), shouldPanZoom = False)
                self.plotOverlay.resizeImage(self.WIDTH - 64, self.PLOT_HEIGHT - 64)
                self.plotOverlay.draw()
            
            # Create the IFS Config Panel
            self.createIFSControlPanel()
            
            # Plot the IFS
            self.plotIFS()
    
    #region GUI
    # Create the IFS Control Panel
    def createIFSControlPanel(self):
        bottomPanelHeight = self.BOTTOM_BAR_HEIGHT + 26
        
        self.bottomPanel = Flow(width = self.WIDTH, height = bottomPanelHeight, bg = "#ad0099")
        with self.bottomPanel:
            buttonPanelWidth = 60
            
            buttonsPanel = Canvas(width = buttonPanelWidth, height = bottomPanelHeight, bg = "#ad0099")
            
            with buttonsPanel:
                img = GraphicsImage(buttonPanelWidth / 2, bottomPanelHeight / 2, PhotoImage(file = self.getImage("warning panel long")), shouldPanZoom = False)
                img.resizeImage(buttonPanelWidth, bottomPanelHeight)
                img.draw()
                
                yStart = 19
                buttonSize = 25
                spacing = 4
                buttonX = buttonPanelWidth / 2 - 1 - buttonSize / 2
            
                newButton = GraphicsButton(buttonX, yStart, self.getImage("add button up"), self.getImage("add button down"), width = buttonSize, height = buttonSize, command = self.newTransform, pressCommand = self.clickDown, tooltipText = 'Open help menu')
                newButton.draw()
            
                saveButton = GraphicsButton(buttonX, yStart + buttonSize + spacing, self.getImage("save button up"), self.getImage("save button down"), width = buttonSize, height = buttonSize, command = self.saveTransforms, pressCommand = self.clickDown, tooltipText = 'Save transforms to JSON')
                saveButton.draw()
            
                loadButton = GraphicsButton(buttonX, yStart + buttonSize * 2 + spacing * 2, self.getImage("load button up"), self.getImage("load button down"), width = buttonSize, height = buttonSize, command = self.loadTransforms, pressCommand = self.clickDown, tooltipText = 'Load transforms from JSON')
                loadButton.draw()
            
                clearButton = GraphicsButton(buttonX, yStart + buttonSize * 3 + spacing * 3, self.getImage("x button up"), self.getImage("x button down"), width = buttonSize, height = buttonSize, command = self.clearTransforms, pressCommand = self.clickDown, tooltipText = 'Clear all transforms')
                clearButton.draw()

            rightPanel = Canvas(width = self.WIDTH - buttonPanelWidth, height = bottomPanelHeight, bg = "#ad0099")
            
            with rightPanel:
                background = GraphicsImage((self.WIDTH - buttonPanelWidth) / 2, bottomPanelHeight / 2, PhotoImage(file = self.getImage("panel wide")), shouldPanZoom = False)
                background.resizeImage(self.WIDTH - buttonPanelWidth, bottomPanelHeight)
                background.draw()
            
                padX = 30
                padY = 10
                self.scrollArea = Canvas(width = self.WIDTH - buttonPanelWidth - padX * 2, height = bottomPanelHeight - padY * 2, bg = "#818181")
                
                with self.scrollArea:
                    def scrollTransforms(event):
                        self.scrollArea.xview_scroll(-1 * int(event.delta / 120), "units")
                    
                    self.scrollArea.bind_all("<MouseWheel>", scrollTransforms)
                    
                    # Add initial transforms
                    for i in range(len(self.initialTransforms)):
                        y = bottomPanelHeight - padY * 2
                        gui = TransformGUI(i, 100, y - 10, self.initialTransforms[i], self.plotIFS, self.getImage("panel big"), self.getImage("button up small"), self.getImage("button down small"), bg = "#818181", main = self)
                        self.scrollArea.addWidget(gui, 50 + i * 100, y / 2)
                        self.transforms.append(gui)
                
                    rightPanel.addWidget(self.scrollArea, (self.WIDTH - buttonPanelWidth) / 2, bottomPanelHeight / 2, width = self.WIDTH - buttonPanelWidth - padX * 2, height = bottomPanelHeight - padY * 2)
            
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
        self.scrollArea.clearWidgets()
        
        self.transforms = []
    
    def newTransform(self):
        self.clickUp()
        
        if len(self.transforms) < self.MAX_TRANSFORMS:
            y = self.BOTTOM_BAR_HEIGHT + 26 - 10 * 2
            i = len(self.transforms)
            gui = TransformGUI(i, 100, y - 10, IFS_Transform(0, 0, 0, 0, 0, 0, 1, (255, 0, 0)), self.plotIFS, self.getImage("panel big"), self.getImage("button up small"), self.getImage("button down small"), bg = "#818181", main = self)
            self.scrollArea.addWidget(gui, 50 + i * 100, y / 2)
            self.transforms.append(gui)
    
    def addTransform(self, trans):
        if len(self.transforms) < self.MAX_TRANSFORMS:
            y = self.BOTTOM_BAR_HEIGHT + 26 - 10 * 2
            i = len(self.transforms)
            gui = TransformGUI(i, 100, y - 10, trans, self.plotIFS, self.getImage("panel big"), self.getImage("button up small"), self.getImage("button down small"), bg = "#818181", main = self)
            self.scrollArea.addWidget(gui, 50 + i * 100, y / 2)
            self.transforms.append(gui)
    
    def removeTransform(self, index):
        self.transforms.pop(index)
        
        for i in range(len(self.transforms)):
            self.transforms[i].index = i
    
    def saveTransforms(self):
        try:
            toSave = {}
            
            for i in range(len(self.transforms)):
                toSave[i] = self.transforms[i].transform.toDict()

            # Write json
            localPath = os.path.dirname(os.path.realpath(__file__))
            with open(localPath + "/transforms.json", "w") as file:
                json.dump(toSave, file)
            
            print("Saved transforms to " + localPath + "/transforms.txt")
        except:
            print("Error writing JSON file")
    
    def loadTransforms(self):
        try:
            # file = filedialog.askopenfilename(initialdir = os.path.dirname(os.path.realpath(__file__)), title = "Select file", filetypes = (("json files","*.json"),("all files","*.*")))
            
            # Load json
            localPath = os.path.dirname(os.path.realpath(__file__))
            with open(localPath + "/transforms.json", "r") as file:
                loaded = json.load(file)
                
            self.clearTransforms()
            
            for i in range(len(loaded)):
                trans = IFS_Transform.ofDict(loaded[str(i)])
                self.addTransform(trans)
        except:
            print("Error reading JSON file")
        
        self.plotIFS()
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
        print("Plotting IFS")
        
        self.initializePixels()
        
        self.point = (random.random(), random.random())
        
        # print("Start point: " + str(self.point))

        self.minX = None
        self.maxX = None
        self.minY = None
        self.maxY = None
        
        self.plot.resizeImage(self.PIX_WIDTH, self.PIX_HEIGHT)
        img = self.plot.getImage()
        img.put(colorRGB(28, 51, 5), to = (0, 0, img.width(), img.height()))

        # Transient iterations to covnerge before checking min and max
        for i in range(10000):
            self.iterate(False, False)
        
        # print("Point after head start: " + str(self.point))
        
        # For getting min and max
        for e in range(1000):
            self.iterate(False, True)
        
        print("MinX: " + str(self.minX))
        print("MaxX: " + str(self.maxX))
        print("MinY: " + str(self.minY))
        print("MaxY: " + str(self.maxY))
        
        # For plotting
        try:
            for j in range(100000):
                self.iterate(True, False)
        except Exception as e:
            print("Size: " + str(self.PIX_WIDTH) + "x" + str(self.PIX_HEIGHT) + " Point: " + str(self.point) + " remapped: " + str(self.remapPt))
            print("Error: " + str(e) + " stack: " + str(traceback.format_exc()))
        
        print("Done iterating")
        
        img.put(self.pixels, (0, 0))
        
        self.plot.setImage(img)
        self.plot.resizeImage(self.WIDTH - 64, self.PLOT_HEIGHT - 64)
        self.plot.draw()
        
        # Keep overlay above plot
        self.mainCanvas.lift(self.plotOverlay.id, self.plot.id)
    
    # Iterate the IFS system
    def iterate(self, shouldPlot, checkMinMax):
        # Choose a random transformation for this iteration, uses the probabilities of each transformation
        randTransform = random.choices(self.transforms, weights = [t.transform.getProb() for t in self.transforms], k = 1)[0].transform
        
        # Transform the current point and keep it as a new point
        newPt = randTransform.transformPoint(self.point[0], self.point[1])
        
        # Should we plot this point by adding it to the pixels array?
        if shouldPlot:
            # Remap the new point to be within the screen
            pt = self.remapPoint(newPt)
            
            self.remapPt = pt
            
            if pt[0] < self.PIX_WIDTH and pt[1] < self.PIX_HEIGHT:
                # Set the pixel at this screen position to the color of the transformation
                self.pixels[floor(pt[0])][floor(pt[1])] = colorRGB(*randTransform.color)
        elif checkMinMax and self.maxX == None:
            # If this is the first point, set the min/max values to this point
            self.minX = newPt[0]
            self.maxX = newPt[0]
            self.minY = newPt[1]
            self.maxY = newPt[1]
        elif checkMinMax: # If not, just update the min/max values
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
        x = self.PIX_WIDTH - remap(x, self.minX, self.maxX, 0.0, self.PIX_WIDTH)
        y = self.PIX_HEIGHT - remap(y, self.minY, self.maxY, 0.0, self.PIX_HEIGHT)
        
        return (x, y)

    # Initialize the pixels array
    def initializePixels(self):
        self.pixels = []
        for x in range(self.PIX_WIDTH):
            col = []
            
            for y in range(self.PIX_HEIGHT):
                
                col.append(colorRGB(28, 51, 5))
            
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
    
    #region Guide
    def help(self):
        print('help')
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
    
    def __init__(self, index, width, height, transform, plotCallback, img, a, b, main, **kwargs):
        self.index = index
        self.plotCallback = plotCallback
        self.width = width
        self.height = height
        self.a = a
        self.b = b
        self.main = main
        
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
        
        self.create_text(45, 10, text = str(self.index), anchor = "nw", font = ("Small Fonts", 12, BOLD), fill = "white")
        
        self.rInput = FloatBox(50, 20, self.transform.getR())
        self.addWidget(self.rInput, 10, 70)
        self.sInput = FloatBox(50, 20, self.transform.getS())
        self.addWidget(self.sInput, 20, 70)
        
        self.thetaInput = FloatBox(50, 20, self.transform.getTheta())
        self.addWidget(self.thetaInput, 10, 130)
        self.phiInput = FloatBox(50, 20, self.transform.getPhi())
        self.addWidget(self.thetaInput, 20, 130)
        
        self.hInput = FloatBox(50, 20, self.transform.getE())
        self.addWidget(self.hInput, 10, 160)
        self.kInput = FloatBox(50, 20, self.transform.getF())
        self.addWidget(self.kInput, 20, 160)
        
        self.probabilityInput = FloatBox(50, 20, self.transform.getE())
        self.addWidget(self.probabilityInput, 10, 220)
        self.colorInput = ColorWidget(50, 20, self.transform.getColor(), "", buttonLabelPrefix = "")
        self.addWidget(self.colorInput, 20, 220)

        # Remove button
        removeButton = GraphicsButton(0, 0, self.main.getImage("x button up"), self.main.getImage("x button down"), width = 20, height = 20, command = lambda: self.main.removeTransform(self.index))
        removeButton.draw()

        # Update button
        updateButton = GraphicsButton(40, 85, self.a, self.b, width = 20, height = 20, command = self.updateTransform, tooltipText = "Update transform")
        updateButton.draw()

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

if __name__ == "__main__":
    IFSExplorer()