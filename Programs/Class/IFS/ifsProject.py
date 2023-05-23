import random
import traceback
from Lib.NewDEGraphics import *
from Lib.transform import *
from Lib.playsound import playsound
from tkinter.font import Font
import os
import json
import datetime
import gc

# Make garbage collection more aggressive
gc.set_threshold(100, 10, 10)

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
        
    MAX_TRANSFORMS = 50
    transforms = []
    transformGUIS = []
    
    pixelFont = None
            
    # Initialize transforms
    initialTransforms = []
    
    # initialTransforms = [
    #     IFS_Transform(xScale = 0.85, yScale = 0.85, theta = 0, phi = 0, h = 0, k = 0, p = 0.1),
    #     IFS_Transform(xScale = 0.04, yScale = 0.85, theta = -60, phi = 0, h = 0.16, k = 0, p = 0.85),
    #     IFS_Transform(xScale = 0.2, yScale = 0.26, theta = 0, phi = 0, h = -0.26, k = 0.23, p = 0.05),
    #     IFS_Transform(xScale = 0.2, yScale = 0.26, theta = 0, phi = 0, h = 0.26, k = -0.23, p = 0.05),
    # ]
        
    # Sierpinski triangle
    # initialTransforms = [
    #     IFS_Transform(xScale = 0.5, yScale = 0.5, theta = 0.0, phi = 0.0, h = 0.0, k = 0.0, p = 1, c = (255, 0, 0)),
    #     IFS_Transform(xScale = 0.5, yScale = 0.5, theta = 0.0, phi = 0.0, h = 0.0, k = 0.5, p = .1, c = (0, 255, 0)),
    #     IFS_Transform(xScale = 0.5, yScale = 0.5, theta = 0.0, phi = 0.0, h = 0.5, k = 0.0, p = 1, c = (0, 0, 255))
    # ]
    
    # Bad fern
    # initialTransforms = [
    #     IFS_Transform(xScale = 0.0, yScale = 0.16, theta = 0.0, phi = 0.0, h = 0.0, k = 0.0, p = 0.01, c = (255, 0, 0)),
    #     IFS_Transform(xScale = -0.04, yScale = 0.85, theta = 0.85, phi = -0.04, h = 0.0, k = 1.6, p = 0.85, c = (0, 255 ,0)),
    #     IFS_Transform(xScale = 0.23, yScale = 0.22, theta = -0.20, phi = -0.26, h = 0.0, k = 1.6, p = 0.07, c = (0, 0, 255)),
    #     IFS_Transform(xScale = 0.26, yScale = 0.24, theta = -0.15, phi = 0.28, h = 0.0, k = 0.44, p = 0.07, c = (0, 0, 255))
    # ]
    
    pixels = []

    point = (random.random(), random.random())

    minX = None
    maxX = None
    minY = None
    maxY = None
    
    drawPadding = [3, 3]
    
    transformsScrollArea = None
    transformsScrollX = 0
    
    helpBoxes = []
    
    def __init__(self):
        self.initImagesAndSounds(os.path.dirname(os.path.realpath(__file__)))
        
        self.win = DEGraphWin("IFS Explorer", self.WIDTH, self.HEIGHT, scale = self.UI_SCALING) #, debugMode = True)
        
        self.win.hideTitlebar()
        self.win.setTransparentColor("#ad0099")
        self.win.update_idletasks()
        self.win.resizable(False, False)
        
        self.pixelFont = Font(family = "Small Fonts", size = 70, weight = NORMAL)
        
        self.win.setPrimaryFont(self.pixelFont)
                        
        # Create the Controls Window
        # self.createControlsWindow()
                
        # UI stuff
        with self.win:
            self.mainCanvas = Canvas(width = self.WIDTH, height = self.HEIGHT - self.BOTTOM_BAR_HEIGHT - 26, bg = "#ad0099")

            with self.mainCanvas:
                # Create the header
                headerImg = GraphicsImage(self.WIDTH / 2, self.TOP_BAR_HEIGHT / 2, tk.PhotoImage(file = self.getImage("header")))
                headerImg.resizeImage(self.WIDTH, self.TOP_BAR_HEIGHT)
                headerImg.draw()
                
                # Quit button
                self.quitButton = GraphicsButton(self.WIDTH - 85, self.TOP_BAR_HEIGHT / 2 - 24, self.getImage("power button up"), self.getImage("power button down"), width = 50, height = 50, command = self.quit, pressCommand = self.clickDown, tooltipText = 'Quit the program', scale = self.UI_SCALING)
                self.quitButton.draw()
                
                # Help button
                self.helpButton = GraphicsButton(self.WIDTH - 142, self.TOP_BAR_HEIGHT / 2 - 24, self.getImage("help button up"), self.getImage("help button down"), width = 50, height = 50, command = self.help, pressCommand = self.clickDown, tooltipText = 'Open help menu', scale = self.UI_SCALING)
                self.helpButton.draw()
                
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
                
                self.plotTitle = self.mainCanvas.create_text(self.WIDTH / 2, 115, text = "IFS Name: None", anchor = 'center', justify = 'center', font = ("Small Fonts", 70, BOLD), fill = "white")
                self.mainCanvas.tag_raise(self.plotTitle)
            
            try:
                # Create the IFS Config Panel
                self.createIFSControlPanel()
            except Exception as e:
                print("ERROR 0: " + str(e) + "\n\n" + str(traceback.format_exc()))
            
            # Plot the IFS
            self.plotIFS()
            
            def initHelp():
                import time
                time.sleep(0.5)
                while self.helpButton == None:
                    time.sleep(0.1)
                self.help()
            
            thr = threading.Thread(target = initHelp)
            thr.start()
    
    #region GUI
    # Create the IFS Control Panel
    def createIFSControlPanel(self):
        bottomPanelHeight = self.BOTTOM_BAR_HEIGHT + 26
        
        self.bottomPanel = Flow(width = self.WIDTH, height = bottomPanelHeight, bg = "#ad0099")
        with self.bottomPanel:
            buttonPanelWidth = 60
            
            self.buttonsPanel = Canvas(width = buttonPanelWidth, height = bottomPanelHeight, bg = "#ad0099")
            
            with self.buttonsPanel:
                img = GraphicsImage(buttonPanelWidth / 2, bottomPanelHeight / 2, PhotoImage(file = self.getImage("warning panel long")), shouldPanZoom = False)
                img.resizeImage(buttonPanelWidth, bottomPanelHeight)
                img.draw()
                
                yStart = 19
                buttonSize = 25
                spacing = 4
                buttonX = buttonPanelWidth / 2 - 1 - buttonSize / 2
            
                self.newButton = GraphicsButton(buttonX, yStart, self.getImage("add button up"), self.getImage("add button down"), width = buttonSize, height = buttonSize, command = self.newTransform, pressCommand = self.clickDown, tooltipText = 'Open help menu', scale = self.UI_SCALING)
                self.newButton.draw()
            
                self.saveButton = GraphicsButton(buttonX, yStart + buttonSize + spacing, self.getImage("save button up"), self.getImage("save button down"), width = buttonSize, height = buttonSize, command = self.saveTransforms, pressCommand = self.clickDown, tooltipText = 'Save transforms to JSON', scale = self.UI_SCALING)
                self.saveButton.draw()
            
                self.loadButton = GraphicsButton(buttonX, yStart + buttonSize * 2 + spacing * 2, self.getImage("load button up"), self.getImage("load button down"), width = buttonSize, height = buttonSize, command = self.loadTransforms, pressCommand = self.clickDown, tooltipText = 'Load transforms from JSON', scale = self.UI_SCALING)
                self.loadButton.draw()
            
                self.clearButton = GraphicsButton(buttonX, yStart + buttonSize * 3 + spacing * 3, self.getImage("x button up"), self.getImage("x button down"), width = buttonSize, height = buttonSize, command = self.clearTransforms, pressCommand = self.clickDown, tooltipText = 'Clear all transforms', scale = self.UI_SCALING)
                self.clearButton.draw()

            self.rightPanel = Canvas(width = self.WIDTH - buttonPanelWidth, height = bottomPanelHeight, bg = "#ad0099")
            
            with self.rightPanel:
                background = GraphicsImage((self.WIDTH - buttonPanelWidth) / 2, bottomPanelHeight / 2, PhotoImage(file = self.getImage("panel wide")), shouldPanZoom = False)
                background.resizeImage(self.WIDTH - buttonPanelWidth, bottomPanelHeight)
                background.draw()
            
                padX = 30
                padY = 10
                self.scrollArea = Canvas(width = self.WIDTH - buttonPanelWidth - padX * 2, height = bottomPanelHeight - padY * 2, bg = "#818181")
                
                # Scroll area for the transforms list
                with self.scrollArea:
                    def scrollTransforms(event):
                        delta = int(event.delta / 20)
                        width = self.WIDTH - buttonPanelWidth - padX * 2
                        curWidth = 100 * len(self.transforms)
                        
                        # if delta > 0:
                        #     delta = 1
                        # elif delta < 0:
                        #     delta = -1
                                                
                        # Don't scroll if we don't need to reveal anything new
                        if width > curWidth:
                            return
                        
                        maxScroll = curWidth - width
                        
                        # print("new scroll: " + str(self.transformsScrollX - delta) + ", maxScroll: " + str(maxScroll))
                        
                        # Clamp the new scroll so that we don't scroll out of bounds
                        newScroll = clamp(self.transformsScrollX - delta, 0, maxScroll)
                        
                        delta = newScroll - self.transformsScrollX
                        
                        self.transformsScrollX = newScroll
                        
                        # print("Delta: " + str(delta) + ", New Scroll: " + str(newScroll))
                        # print("transformsScrollX: " + str(self.transformsScrollX))
                        
                        # self.scrollArea.xview_scroll(delta, "units")
                        self.scrollArea.move("all", -delta, 0)
                        # self.scrollArea.update()
                        # self.scrollArea.scan_mark(0, 0)
                        # self.scrollArea.scan_dragto(-delta, 0, gain = 1)
                        # self.scrollArea.xview('scroll', delta, 'units')
                    
                    self.scrollArea.bind_all("<MouseWheel>", scrollTransforms, add = True)
                    
                    self.scrollArea.config(scrollregion = (0, 0, 0, 50 + len(self.initialTransforms) * 100))
                    
                    self.initialTransforms = self.loadRandomSystem()
                    
                    # Add initial transforms
                    for i in range(len(self.initialTransforms)):
                        y = bottomPanelHeight - padY * 2
                        gui = TransformGUI(i, 100, y - 10, self.initialTransforms[i], self.plotIFS, self.getImage("panel big"), self.getImage("button up small"), self.getImage("button down small"), bg = "#818181", main = self)
                        self.scrollArea.addWidget(gui, 50 + i * 100, y / 2)
                        self.transforms.append(gui)
                
                    self.rightPanel.addWidget(self.scrollArea, (self.WIDTH - buttonPanelWidth) / 2, bottomPanelHeight / 2, width = self.WIDTH - buttonPanelWidth - padX * 2, height = bottomPanelHeight - padY * 2)
    #endregion
    
    #region Transform management
    def clearTransforms(self):
        self.scrollArea.clearWidgets()
        
        self.transforms = []
        self.scrollArea.move("all", -self.transformsScrollX, 0)
        self.transformsScrollX = 0
        
        # self.plotIFS()
    
    def newTransform(self):
        self.clickUp()
        
        if len(self.transforms) < self.MAX_TRANSFORMS:
            y = self.BOTTOM_BAR_HEIGHT + 26 - 10 * 2
            i = len(self.transforms)
            gui = TransformGUI(i, 100, y - 10, IFS_Transform(0, 0, 0, 0, 0, 0, 1, (255, 0, 0)), self.plotIFS, self.getImage("panel big"), self.getImage("button up small"), self.getImage("button down small"), bg = "#818181", main = self)
            self.scrollArea.addWidget(gui, 50 + i * 100, y / 2)
            self.transforms.append(gui)
        
        self.plotIFS()
    
    def addTransform(self, trans):
        if len(self.transforms) < self.MAX_TRANSFORMS:
            y = self.BOTTOM_BAR_HEIGHT + 26 - 10 * 2
            i = len(self.transforms)
            gui = TransformGUI(i, 100, y - 10, trans, self.plotIFS, self.getImage("panel big"), self.getImage("button up small"), self.getImage("button down small"), bg = "#818181", main = self)
            self.scrollArea.addWidget(gui, 50 + i * 100, y / 2)
            self.transforms.append(gui)
    
    def removeTransform(self, index):
        transformsCopy = self.transforms.copy()
        
        self.clearTransforms()
        
        transformsCopy.pop(index)
        
        for i in range(len(transformsCopy)):
            y = self.BOTTOM_BAR_HEIGHT + 26 - 10 * 2
            i = len(self.transforms)
            gui = transformsCopy[i]
            gui.setIndex(i)
            self.scrollArea.addWidget(gui, 50 + i * 100, y / 2)
            self.transforms.append(gui)
        
        self.plotIFS()
    
    def saveTransforms(self):
        try:
            path = filedialog.askdirectory(initialdir = os.path.dirname(os.path.realpath(__file__)) + "/Systems", title = "Select directory")
            
            toSave = {}
            
            for i in range(len(self.transforms)):
                toSave[i] = self.transforms[i].transform.toDict()

            fileName = "system " + datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S") + ".json"

            # Write json
            with open(path + "/" + fileName, "w") as file:
                json.dump(toSave, file, indent = 4)
            
            print("Saved transforms to " + path + "/" + fileName)
        except Exception as e:
            print("Error writing JSON file" + str(e) + "\n" + traceback.format_exc())
    
    def loadTransforms(self):
        try:
            fileDir = filedialog.askopenfilename(initialdir = os.path.dirname(os.path.realpath(__file__)) + "/Systems", title = "Select file", filetypes = (("json files","*.json"),("all files","*.*")))
            
            if fileDir == "" or fileDir == None:
                return
            
            lastSlash = fileDir.rfind("/")
            name = fileDir[lastSlash + 1:].replace(".json", "")
            self.mainCanvas.itemconfig(self.plotTitle, text = "IFS Name: " + name)
            self.mainCanvas.tag_raise(self.plotTitle)
            
            # Load json
            with open(fileDir, "r") as file:
                loaded = json.load(file)
                
            self.clearTransforms()
            
            for i in range(len(loaded)):
                trans = IFS_Transform.ofDict(loaded[str(i)])
                self.addTransform(trans)
            
            print("Loaded transforms from " + fileDir)
        except Exception as e:
            print("Error reading JSON file. " + str(e) + "\n" + traceback.format_exc())
        
        self.plotIFS()
    
    def loadInitTransforms(self, fileName):
        fileDir = os.path.dirname(os.path.realpath(__file__)) + "/Systems/" + fileName
        
        name = fileName.replace(".json", "")
        self.mainCanvas.itemconfig(self.plotTitle, text = "IFS Name: " + name)
        self.mainCanvas.tag_raise(self.plotTitle)
        
        # Load json
        with open(fileDir, "r") as file:
            loaded = json.load(file)
            
        self.clearTransforms()
        
        toReturn = []
        
        for i in range(len(loaded)):
            toReturn.append(IFS_Transform.ofDict(loaded[str(i)]))
        
        for i in range(len(toReturn)):
            print(toReturn[i])
        
        print("Loaded " + str(len(toReturn)) + " transforms from " + fileDir)
        return toReturn
    
    def loadRandomSystem(self):
        try:
            directory = os.path.dirname(os.path.realpath(__file__)) + "/Systems"
            
            # Get list of every file in that folder
            files = []
            for (dirpath, dirnames, filenames) in os.walk(directory):
                files.extend(filenames)
                break
            
            # Get random file
            fileDir = os.path.dirname(os.path.realpath(__file__)) + "/Systems/" + random.choice(files)
            
            name = fileDir.replace(os.path.dirname(os.path.realpath(__file__)) + "/Systems/", "").replace(".json", "")
            self.mainCanvas.itemconfig(self.plotTitle, text = "IFS Name: " + name)
            self.mainCanvas.tag_raise(self.plotTitle)
            
            # Load json
            with open(fileDir, "r") as file:
                loaded = json.load(file)
                
            self.clearTransforms()
            
            toReturn = []
            
            for i in range(len(loaded)):
                toReturn.append(IFS_Transform.ofDict(loaded[str(i)]))
            
            print("Loaded " + str(len(toReturn)) + " transforms from " + fileDir)
        except Exception as e:
            print("Error reading JSON file. " + str(e) + "\n" + traceback.format_exc())
        
        return toReturn
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
        
        if len(self.transforms) == 0:
            return
        
        try:
            self.initializePixels()
            
            self.point = (random.random(), random.random())
            
            self.skips = 0
            
            # print("Start point: " + str(self.point))

            self.minX = None
            self.maxX = None
            self.minY = None
            self.maxY = None
            
            self.plot.resizeImage(self.PIX_WIDTH, self.PIX_HEIGHT)
            img = self.plot.getImage()
            img.put(colorRGB(28, 51, 5), to = (0, 0, img.width(), img.height()))

            # Transient iterations to converge before checking min and max
            for i in range(100):
                self.iterate(False, False)
            
            # print("Point after head start: " + str(self.point))
            
            # For getting min and max
            for e in range(10000):
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
            
            # Rotate every pixel by 45 degrees using the width and height
            import copy
            pixCopy = copy.deepcopy(self.pixels)
            for x in range(self.PIX_WIDTH):
                for y in range(self.PIX_HEIGHT):
                    self.pixels[x][y] = pixCopy[y][x]
            
            img.put(self.pixels, (0, 0))
            
            self.plot.setImage(img)
            self.plot.resizeImage(self.WIDTH - 64, self.PLOT_HEIGHT - 64)
            self.plot.draw()
            
            # Keep overlay above plot
            self.mainCanvas.lift(self.plotOverlay.id, self.plot.id)
            
            print("Skips: " + str(self.skips))
        except Exception as e:
            print("Error plotting IFS: " + str(e) + " stack: " + str(traceback.format_exc()))
        
        gc.collect()
    
    # Choose a random transform using its probability
    def chooseTransform(self):
        weights = [t.probability() for t in self.transforms]
        try:
            return random.choices(self.transforms, weights = weights)[0].transform
        except:
            print("Error choosing transform")
            return random.choice(self.transforms).transform
    
    skips = 0
    
    # Iterate the IFS system
    def iterate(self, shouldPlot, checkMinMax):
        # Choose a random transformation for this iteration, uses the probabilities of each transformation
        randTransform = self.chooseTransform()
        
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
            else:
                self.skips += 1
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
        try:
            x = self.PIX_WIDTH - remap(x, self.minX, self.maxX, self.drawPadding[0], self.PIX_WIDTH - self.drawPadding[0] * 2)
            y = self.PIX_HEIGHT - remap(y, self.minY, self.maxY, self.drawPadding[1], self.PIX_HEIGHT - self.drawPadding[1] * 2)
        except:
            return (-1, -1)
            # print("max1 - min1: " + str(self.maxX - self.minX) + ", max1: " + str(self.maxX) + ", min1: " + str(self.minX))

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
    # Show a help window with info about the program
    def help(self):
        print("Showing help")
        
        helpBoxes = [
                    ("Hello there! Our sensors detect that this is the first time you are powering on this device.\n\nThis is the IFS EXPLORER 2000™®© - A never before seen handheld, portable, and powerful tool used for exploring the IFS world.\n\nThis user manual will show you how to use this state-of-the-art tool that lets you explore the beauty and intricacies of Iterated Function Systems and teach you about the incredible things you can do with this device. All buttons, switches, and screens on this tool have tooltips, just hover your finger over something to get a better understanding of what it does.\n\n(WARNING: If you attempt to disassemble this device then our hitmen will be informed of your location and the device will self destruct)", self.win, (self.WIDTH / 2 - 150, self.HEIGHT / 2 - 200)),
                    ("If you would like to re-open this user manual, click the green help button.", self.helpButton, (-300, 50)),
                    ("If you would like to turn off the device, click the red power button.", self.quitButton, (-300, 50)),
                    ("The large glass panel in the center of this tool is called the ScreenTron 6000®. Featuring a massive 3 inch OLED display, this tool has the largest screen in the industry. The ScreenTron 6000® displays to you in high-resolution the IFS system you are currently drawing.", self.win, (self.WIDTH / 2 - 150, self.HEIGHT / 2 - 100)),
                    ("The striped metal panel near the bottom left of this device is called the Multidimensional Transform Instance Manipulator. This lets you tap into the intergalactic energy fields and change the parameters of each individual transform in the IFS you are currently plotting.", self.buttonsPanel, (60, 0)),
                    ("This button adds a new transform to the IFS system.", self.newButton, (25, -90)),
                    ("This button saves the current IFS system to a json file.", self.saveButton, (25, -90)),
                    ("This button loads an IFS system from a json file.\nYou have the choice of a wide variety of handcrafted and (relatively) high quality pre-made IFS systems.\n\nNOTE: Since these presets were not made by me, some might not function properly with this device due to error in translating the two file formats.\n\nThese systems were sourced from the ifs files on the website: https://larryriddle.agnesscott.org/ifskit/gallery/gallery.htm", self.loadButton, (25, -170)),
                    ("This button clears the current IFS system.", self.clearButton, (25, -75)),
                    ("The long metal panel at the bottom right of the device is the Transform Flux Editor. This allows you to see individual transforms, change their values, or remove them. You can scroll your mouse wheel anywhere on the device to scroll through this list. You may notice that there already are a bunch of transforms listed. This is because, upon being turned on, the device intelligently picks out a random preset transform from the folder called Transforms located at this classpath directory on the device's Quantum Entangulator Memory.", self.rightPanel, (-300, -80)),
                    ("Each panel in this list represents one transform. It contains the parameters for each value of a transform.", self.transforms[0], (-80, -110)),
                    ("This button updates the IFS graph with its new values.", self.transforms[0].updateButton, (20, -85)),
                    ("This input lets you change the x scale of the transform.", self.transforms[0].rInput, (-290, -85)),
                    ("This input lets you change the y scale of the transform.", self.transforms[0].sInput, (-290, -85)),
                    ("This input lets you change the x shift of the transform.", self.transforms[0].hInput, (-280, -85)),
                    ("This input lets you change the y shift of the transform.", self.transforms[0].kInput, (-280, -85)),
                    ("This input lets you change the theta of the transform.", self.transforms[0].thetaInput, (-275, -85)),
                    ("This input lets you change the probability of the transform being selected when drawing the IFS.", self.transforms[0].probabilityInput, (-305, -85)),
                    ("Click this box to select the color of the transform.", self.transforms[0].colorInput, (-300, -70)),
                    ("This button removes this transform from the transform list.", self.transforms[0].removeButton, (20, -85)),
                    ("That the last page of the user manual! If you need to re-open this user manual, press the green help button on the top right corner of the device.", self.win, (self.WIDTH / 2 - 150, self.HEIGHT / 2 - 75))
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
            # if self.helpBoxIndex >= 1:
            #     # Check target widget type
            #     if isinstance(helpBoxes[self.helpBoxIndex][1], HideableFrame):
            #         helpBoxes[self.helpBoxIndex][1].showHideButton.config(highlightthickness = 0)
            #     else:
            #         helpBoxes[self.helpBoxIndex][1].config(highlightthickness = 0)
            
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
            # if self.helpBoxIndex >= 1:
            #     # Check target widget type
            #     data[1].setOutline('red')
            #     data[1].setOutlineThickness(5)
            
            # Next button text
            if self.helpBoxIndex >= len(helpBoxes) - 1:
                # self.temp.destroy()
                nextText = "Close User Manual"
            else:
                nextText = "Next Page"
            
            # Create a popup with the text and position it next to the widget with the desired offset
            self.helpBox = Popup(data[1], text = data[0], closeButtonText = nextText, xOffset = data[2][0], yOffset = data[2][1], font = (PRIMARY, 50, NORMAL))
            self.helpBox.show()
            self.helpBox.registerCloseCommand(nextHelpBox)
        
        nextHelpBox()
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
        
        self.title = self.create_text(45, 10, text = str(self.index + 1), anchor = "nw", font = ("Small Fonts", 40, BOLD), fill = "white")
        
        self.rInput = GraphicsFloatBox(31, 25, 34, 20, self.main.getImage("sunken box"), self.transform.getR(), tooltipText = "X Scale")
        self.rInput.draw()
        self.sInput = GraphicsFloatBox(68, 25, 34, 20, self.main.getImage("sunken box"), self.transform.getS(), tooltipText = "Y Scale")
        self.sInput.draw()
        
        self.hInput = GraphicsFloatBox(31, 45, 34, 20, self.main.getImage("sunken box"), self.transform.getE(), tooltipText = "X Shift")
        self.hInput.draw()
        self.kInput = GraphicsFloatBox(68, 45, 34, 20, self.main.getImage("sunken box"), self.transform.getF(), tooltipText = "Y Shift")
        self.kInput.draw()
        
        self.thetaInput = GraphicsFloatBox(31, 65, 34, 20, self.main.getImage("sunken box"), self.transform.getTheta(), tooltipText = "Theta")
        self.thetaInput.draw()
        self.probabilityInput = GraphicsFloatBox(68, 65, 34, 20, self.main.getImage("sunken box"), self.transform.getProb(), tooltipText = "Probability")
        self.probabilityInput.draw()
        
        self.colorInput = GraphicsSwatch(68 - 6, 85 + 2, 12, 12, self.transform.getColor(), tooltipText = "Transform Color")
        self.colorInput.draw()

        # Remove button
        self.removeButton = GraphicsButton(3, 3, self.main.getImage("x button up"), self.main.getImage("x button down"), width = 20, height = 20, command = lambda: self.main.removeTransform(self.index), tooltipText = "Remove transform", scale = self.main.UI_SCALING)
        self.removeButton.draw()

        # Update button
        self.updateButton = GraphicsButton(31, 85, self.a, self.b, width = 20, height = 20, command = self.updateTransform, tooltipText = "Update transform", scale = self.main.UI_SCALING)
        self.updateButton.draw()

    def updateTransform(self):
        print("Before update " + str(self.transform))
        self.transform = IFS_Transform(self.rInput.value, self.sInput.value, self.thetaInput.value, self.thetaInput.value, self.hInput.value, self.kInput.value, self.probabilityInput.value, self.colorInput.getColor())
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

    def setIndex(self, index):
        self.index = index
        self.itemconfig(self.title, text = str(self.index + 1))

if __name__ == "__main__":
    IFSExplorer()