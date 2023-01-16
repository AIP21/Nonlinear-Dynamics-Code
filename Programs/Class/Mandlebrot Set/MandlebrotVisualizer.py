import array
import random
import struct
import time
from Lib.NewDEGraphics import *
import Lib.NewDEGraphics as ndg
import threading
import math
import numpy as np
from PIL import Image

class MandlebrotSetExplorer():
    width = 1000
    height = 500

    renderSize = (1000, 1000) # The size of the image to render in pixels
    computeThreads = 32 # The number of threads to use for computing the mandlebrot's set
    iterations = 100 # The iterations of the mandlebrot set used when drawing
    drawMethod = 2 # The method to use. 1 = threshold, 2 = smooth

    backgroundColor = (0, 0, 0)

    # A map of rgb points in your distribution
    # [distance, (r, g, b)]
    # distance is percentage from left edge
    colorMap = [
        [0.00, (0, 0, 0)],
        [0.20, (0, 0, 127)],
        [0.40, (0, 127, 0)],
        [0.60, (127, 0, 0)],
        [0.80, (191, 191, 0)],
        [0.90, (255, 191, 0)],
        [1.00, (255, 255, 255)],
    ]

    customCoords = [-2.25, -1.5, 0.75, 1.5] # The region of the mandlebrot set to draw
    
    def main(self):
        # Create a window
        self.mainWin = DEGraphWin("Mandlebrot's Set Visualizer", width = self.width, height = self.height)
        
        # Prevent an error
        self.dgImg = None
    
        imageWidth = int(self.width * 0.4)
        rightSideWidth = int(self.width * 0.2)

        # Create the main ui layout
        with self.mainWin:
            with Flow(background = "black", width = self.width, height = self.height):
                self.mandlebrotSetFrame = Stack(background = "orange")
                with self.mandlebrotSetFrame:
                    Label("Mandlebrot Set")
                    ndg.Image("image.png", width = imageWidth, height = self.height)
                    
                self.juliaSetFrame = Stack(background = "yellow")
                with self.juliaSetFrame:
                    Label("Julia Set")
                    ndg.Image("image.png", width = imageWidth, height = self.height)
                    
                self.rightSideFrame = Stack(width = rightSideWidth, background = "green")
                with self.rightSideFrame:
                    # with Stack(width = rightSideWidth, background = "red"):
                    self.createControlPanel(rightSideWidth)

                    
                    # with Flow(width = rightSideWidth, background = "blue"):
                    #     Label("A")
                    #     Label("B")
    
    # Render the mandlebrot set to an image and display that image
    def renderMandlebrotSet(self):
        # Compute the mandlebrot's set
        print("Computing the mandlebrot's set")
        startTime = time.time() * 1000
        
        # Compute the mandlebrot set into an array of pixels
        # Split computation into threads
        pixelStep = self.renderSize[1] / self.computeThreads
        coordStep = (self.customCoords[3] - self.customCoords[1]) / self.computeThreads
        threads = []
        threadResults = []
        
        # Create the threads
        for threadNum in range(self.computeThreads):
            threadCustomCoords = [self.customCoords[0], self.customCoords[1] + (coordStep * threadNum), self.customCoords[2], self.customCoords[1] + (coordStep * (threadNum + 1))]
            threadSize = (self.renderSize[0], int(pixelStep * (threadNum + 1)) - int(pixelStep * threadNum))
            print(str(threadNum) + "'s custom coords: " + str(threadCustomCoords))
            print(str(threadNum) + "'s size: " + str(threadSize))
            thread = ThreadWithReturnValue(target = self.computeMandlebrotSet, args = (threadSize, threadCustomCoords, self.iterations, self.drawMethod, self.colorMap, self.backgroundColor))
            thread.start()
            threads.append(thread)
        
        for thread in threads:
            result = thread.join()
            threadResults.append(result.flatten())
        
        # Get the results of the threads into a pixels list
        pixels = np.concatenate(threadResults, axis = 0).flatten().tolist()
        
        print("Finished computing all values in: " + str((time.time() * 1000) - startTime) + "ms")
        startTime = time.time() * 1000
        
        # Draw the set to an image and then to the canvas
        print("Starting to draw the set to an image")
                
        image = Image.new("RGB", self.renderSize, self.backgroundColor)
        image.putdata(pixels)
        
        print(str(len(pixels)) + " pixels, image dimensions: " + str(image.size))
        
        image.save("image.png")
        
        print("Finished drawing to an image in: " + str((time.time() * 1000) - startTime) + "ms")
        
        # Display with an image widget
        # Draw the image to the canvas
        if self.dgImg != None:
            self.mainWin.remove(self.dgImg)
        
        self.dgImg = Image(0, 0, "image.png")
    
    # Computes the mandlebrot set and returns it's colors
    def computeMandlebrotSet(self, size, customCoords, maxIterations, method, colorGradient, backgroundColor = (0, 0, 0), color = (255, 255, 255)):
        # Calculate mandlebrot's set into an array using numpy, using vEcToRiZaTiOn
        rMin = customCoords[0]
        rMax = customCoords[2]
        iMin = customCoords[1]
        iMax = customCoords[3]
        
        startTime = time.time() * 1000
        
        # Create ALL the x and y values
        x = np.linspace(rMin, rMax, size[0]).reshape((1, size[0]))
        y = np.linspace(iMin, iMax, size[1]).reshape((size[1], 1))
        
        # Create ALL the complex numbers
        c = x + 1j * y
        
        # Initialize z to ALL be zero
        z = np.zeros(c.shape, dtype = np.complex128)
        
        # Keep track in which iteration the points diverged
        pixels = np.zeros((size[1], size[0]), dtype='i,i,i')
        pixels.fill(backgroundColor)
        
        # Keep track on which points did not converge so far
        m = np.full(c.shape, True, dtype = bool)
        for i in range(maxIterations):
            z[m] = z[m] ** 2 + c[m]
            diverged = np.greater(np.abs(z), 2, out = np.full(c.shape, False), where = m) # Find diverging
                        
            if method == 1:
                # Threshold coloring
                pixels[diverged] = color
            elif method == 2:
                # Smooth coloring
                pixels[diverged] = getGradientColorTuple(i, maxIterations, colorGradient)

            # Remember which have diverged
            m[np.abs(z) > 2] = False
        
        print("Finished computing a thread in: " + str((time.time() * 1000) - startTime) + "ms")
        
        return pixels

    # Compute the Julia set and return it's colors
    def computeJuliaSet(self, currentJuliaC):
        pixels = []
        
        z = complex(20 * random(), 20 * random())
        for n in range(10000):
            z = (z - currentJuliaC) ** 0.5
            if (random() < 0.5):
                z *= -1
        
        for n in range(10000):
            z = (z - currentJuliaC) ** 0.5
            if (random() < 0.5):
                z *= -1
            pixels.append(z.real, z.imag)

    # Create the control panel elements
    def createControlPanel(self, panelWidth):
        Label("Controls", width = panelWidth)
        
        Button(text = "Render", width = panelWidth * 0.9, height = 40, cornerRadius = 10, command = self.renderMandlebrotSet)
        
        Button(text = "Quit", width = panelWidth * 0.9, height = 40, cornerRadius = 10, command = self.close)
        
        with Stack():
            Label("Threads: ")
            threadsEntry = TextBox()
            
        # Label("Iterations: ")
        # iterationsEntry = TextBox()
        # Label("Method: ")
        # methodEntry = TextBox()
        # Label("Background color: ")
        # with Stack():
        #     backgroundREntry = TextBox()
        #     backgroundGEntry = TextBox()
        #     backgroundBEntry = TextBox()
        # Label("Color map: ")
        # with Stack():
        #     colorMapEntry = TextBox()
        # Label("Custom coords: ")
        # with Stack():
        #     customCoordsX1Entry = TextBox()
        #     customCoordsY1Entry = TextBox()
        #     customCoordsX2Entry = TextBox()
        #     customCoordsY2Entry = TextBox()

    # Custom close behavior callback
    def close(self):
        self.mainWin.destroy()
        safeExit = True
        exit()

#region Utils
def remap(value, min1, max1, min2, max2) -> float:
    return min2 + (value - min1) * (max2 - min2) / (max1 - min1)

def lerpColor(color1, color2, amount):
    r = int(lerp(amount, color1[0], color2[0]))
    g = int(lerp(amount, color1[1], color2[1]))
    b = int(lerp(amount, color1[2], color2[2]))
    return (r, g, b)

def lerp(val, a, b) -> float:
    return a + (b - a) * val

def inverseLerp(val, a, b) -> float:
    return (val - a) / (b - a)

def gaussian(x, a, b, c, d = 0):
    return a * math.exp(-(x - b) ** 2 / (2 * c ** 2)) + d

def getGradientColorTuple(val, maxVal, gradient, spread = 1):
    maxVal = float(maxVal)
    div = maxVal / (spread * len(gradient))
    r = sum([gaussian(val, p[1][0], p[0] * maxVal, div) for p in gradient])
    g = sum([gaussian(val, p[1][1], p[0] * maxVal, div) for p in gradient])
    b = sum([gaussian(val, p[1][2], p[0] * maxVal, div) for p in gradient])
    return min(255, r), min(255, g), min(255, b)

# https://en.wikipedia.org/wiki/Fast_inverse_square_root
def fastInverseSqrt(number):
    threehalfs = 1.5
    x2 = number * 0.5
    y = number
    
    packed_y = struct.pack('f', y)
    i = struct.unpack('i', packed_y)[0]  # evil floating point bit level hacking
    i = 0x5f3759df - (i >> 1)            # what the fuck?
    packed_i = struct.pack('i', i)
    y = struct.unpack('f', packed_i)[0]  # treat int bytes as float
    
    y = y * (threehalfs - (x2 * y * y))  # newtons method
    return y

class ThreadWithReturnValue(threading.Thread):
    def __init__(self, group = None, target = None, name = None, args = (), kwargs = {}, Verbose = None):
        threading.Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args,  **self._kwargs)
            
    def join(self, *args):
        threading.Thread.join(self, *args)
        return self._return
    #endregion

# Run the program
if __name__ == "__main__":
    app = MandlebrotSetExplorer()
    app.main()