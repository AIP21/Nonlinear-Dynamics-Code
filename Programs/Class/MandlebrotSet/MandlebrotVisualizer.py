import array
import os
import random
import struct
import time
from Lib.NewDEGraphics import *
import Lib.NewDEGraphics as ndg
import threading
import math
import numpy as np

# from Lib.Sound.playsound import playsound
# import wave

# try:
#     import winsound
#     import sounddevice
    
#     nativeSound = False
# except:
#     nativeSound = True

class MandlebrotSetExplorer():
    width = 1350
    height = 750

    renderSize = (500, 500) # The size of the image to render in pixels
    computeThreads = 16 # The number of threads to use for computing
    renderSweeps = 4 # The number of sweeps to use when rendering

    mandlebrotIterations = 100 # The iterations of the mandlebrot set used when drawing
    mandlebrotDrawMethod = 2 # The method to use to draw the mandlebrot set. 1 = threshold, 2 = smooth, 3 = gaussian coloring, 4 = random colors (very cool looking)
    mandlebrotSounds = False
    SAMPLE_RATE = 44100 # The sample rate for mandlebrot sounds (don't touch)
    
    juliaIterations = 100 # The iterations of the julia set used when drawing
    juliaDrawMethod = 2 # The method to use to draw the julia set. 1 = threshold, 2 = smooth, 3 = random colors (very cool looking)
    autoComputeJuliaSet = False

    backgroundColor = (0, 0, 0)
    
    mandlebrotRendered = False
    juliaRendered = False
    mandlebrotBeingDrawn = False
    juliaBeingDrawn = False
    
    isZooming = False
    
    exiting = False
    
    #region Color Maps
    # A map of rgb points in your distribution
    # [distance, (r, g, b)]
    # distance is percentage from left edge
    colorMap = [(0.001462, 0.000466, 0.013866),
               (0.002258, 0.001295, 0.018331),
               (0.003279, 0.002305, 0.023708),
               (0.004512, 0.003490, 0.029965),
               (0.005950, 0.004843, 0.037130),
               (0.007588, 0.006356, 0.044973),
               (0.009426, 0.008022, 0.052844),
               (0.011465, 0.009828, 0.060750),
               (0.013708, 0.011771, 0.068667),
               (0.016156, 0.013840, 0.076603),
               (0.018815, 0.016026, 0.084584),
               (0.021692, 0.018320, 0.092610),
               (0.024792, 0.020715, 0.100676),
               (0.028123, 0.023201, 0.108787),
               (0.031696, 0.025765, 0.116965),
               (0.035520, 0.028397, 0.125209),
               (0.039608, 0.031090, 0.133515),
               (0.043830, 0.033830, 0.141886),
               (0.048062, 0.036607, 0.150327),
               (0.052320, 0.039407, 0.158841),
               (0.056615, 0.042160, 0.167446),
               (0.060949, 0.044794, 0.176129),
               (0.065330, 0.047318, 0.184892),
               (0.069764, 0.049726, 0.193735),
               (0.074257, 0.052017, 0.202660),
               (0.078815, 0.054184, 0.211667),
               (0.083446, 0.056225, 0.220755),
               (0.088155, 0.058133, 0.229922),
               (0.092949, 0.059904, 0.239164),
               (0.097833, 0.061531, 0.248477),
               (0.102815, 0.063010, 0.257854),
               (0.107899, 0.064335, 0.267289),
               (0.113094, 0.065492, 0.276784),
               (0.118405, 0.066479, 0.286321),
               (0.123833, 0.067295, 0.295879),
               (0.129380, 0.067935, 0.305443),
               (0.135053, 0.068391, 0.315000),
               (0.140858, 0.068654, 0.324538),
               (0.146785, 0.068738, 0.334011),
               (0.152839, 0.068637, 0.343404),
               (0.159018, 0.068354, 0.352688),
               (0.165308, 0.067911, 0.361816),
               (0.171713, 0.067305, 0.370771),
               (0.178212, 0.066576, 0.379497),
               (0.184801, 0.065732, 0.387973),
               (0.191460, 0.064818, 0.396152),
               (0.198177, 0.063862, 0.404009),
               (0.204935, 0.062907, 0.411514),
               (0.211718, 0.061992, 0.418647),
               (0.218512, 0.061158, 0.425392),
               (0.225302, 0.060445, 0.431742),
               (0.232077, 0.059889, 0.437695),
               (0.238826, 0.059517, 0.443256),
               (0.245543, 0.059352, 0.448436),
               (0.252220, 0.059415, 0.453248),
               (0.258857, 0.059706, 0.457710),
               (0.265447, 0.060237, 0.461840),
               (0.271994, 0.060994, 0.465660),
               (0.278493, 0.061978, 0.469190),
               (0.284951, 0.063168, 0.472451),
               (0.291366, 0.064553, 0.475462),
               (0.297740, 0.066117, 0.478243),
               (0.304081, 0.067835, 0.480812),
               (0.310382, 0.069702, 0.483186),
               (0.316654, 0.071690, 0.485380),
               (0.322899, 0.073782, 0.487408),
               (0.329114, 0.075972, 0.489287),
               (0.335308, 0.078236, 0.491024),
               (0.341482, 0.080564, 0.492631),
               (0.347636, 0.082946, 0.494121),
               (0.353773, 0.085373, 0.495501),
               (0.359898, 0.087831, 0.496778),
               (0.366012, 0.090314, 0.497960),
               (0.372116, 0.092816, 0.499053),
               (0.378211, 0.095332, 0.500067),
               (0.384299, 0.097855, 0.501002),
               (0.390384, 0.100379, 0.501864),
               (0.396467, 0.102902, 0.502658),
               (0.402548, 0.105420, 0.503386),
               (0.408629, 0.107930, 0.504052),
               (0.414709, 0.110431, 0.504662),
               (0.420791, 0.112920, 0.505215),
               (0.426877, 0.115395, 0.505714),
               (0.432967, 0.117855, 0.506160),
               (0.439062, 0.120298, 0.506555),
               (0.445163, 0.122724, 0.506901),
               (0.451271, 0.125132, 0.507198),
               (0.457386, 0.127522, 0.507448),
               (0.463508, 0.129893, 0.507652),
               (0.469640, 0.132245, 0.507809),
               (0.475780, 0.134577, 0.507921),
               (0.481929, 0.136891, 0.507989),
               (0.488088, 0.139186, 0.508011),
               (0.494258, 0.141462, 0.507988),
               (0.500438, 0.143719, 0.507920),
               (0.506629, 0.145958, 0.507806),
               (0.512831, 0.148179, 0.507648),
               (0.519045, 0.150383, 0.507443),
               (0.525270, 0.152569, 0.507192),
               (0.531507, 0.154739, 0.506895),
               (0.537755, 0.156894, 0.506551),
               (0.544015, 0.159033, 0.506159),
               (0.550287, 0.161158, 0.505719),
               (0.556571, 0.163269, 0.505230),
               (0.562866, 0.165368, 0.504692),
               (0.569172, 0.167454, 0.504105),
               (0.575490, 0.169530, 0.503466),
               (0.581819, 0.171596, 0.502777),
               (0.588158, 0.173652, 0.502035),
               (0.594508, 0.175701, 0.501241),
               (0.600868, 0.177743, 0.500394),
               (0.607238, 0.179779, 0.499492),
               (0.613617, 0.181811, 0.498536),
               (0.620005, 0.183840, 0.497524),
               (0.626401, 0.185867, 0.496456),
               (0.632805, 0.187893, 0.495332),
               (0.639216, 0.189921, 0.494150),
               (0.645633, 0.191952, 0.492910),
               (0.652056, 0.193986, 0.491611),
               (0.658483, 0.196027, 0.490253),
               (0.664915, 0.198075, 0.488836),
               (0.671349, 0.200133, 0.487358),
               (0.677786, 0.202203, 0.485819),
               (0.684224, 0.204286, 0.484219),
               (0.690661, 0.206384, 0.482558),
               (0.697098, 0.208501, 0.480835),
               (0.703532, 0.210638, 0.479049),
               (0.709962, 0.212797, 0.477201),
               (0.716387, 0.214982, 0.475290),
               (0.722805, 0.217194, 0.473316),
               (0.729216, 0.219437, 0.471279),
               (0.735616, 0.221713, 0.469180),
               (0.742004, 0.224025, 0.467018),
               (0.748378, 0.226377, 0.464794),
               (0.754737, 0.228772, 0.462509),
               (0.761077, 0.231214, 0.460162),
               (0.767398, 0.233705, 0.457755),
               (0.773695, 0.236249, 0.455289),
               (0.779968, 0.238851, 0.452765),
               (0.786212, 0.241514, 0.450184),
               (0.792427, 0.244242, 0.447543),
               (0.798608, 0.247040, 0.444848),
               (0.804752, 0.249911, 0.442102),
               (0.810855, 0.252861, 0.439305),
               (0.816914, 0.255895, 0.436461),
               (0.822926, 0.259016, 0.433573),
               (0.828886, 0.262229, 0.430644),
               (0.834791, 0.265540, 0.427671),
               (0.840636, 0.268953, 0.424666),
               (0.846416, 0.272473, 0.421631),
               (0.852126, 0.276106, 0.418573),
               (0.857763, 0.279857, 0.415496),
               (0.863320, 0.283729, 0.412403),
               (0.868793, 0.287728, 0.409303),
               (0.874176, 0.291859, 0.406205),
               (0.879464, 0.296125, 0.403118),
               (0.884651, 0.300530, 0.400047),
               (0.889731, 0.305079, 0.397002),
               (0.894700, 0.309773, 0.393995),
               (0.899552, 0.314616, 0.391037),
               (0.904281, 0.319610, 0.388137),
               (0.908884, 0.324755, 0.385308),
               (0.913354, 0.330052, 0.382563),
               (0.917689, 0.335500, 0.379915),
               (0.921884, 0.341098, 0.377376),
               (0.925937, 0.346844, 0.374959),
               (0.929845, 0.352734, 0.372677),
               (0.933606, 0.358764, 0.370541),
               (0.937221, 0.364929, 0.368567),
               (0.940687, 0.371224, 0.366762),
               (0.944006, 0.377643, 0.365136),
               (0.947180, 0.384178, 0.363701),
               (0.950210, 0.390820, 0.362468),
               (0.953099, 0.397563, 0.361438),
               (0.955849, 0.404400, 0.360619),
               (0.958464, 0.411324, 0.360014),
               (0.960949, 0.418323, 0.359630),
               (0.963310, 0.425390, 0.359469),
               (0.965549, 0.432519, 0.359529),
               (0.967671, 0.439703, 0.359810),
               (0.969680, 0.446936, 0.360311),
               (0.971582, 0.454210, 0.361030),
               (0.973381, 0.461520, 0.361965),
               (0.975082, 0.468861, 0.363111),
               (0.976690, 0.476226, 0.364466),
               (0.978210, 0.483612, 0.366025),
               (0.979645, 0.491014, 0.367783),
               (0.981000, 0.498428, 0.369734),
               (0.982279, 0.505851, 0.371874),
               (0.983485, 0.513280, 0.374198),
               (0.984622, 0.520713, 0.376698),
               (0.985693, 0.528148, 0.379371),
               (0.986700, 0.535582, 0.382210),
               (0.987646, 0.543015, 0.385210),
               (0.988533, 0.550446, 0.388365),
               (0.989363, 0.557873, 0.391671),
               (0.990138, 0.565296, 0.395122),
               (0.990871, 0.572706, 0.398714),
               (0.991558, 0.580107, 0.402441),
               (0.992196, 0.587502, 0.406299),
               (0.992785, 0.594891, 0.410283),
               (0.993326, 0.602275, 0.414390),
               (0.993834, 0.609644, 0.418613),
               (0.994309, 0.616999, 0.422950),
               (0.994738, 0.624350, 0.427397),
               (0.995122, 0.631696, 0.431951),
               (0.995480, 0.639027, 0.436607),
               (0.995810, 0.646344, 0.441361),
               (0.996096, 0.653659, 0.446213),
               (0.996341, 0.660969, 0.451160),
               (0.996580, 0.668256, 0.456192),
               (0.996775, 0.675541, 0.461314),
               (0.996925, 0.682828, 0.466526),
               (0.997077, 0.690088, 0.471811),
               (0.997186, 0.697349, 0.477182),
               (0.997254, 0.704611, 0.482635),
               (0.997325, 0.711848, 0.488154),
               (0.997351, 0.719089, 0.493755),
               (0.997351, 0.726324, 0.499428),
               (0.997341, 0.733545, 0.505167),
               (0.997285, 0.740772, 0.510983),
               (0.997228, 0.747981, 0.516859),
               (0.997138, 0.755190, 0.522806),
               (0.997019, 0.762398, 0.528821),
               (0.996898, 0.769591, 0.534892),
               (0.996727, 0.776795, 0.541039),
               (0.996571, 0.783977, 0.547233),
               (0.996369, 0.791167, 0.553499),
               (0.996162, 0.798348, 0.559820),
               (0.995932, 0.805527, 0.566202),
               (0.995680, 0.812706, 0.572645),
               (0.995424, 0.819875, 0.579140),
               (0.995131, 0.827052, 0.585701),
               (0.994851, 0.834213, 0.592307),
               (0.994524, 0.841387, 0.598983),
               (0.994222, 0.848540, 0.605696),
               (0.993866, 0.855711, 0.612482),
               (0.993545, 0.862859, 0.619299),
               (0.993170, 0.870024, 0.626189),
               (0.992831, 0.877168, 0.633109),
               (0.992440, 0.884330, 0.640099),
               (0.992089, 0.891470, 0.647116),
               (0.991688, 0.898627, 0.654202),
               (0.991332, 0.905763, 0.661309),
               (0.990930, 0.912915, 0.668481),
               (0.990570, 0.920049, 0.675675),
               (0.990175, 0.927196, 0.682926),
               (0.989815, 0.934329, 0.690198),
               (0.989434, 0.941470, 0.697519),
               (0.989077, 0.948604, 0.704863),
               (0.988717, 0.955742, 0.712242),
               (0.988367, 0.962878, 0.719649),
               (0.988033, 0.970012, 0.727077),
               (0.987691, 0.977154, 0.734536),
               (0.987387, 0.984288, 0.742002),
               (0.987053, 0.991438, 0.749504)]
    #endregion

    mandlebrotCustomCoords = [-2.25, -1.5, 0.75, 1.5] # The region of the mandlebrot set to draw
    juliaCustomCoords = [-2.25, -1.5, 2.25, 1.5] # The region of the julia set to draw
    
    orbitLinePool = [] # A pool of lines for drawing orbits
    orbitEllipsePool = [] # A pool of ellipses for drawing orbits
    
    bookmarks = []
    
    def main(self):
        # Create a window
        self.mainWin = DEGraphWin("Mandlebrot Explorer", width = self.width, height = self.height)
        self.mainWin.protocol("WM_DELETE_WINDOW", self.close)
        
        # Fill the pools
        for i in range(0, 50):
            self.orbitLinePool.append(Line(None, 0, 0, 0, 0, 'red'))
            self.orbitEllipsePool.append(Ellipse(None, 0, 0, 0, 0, 'red'))
        
        # Prevent an error
        self.dgImg = None
        self.clickedPointPixel = None
        self.clickedPoint = None
        self.orbitDrawThread = None
        self.mandlebrotRenderThread = None
        self.juliaRenderThread = None
    
        self.imageWidth = int(self.width * 0.4)
        rightSideWidth = int(self.width * 0.2)
        
        # Create the main ui layout
        with self.mainWin:
            with Stack():
                title = Label("Mandlebrot Explorer", width = self.width, font = "Arial 16 bold")
                subtitle = Label("By: Alexander Irausquin-Petit", width = self.width, font = "Arial 10 bold")
            
                with Flow():
                    mandlebrotFrame = Stack()
                    with mandlebrotFrame:
                        with Flow():
                            Label("Mandlebrot Set", width = 25)
                            
                            recenterMB = Button(text = "Recenter", width = 70, height = 22, padding = 3, cornerRadius = 10, textFont = "Arial 8 bold", command = self.recenterMandlebrotSet)
                            recenterMB.setHoverEffect(("grow/darken", (4, 4, (50, 50, 50))))
                            
                            self.zoomMandlebrotButton = Button(text = "Zoom", width = 50, height = 22, padding = 3, cornerRadius = 10, textFont = "Arial 8 bold", command = self.zoom)
                            self.zoomMandlebrotButton.setHoverEffect(("grow/darken", (4, 4, (50, 50, 50))))
                            
                            self.addBookmarkButton = Button(text = "+ Bookmark", width = 100, height = 22, padding = 3, cornerRadius = 10, textFont = "Arial 8 bold", command = self.addBookmark)
                            self.addBookmarkButton.setHoverEffect(("grow/darken", (4, 4, (50, 50, 50))))
                            self.addBookmarkButton.disable()
                            
                            self.showBookmarksButton = Button(text = "Bookmarks", width = 100, height = 22, padding = 3, cornerRadius = 10, textFont = "Arial 8 bold", command = self.showBookmarks)
                            self.showBookmarksButton.setHoverEffect(("grow/darken", (4, 4, (50, 50, 50))))
                        
                        self.mandlebrotSet = Plot(height = self.height - 200, width = self.imageWidth, background = "black")
                        self.mandlebrotSet.selectionMaintainAspectRatio = True
                        self.mandlebrotSet.enableSelectionBox = False
                        self.mandlebrotSet.setOnClickDown(self.mandlebrotSetClicked)
                        self.mandlebrotSet.setOnClickUp(self.mandlebrotSetZoomed)
                        self.mandlebrotSet.setOnDrag(self.mandlebrotSetDragged)

                        self.mandlebrotStatusText = Label("Click draw to render the mandlebrot set")
                        
                        self.mandlebrotProgress = ProgressBar(0, 100, 0, width = self.imageWidth, height = 30)
                    
                    juliaFrame = Stack()
                    with juliaFrame:
                        with Flow():
                            Label("Julia Set", width = 50)
                            recenterJulia = Button(text = "Recenter", width = 70, height = 22, padding = 3, cornerRadius = 10, textFont = "Arial 8 bold", command = self.recenterJuliaSet)
                            recenterJulia.setHoverEffect(("grow/darken", (4, 4, (50, 50, 50))))
                            
                            self.zoomJuliaButton = Button(text = "Zoom", width = 50, height = 22, padding = 3, cornerRadius = 10, textFont = "Arial 8 bold", command = self.zoom)
                            self.zoomJuliaButton.setHoverEffect(("grow/darken", (4, 4, (50, 50, 50))))
                            
                        self.juliaSet = Plot(height = self.height - 200, width = self.imageWidth, background = "black")
                        self.mandlebrotSet.selectionMaintainAspectRatio = True
                        self.juliaSet.enableSelectionBox = False
                        self.juliaSet.setOnClickDown(self.juliaSetClicked)
                        self.juliaSet.setOnClickUp(self.juliaSetZoomed)
                        self.juliaSet.setOnDrag(self.juliaSetDragged)
                        
                        self.juliaStatusText = Label("Click anywhere on the mandlebrot set to draw the julia set")
                    
                        self.juliaProgress = ProgressBar(0, 100, 0, width = self.imageWidth, height = 30)
                    
                    self.rightSideFrame = Stack(height = self.height)
                    with self.rightSideFrame:
                        quitButton = Button(text = "Quit", color = (240, 75, 75), width = rightSideWidth * 0.9, height = 40, cornerRadius = 10, command = self.close)
                        Tooltip(quitButton, "Quit the program (duh)")
                        
                        self.createControlPanel(rightSideWidth)
        
        self.mainWin.update()
    
    #region Rendering and computation
    
    ##### Mandlebrot Set Functions #####
    
    # Draw the mandlebrot set (called by the draw button)
    def drawMandlebrotSet(self):
        if self.mandlebrotBeingDrawn:
            return
        
        # Set status text and progress bar
        self.mandlebrotStatusText.text = "Computing..."
        self.mandlebrotProgress.setValue(0)
        
        # Disable drawing the set again set while it is being drawn
        self.drawMandlebrotButton.disable()
        
        if self.mandlebrotRenderThread != None:
            self.mandlebrotRenderThread.stop()
                
        # Create and start the thread
        self.mandlebrotRenderThread = StoppableThread(name = "mandlebrotRenderThread", target = self.renderMandlebrotSet)
        self.mandlebrotRenderThread.start()
        
        self.mandlebrotBeingDrawn = True
    
    # Computes the mandlebrot set and returns it's colors
    def computeMandlebrotSet(self, size, customCoords, maxIterations):
        # Compute the mandlebrot set
        print("Computing the mandlebrot set")
        startTime = time.time()

        # Calculate mandlebrot set into an array using numpy, using vEcToRiZaTiOn
        rMin = customCoords[0]
        rMax = customCoords[2]
        iMin = customCoords[1]
        iMax = customCoords[3]

        # Create ALL the x and y values
        x,y = np.ogrid[rMin:rMax:size[0] * 1j, iMin:iMax:size[1] * 1j]

        # Create ALL the complex numbers
        c = x + (y * 1j)

        # Initialize z to ALL be zero
        z = np.zeros(c.shape, dtype = np.complex128)

        # Keep track of which points did not converge so far
        m = np.full(c.shape, True, dtype = bool)

        # Keep track in which iteration the points diverged
        divergenceTimes = maxIterations + np.zeros(z.shape, dtype = int)

        for i in range(maxIterations):
            # Iterate
            z[m] = z[m] ** 2 + c[m]
            
            # Find diverging
            diverging = np.greater(np.abs(z), 2, out = np.full(c.shape, False), where = m)

            # Find which diverged in this iteration
            diverged = np.logical_and(diverging, m)
            
            # Remember which have diverged
            m[np.abs(z) > 2] = False
            
            # Remember when they diverged
            divergenceTimes[diverged] = i
            
            self.mandlebrotProgress.setValue(lerp(i / maxIterations, 0, 100))

        diff = time.time() - startTime
        print("Finished computing the mandlebrot set in: " + str(diff) + "sec (" + str(diff * 1000) + "ms)")

        return divergenceTimes

    # Done on another thread to avoid freezing. Render mandlebrot data using a sweep algorithm
    def renderMandlebrotSet(self):
        # Compute the mandlebrot set
        computedData = self.computeMandlebrotSet(self.renderSize, self.mandlebrotCustomCoords, self.mandlebrotIterations)
        
        startTime = time.time()
        
        print("Rendering the mandlebrot set")
        
        self.mandlebrotStatusText.text = "Rendering..."
        self.mandlebrotProgress.setValue(0)
        
        self.mandlebrotSet.clear()
        
        totalPixelTime = 0
        rowLoop = 0
        
        # Sweep
        for sweep in range(self.renderSweeps):
            y = sweep
            
            # Go through every y value, with a step of sweeps
            while y < self.renderSize[1]:
                startLoop = time.time()
                
                # Track the color of every pixel on this row
                rowColors = []
                                
                # Go through every x value
                for x in range(self.renderSize[0]):
                    val = computedData[x][y]
                    
                    color = 'black'
                                    
                    pixelTime = time.time()
                    if self.mandlebrotDrawMethod == 1:
                        if val == self.mandlebrotIterations:
                            # Threshold coloring
                            color = 'white'
                    elif self.mandlebrotDrawMethod == 2:
                        if val != self.mandlebrotIterations:
                            # Gradient coloring
                            color = colorRGB(*getGradientColor(val / self.mandlebrotIterations, self.colorMap))
                    elif self.mandlebrotDrawMethod == 3:
                        if val != self.mandlebrotIterations:
                            # Wierd coloring
                            color = colorRGB(*getGradientColor((math.sin(val) + 1) / 2, self.colorMap))
                    
                    rowColors.append(color)
                    
                    totalPixelTime += time.time() - pixelTime
                
                # Append row pixel colors
                self.mandlebrotSet.plotBulk(0, y,  ("{" + str(rowColors)[1:-1].replace('\'', '').replace(',', '') + "} "))
                
                # Step the y value
                y += self.renderSweeps
                
                rowLoop += time.time() - startLoop
                
                # Progress using sweep and y value
                newProgress = lerp((sweep + (y / self.renderSize[1])) / self.renderSweeps, 0, 100)
                self.mandlebrotProgress.setValue(newProgress)
        
        # Print average times
        print("Average pixel time: " + str((totalPixelTime / (self.renderSize[0] * self.renderSize[1])) * 1000) + "ms")
        print("Total pixel time: " + str(totalPixelTime * 1000) + "ms")
        print("Average row loop time: " + str((rowLoop / self.renderSize[1]) * 1000) + "ms")
        print("Total row loop time: " + str(rowLoop * 1000) + "ms")
        
        diff = time.time() - startTime
        print("Finished rendering the mandlebrot set in: " + str(diff) + "sec (" + str(diff * 1000) + "ms)")
        
        self.mandlebrotRendered = True
        self.drawMandlebrotButton.enable()
        
        # Set status text
        self.mandlebrotStatusText.text = ""
        self.mandlebrotBeingDrawn = False
        self.mandlebrotProgress.setValue(0)
    
    
    ##### Orbit Functions #####
    
    # Compute the info (orbit, iterations, diverged) of a point in the mandlebrot set
    def computePointInfo(self, point, maxIterations):
        z = complex(0, 0)
        
        orbit = []
        for i in range(maxIterations):
            z = z ** 2 + point
            
            orbit.append(z)
            
            if abs(z) >= 2:
                return (orbit, i, True)
        
        return (orbit, maxIterations, False)

    # Constantly draws an orbit. Pools it's lines and ellipses for efficiency (yes)
    # Basically just lines between all the points in the orbit.
    # It also draws ellipses showing the points in the orbit.
    # This needs to be run in another thread!
    def drawOrbitPath(self):
        # Undraw all pooled lines and ellipses
        for line in self.orbitLinePool:
            line.setCanvas(self.mandlebrotSet)
            line.undraw()
        
        for ellipse in self.orbitEllipsePool:
            ellipse.setCanvas(self.mandlebrotSet)
            ellipse.undraw()
        
        def toneFromPoint(outdata: np.ndarray, frames: int, time, status) -> None:            
            # Write the sound data to two channels
            resultChannel1 = None
            resultChannel2 = None
            
            # Both channels
            t = (np.arange(frames)) / self.SAMPLE_RATE
            t = t.reshape(-1, 1)

            wave = np.sin(2 * np.pi * z.real * t)

            if resultChannel1 is None:
                resultChannel1 = wave
            else:
                resultChannel1 += wave

            wave2 = np.sin(2 * np.pi * z.imag * t)

            if resultChannel2 is None:
                resultChannel2 = wave2
            else:
                resultChannel2 += wave2

            # Normalize the result
            resultChannel1 /= max(abs(resultChannel1))
            resultChannel2 /= max(abs(resultChannel2))
            
            # Write the result to the output
            outdata[:, 0] = resultChannel1.flatten()
            outdata[:, 1] = resultChannel2.flatten()
        
        # Play a sound with the frequency of the point (left channel = real, right channel = imaginary)            
        # stream = sounddevice.OutputStream(channels = 2, blocksize = self.SAMPLE_RATE, samplerate = self.SAMPLE_RATE, callback = toneFromPoint)
        # stream.start()

        # Iteration vars
        point = self.clickedPoint # Cache the clicked point
        lastPoint = (self.clickedPoint.real, self.clickedPoint.imag)
        iter = 0
        lineIndex = 0
        z = complex(0, 0)
        inCycle = False
        cycleDrawn = False
        diverged = False
        
        # Track the visited points
        visitedPoints = []
        
        # Draw the lines and ellipses
        while not self.exiting:
            # Make sure shift is not being pressed
            if not self.isZooming:
                # Check that the clicked point hasn't changed
                if point != self.clickedPoint:
                    # Undraw all pooled lines and ellipses
                    for line in self.orbitLinePool:
                        line.setCanvas(self.mandlebrotSet)
                        line.undraw()
                    
                    for ellipse in self.orbitEllipsePool:
                        ellipse.setCanvas(self.mandlebrotSet)
                        ellipse.undraw()
                    
                # Iteration vars
                    point = self.clickedPoint # Cache the clicked point
                    lastPoint = (self.clickedPoint.real, self.clickedPoint.imag)
                    iter = 0
                    lineIndex = 0
                    z = complex(0, 0)
                    inCycle = False
                    cycleDrawn = False
                    diverged = False

                    visitedPoints = []
                
                if cycleDrawn or diverged: # Cycle has already been drawn, do nothing
                    pass
                elif inCycle:
                    # Draw only the cycle points
                    pt = visitedPoints[iter]
                    
                    if iter == len(visitedPoints) - 1:
                        cycleDrawn = True
                else: # Iterate mandlebrot fracal normally
                    z = z ** 2 + point
                    
                    pt = (round(z.real, 2), round(z.imag, 2))
                    
                    if (abs(z) >= 2):
                        # print("DIVERGED")
                        diverged = True
                                    
                    # Check if the point has been visited before
                    if pt in visitedPoints:
                        inCycle = True
                        iter = visitedPoints.index(pt) - 1
                    else:
                        visitedPoints.append(pt)
                
                if inCycle:
                    self.orbitLinePool[lineIndex].setColor("green")
                    self.orbitEllipsePool[lineIndex].setColor("green")
                else:
                    self.orbitLinePool[lineIndex].setColor("red")
                    self.orbitEllipsePool[lineIndex].setColor("red")
                    
                self.orbitLinePool[lineIndex].setPoints(*self.getMandlebrotWidgetPoint(lastPoint), *self.getMandlebrotWidgetPoint(pt))
                self.orbitLinePool[lineIndex].draw()
                
                self.orbitEllipsePool[lineIndex].setCenter(*self.getMandlebrotWidgetPoint(pt))
                self.orbitEllipsePool[lineIndex].setSize(5, 5)
                self.orbitEllipsePool[lineIndex].draw()
                
                lastPoint = pt
            
                lineIndex += 1
                
                if lineIndex >= len(self.orbitLinePool):
                    lineIndex = 0
                
                iter += 1
                
                try:
                    if not self.dragging:
                        time.sleep(0.05)
                except:
                    dummy = 0

        # threading.Thread(target = self.playOrbitSound).start()


    ##### Julia Set Functions #####
    
    # Draw the julia set (called by clicking the mandlebrot set)
    def drawJuliaSet(self):
        if self.juliaBeingDrawn:
            return
        
        # Set status text
        self.juliaStatusText.text = "Computing..."
        self.juliaProgress.setValue(0)
        
        # Disable drawing the set again set while it is being drawn
        self.drawJuliaButton.disable()
        
        if self.juliaRenderThread != None:
            self.juliaRenderThread.stop()
                
        # Create and start the thread
        self.juliaRenderThread = StoppableThread(name = "juliaRenderThread", target = self.renderJuliaSet)
        self.juliaRenderThread.start()
        
        self.juliaBeingDrawn = True
    
    # Compute the Julia set and return it's colors
    def computeJuliaSet(self, size, customCoords, maxIterations, juliaC):
        # Compute the julia set
        print("Computing the julia set")
        startTime = time.time()

        # Calculate julia set into an array using numpy, using vEcToRiZaTiOn
        rMin = customCoords[0]
        rMax = customCoords[2]
        iMin = customCoords[1]
        iMax = customCoords[3]

        # Create ALL the x and y values
        x,y = np.ogrid[rMin:rMax:size[0] * 1j, iMin:iMax:size[1] * 1j]

        # Create ALL the complex numbers
        z = x + (y * 1j)

        # Initialize z to ALL be zero
        c = np.full(z.shape, juliaC)

        # Keep track of which points did not converge so far
        m = np.full(c.shape, True, dtype = bool)

        # Keep track in which iteration the points diverged
        divergenceTimes = maxIterations + np.zeros(z.shape, dtype = int)

        for i in range(maxIterations):
            # Iterate
            z[m] = z[m] ** 2 + c[m]
            
            # Find diverging
            diverging = np.greater(np.abs(z), 2, out = np.full(c.shape, False), where = m)

            # Find which diverged in this iteration
            diverged = np.logical_and(diverging, m)
            
            # Remember which have diverged
            m[np.abs(z) > 2] = False
            
            # Remember when they diverged
            divergenceTimes[diverged] = i
            
            self.juliaProgress.setValue(lerp((i / maxIterations), 0, 100))

        diff = time.time() - startTime
        print("Finished computing the julia set in: " + str(diff) + "sec (" + str(diff * 1000) + "ms)")

        return divergenceTimes
    
    # Done on another thread to avoid freezing. Render the julia and display that image
    def renderJuliaSet(self):
        # Compute the julia set
        computedData = self.computeJuliaSet(self.renderSize, self.juliaCustomCoords, self.juliaIterations, self.clickedPoint)
        
        startTime = time.time()
        
        print("Rendering the julia set")
        
        self.juliaStatusText.text = "Rendering..."
        self.juliaProgress.setValue(0)
        
        self.juliaSet.clear()
        
        totalPixelTime = 0
        rowLoop = 0
        
        # Sweep
        for sweep in range(self.renderSweeps):
            y = sweep
            
            # Go through every y value, with a step of sweeps
            while y < self.renderSize[1]:
                startLoop = time.time()
                
                # Track the color of every pixel on this row
                rowColors = []
                                
                # Go through every x value
                for x in range(self.renderSize[0]):
                    val = computedData[x][y]
                    
                    color = 'black'
                                    
                    pixelTime = time.time()
                    if self.juliaDrawMethod == 1:
                        if val == self.juliaIterations:
                            # Threshold coloring
                            color = 'white'
                    elif self.juliaDrawMethod == 2:
                        if val != self.juliaIterations:
                            # Gradient coloring
                            color = colorRGB(*getGradientColor(val / self.juliaIterations, self.colorMap))
                    
                    rowColors.append(color)
                    
                    totalPixelTime += time.time() - pixelTime
                
                # Append row pixel colors
                self.juliaSet.plotBulk(0, y,  ("{" + str(rowColors)[1:-1].replace('\'', '').replace(',', '') + "} "))
                
                # Step the y value
                y += self.renderSweeps
                                
                rowLoop += time.time() - startLoop
                
                # Progress using sweep and y value
                newProgress = lerp((sweep + (y / self.renderSize[1])) / self.renderSweeps, 0, 100)
                self.juliaProgress.setValue(newProgress)
        
        # Print average times
        print("Average pixel time: " + str((totalPixelTime / (self.renderSize[0] * self.renderSize[1])) * 1000) + "ms")
        print("Total pixel time: " + str(totalPixelTime * 1000) + "ms")
        print("Average row loop time: " + str((rowLoop / self.renderSize[1]) * 1000) + "ms")
        print("Total row loop time: " + str(rowLoop * 1000) + "ms")
        
        diff = time.time() - startTime
        print("Finished rendering the julia set in: " + str(diff) + "sec (" + str(diff * 1000) + "ms)")
        
        self.juliaRendered = True
        self.drawJuliaButton.enable()
        
        # Set status text
        self.juliaStatusText.text = ""
        self.juliaBeingDrawn = False
        self.juliaProgress.setValue(0)
    #endregion

    #region Sound
    # def playOrbitSound(self):
    #     if(self.clickedOrbit == None):
    #         return
        
    #     print("Playing orbit sounds")
        
    #     if nativeSound:
    #         soundFile = self.getTone(self.clickedOrbit)
            
    #         playsound(soundFile)
        
    #         time.sleep(1)
    #     else:

    #         # stream = sounddevice.OutputStream(channels = 2, blocksize = self.SAMPLE_RATE, samplerate = self.SAMPLE_RATE, callback = self.toneFromOrbit)
    #         # stream.start()

    #         # while True:
    #         time.sleep(4)
    
    # def getTone(self, orbit):
    #     # Check if the tones dir exists
    #     if (not os.path.isdir("tones")):
    #         os.mkdir("tones")
        
    #     # Remove if the sound file exists
    #     if (os.path.isfile("tones/orbitTone.wav")):
    #         os.remove("tones/orbitTone.wav")
        
    #     sampleRate = 44100
        
    #     file = wave.open("tones/orbitTone.wav", "w")
    #     file.setnchannels(1) # mono
    #     file.setsampwidth(2)
    #     file.setframerate(sampleRate)
        
    #     for i in range(len(orbit)):
    #         val = orbit[i]
            
    #         z = complex(round(val.real, 2), round(val.imag, 2))
        
    #         # Get the frequency
    #         freq = remap(z.real, self.mandlebrotCustomCoords[0], self.mandlebrotCustomCoords[2], 100, 1000)
            
    #         data = struct.pack('<h', int(freq))
    #         file.writeframesraw(data)
            
    #     file.close()
        
    #     return str("tones/orbitTone.wav")
    #endregion

    #region Interaction
    def zoom(self):
        self.isZooming = True
        self.zoomMandlebrotButton.disable()
        self.zoomJuliaButton.disable()
    
    # Dragged the mouse over the mandlebrot set
    def mandlebrotSetDragged(self, value):
        # Toggle the drag box if shift is pressed
        self.mandlebrotSet.enableSelectionBox = self.isZooming

        if not self.isZooming:
            self.mandlebrotSetClicked(value, True)
    
    # Clicked on the mandlebrot set
    def mandlebrotSetClicked(self, value, drag = False):
        if (self.mandlebrotRendered == False or self.isZooming):
            return
        
        self.dragging = drag
    
        # Get frame size
        w = self.mandlebrotSet.getWidth()
        h = self.mandlebrotSet.getHeight()
        
        # Set clicked point info
        self.updateClickedPointInfo(value.x, value.y, w, h, 0)
        
        # Draw the orbit
        if self.orbitDrawThread == None:
            self.orbitDrawThread = StoppableThread(name = "orbitDrawThread", target = self.drawOrbitPath)
            self.orbitDrawThread.start()
        
        self.drawJuliaButton.enable()
        
        self.addBookmarkButton.enable()
        
        if not drag and self.autoComputeJuliaSet and self.drawJuliaButton.isEnabled():
            self.drawJuliaSet()
    
    # Reset zoom and center the mandlebrot set
    def recenterMandlebrotSet(self):
        self.mandlebrotCustomCoords = [-2.25, -1.5, 0.75, 1.5]
        self.drawMandlebrotSet()
        
        # Refersh bookmarks
        self.refreshBookmarks()
    
    # Zoom into the mandlebrot set
    def mandlebrotSetZoomed(self, value):
        if self.isZooming:
            zoom = self.mandlebrotSet.selectionBox
            
            if zoom == None or self.mandlebrotRendered == False or self.mandlebrotBeingDrawn:
                return
            
            # Get frame size
            w = self.mandlebrotSet.getWidth()
            h = self.mandlebrotSet.getHeight()
            
            # Copy the zoom values
            zoomX1 = zoom[0]
            zoomY1 = zoom[1]
            zoomX2 = zoom[2]
            zoomY2 = zoom[3]
            
            # Correct the zoom coordinates if the user dragged the mouse from bottom right to top left
            if (zoom[0] > zoom[2]):
                zoomX1 = zoom[2]
                zoomX2 = zoom[0]
            if (zoom[1] > zoom[3]):
                zoomY1 = zoom[3]
                zoomY2 = zoom[1]
            
            print("Zoom: " + str(zoomX1) + ", " + str(zoomY1) + ", " + str(zoomX2) + ", " + str(zoomY2))
            
            # Convert the zoom coordinates to custom coords
            x1 = self.mandlebrotCustomCoords[0] + (self.mandlebrotCustomCoords[2] - self.mandlebrotCustomCoords[0]) * (zoomX1 / w)
            y1 = self.mandlebrotCustomCoords[1] + (self.mandlebrotCustomCoords[3] - self.mandlebrotCustomCoords[1]) * (zoomY1 / h)
            x2 = self.mandlebrotCustomCoords[0] + (self.mandlebrotCustomCoords[2] - self.mandlebrotCustomCoords[0]) * (zoomX2 / w)
            y2 = self.mandlebrotCustomCoords[1] + (self.mandlebrotCustomCoords[3] - self.mandlebrotCustomCoords[1]) * (zoomY2 / h)
            
            diff = [x1 - self.mandlebrotCustomCoords[0], y1 - self.mandlebrotCustomCoords[1], x2 - self.mandlebrotCustomCoords[2], y2 - self.mandlebrotCustomCoords[3]]
            # print(diff)
            
            # Set the new coordinates
            self.mandlebrotCustomCoords = [x1, y1, x2, y2]
            
            # print(self.mandlebrotCustomCoords)
            
            # Render the set
            self.drawMandlebrotSet()
            
            # Reset zoom state
            self.isZooming = False
            self.zoomMandlebrotButton.enable()
            self.zoomJuliaButton.enable()
            
            # Refersh bookmarks
            self.refreshBookmarks()
    
    #############################

    # Dragged the mouse over the julia set
    def juliaSetDragged(self, value):
        # Toggle the drag box if shift is pressed
        self.juliaSet.enableSelectionBox = self.isZooming

        if not self.isZooming:
            self.juliaSetClicked(value)
    
    # Clicked on the julia set
    def juliaSetClicked(self, value):
        if(self.juliaRendered == False and not self.isZooming):
            return
    
        w = self.juliaSet.getWidth()
        h = self.juliaSet.getHeight()
        
        # Set clicked point info
        self.updateClickedPointInfo(value.x, value.y, w, h, 1)
    
    def recenterJuliaSet(self):
        self.juliaCustomCoords = [-2.25, -1.5, 2.25, 1.5]
        self.drawJuliaSet(self.juliaC)
        
        # Refersh bookmarks
        self.refreshBookmarks()
    
    def juliaSetZoomed(self, zoom):
         if self.isZooming:
            zoom = self.juliaSet.selectionBox
            
            if zoom == None or self.juliaRendered == False or self.juliaBeingDrawn:
                return
            
            # Get frame size
            w = self.juliaSet.getWidth()
            h = self.juliaSet.getHeight()
            
            # Copy the zoom values
            zoomX1 = zoom[0]
            zoomY1 = zoom[1]
            zoomX2 = zoom[2]
            zoomY2 = zoom[3]
            
            # Correct the zoom coordinates if the user dragged the mouse from bottom right to top left
            if (zoom[0] > zoom[2]):
                zoomX1 = zoom[2]
                zoomX2 = zoom[0]
            if (zoom[1] > zoom[3]):
                zoomY1 = zoom[3]
                zoomY2 = zoom[1]
            
            print("Zoom: " + str(zoomX1) + ", " + str(zoomY1) + ", " + str(zoomX2) + ", " + str(zoomY2))
            
            # Convert the zoom coordinates to custom coords
            x1 = self.juliaCustomCoords[0] + (self.juliaCustomCoords[2] - self.juliaCustomCoords[0]) * (zoomX1 / w)
            y1 = self.juliaCustomCoords[1] + (self.juliaCustomCoords[3] - self.juliaCustomCoords[1]) * (zoomY1 / h)
            x2 = self.juliaCustomCoords[0] + (self.juliaCustomCoords[2] - self.juliaCustomCoords[0]) * (zoomX2 / w)
            y2 = self.juliaCustomCoords[1] + (self.juliaCustomCoords[3] - self.juliaCustomCoords[1]) * (zoomY2 / h)
            
            diff = [x1 - self.juliaCustomCoords[0], y1 - self.juliaCustomCoords[1], x2 - self.juliaCustomCoords[2], y2 - self.juliaCustomCoords[3]]
            # print(diff)
            
            # Set the new coordinates
            self.juliaCustomCoords = [x1, y1, x2, y2]
            
            # print(self.juliaCustomCoords)
            
            # Render the set
            self.drawJuliaSet()
            
            # Reset zoom state
            self.isZooming = False
            self.zoomMandlebrotButton.enable()
            self.zoomJuliaButton.enable()
            
            # Refersh bookmarks
            self.refreshBookmarks()
    #endregion
    
    # Update the info listed about the currently clicked point
    def updateClickedPointInfo(self, x, y, w, h, set):
        # 0 = mandlebrot, 1 = julia
        if set == 0:
            # Get the coordinates of the click in the complex plane
            xCoord = self.mandlebrotCustomCoords[0] + (self.mandlebrotCustomCoords[2] - self.mandlebrotCustomCoords[0]) * (x / w)
            yCoord = self.mandlebrotCustomCoords[1] + (self.mandlebrotCustomCoords[3] - self.mandlebrotCustomCoords[1]) * (y / h)

            iters = self.mandlebrotIterations
            
            self.selectedSet = self.mandlebrotSet
        elif set == 1:
            # Get the coordinates of the click in the complex plane
            xCoord = self.juliaCustomCoords[0] + (self.juliaCustomCoords[2] - self.juliaCustomCoords[0]) * (x / w)
            yCoord = self.juliaCustomCoords[1] + (self.juliaCustomCoords[3] - self.juliaCustomCoords[1]) * (y / h)

            iters = self.juliaIterations
            
            self.selectedSet = self.juliaSet
            
        # Set info
        self.clickedPointLabel.text = ("Clicked point: " + str(round(xCoord, 3)) + " + " + str(round(yCoord, 3)) + "i")
        info = self.computePointInfo(complex(xCoord, yCoord), iters)
        self.clickedPointPixel = (x, y)
        self.clickedPoint = complex(xCoord, yCoord)
        self.clickedPointOrbitLabel.text = ("Orbit: " + str(info[0]))
        self.orbitTooltip.text = ("Orbit: " + str(info[0]))
        self.clickedPointItersLabel.text = ("Iterations: " + str(info[1]))
        self.clickedPointDivergedLabel.text = ("Diverged: " + str(info[2]))

    #region Bookmarks
    
    def refreshBookmarks(self):
        if self.bookmarks == None:
            return
        
        for bookmark in self.bookmarks:
            pt = bookmark[0]
            pixel = bookmark[1]
            overlay = bookmark[2]
            coords = bookmark[3]
            setNum = bookmark[4]
            
            # Calculate a new pixel position for the bookmark using the current custom coordinates
            if setNum == 0:
                curCoords = self.mandlebrotCustomCoords
            elif setNum == 1:
                curCoords = self.juliaCustomCoords
            
            x1Mult = curCoords[0] / coords[0]
            y1Mult = curCoords[1] / coords[1]
            x2Mult = curCoords[2] / coords[2]
            y2Mult = curCoords[3] / coords[3]
            
            newPt = (pt[0] * x1Mult, pt[1] * y1Mult)
            newPixel = (pixel[0] * x1Mult, pixel[1] * y1Mult)
                        
            # Update the bookmark info
            bookmark[0] = newPt
            bookmark[1] = newPixel
            bookmark[3] = curCoords

            # Move the bookmark overlay to the new pixel position
            overlay.move(newPixel[0] - pixel[0], newPixel[1] - pixel[1])
    
    # Add a bookmark
    def addBookmark(self):
        pt = self.clickedPoint
        pixel = self.clickedPointPixel
        
        # Create a bookmark overlay on the mandlebrot set (random color)
        color = colorRGB(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        bookmarkOverlay = Ellipse(self.selectedSet, pixel[0], pixel[1], 10, 10, color = color)
        bookmarkOverlay.draw()
        
        # Add the new bookmark to the lis
        if self.selectedSet == self.mandlebrotSet:
            self.bookmarks.append([(pt.real, pt.imag), pixel, bookmarkOverlay, self.mandlebrotCustomCoords, 0, self.clickedPointPixel, str(pt), color])
        elif self.selectedSet == self.juliaSet:
            self.bookmarks.append([(pt.real, pt.imag), pixel, bookmarkOverlay, self.juliaCustomCoords, 1, self.clickedPointPixel, str(pt), color])
    
    def deleteBookmark(self, bookmark):
        bookmark[2].undraw()
        self.bookmarkEntries.pop(bookmark[6])
        self.bookmarks.remove(bookmark)
        self.bookmarksWin.close()
        self.showBookmarks()
    
    # Show a window with a list of bookmarks, with the option to delete them or select them as the current point
    def showBookmarks(self):
        self.bookmarksWin = Window("Bookmarks", 500, 300)
                
        self.bookmarkEntries = {}

        with self.bookmarksWin:
            with Stack():
                title = Label("Bookmarked Points", width = 500, font = "Arial 16 bold")
                
                if len(self.bookmarks) == 0:
                    notice = AutoWrappingLabel("No bookmarks... Click anywhere in the mandlebrot set to select a point, then click the '+ Bookmark' button to add it to the list!")
                else:
                    listbox = ScrollableFrame(width = 500, height = 300)
                    
                    with listbox:
                        for i in range(len(self.bookmarks)):
                            bookmark = self.bookmarks[i]
                            
                            # Add a list entry
                            entry = Flow()
                            with entry:
                                # Rounded string
                                name = str(round(bookmark[0][0], 3)) + " + " + str(round(bookmark[0][1], 3)) + "i"
                                
                                l = Label(str(i) + "; Point: " + name, color = bookmark[7])
                                v = Button("View", command = lambda: self.selectBookmark(bookmark))
                                d = Button("Delete", command = lambda: self.deleteBookmark(bookmark))
                            
                            self.bookmarkEntries.update({bookmark[6]: (entry, l, v, d)})
    
    def selectBookmark(self, bookmark):
        self.clickedPoint = bookmark[0]
        self.clickedPointPixel = bookmark[5]
        
        if bookmark[4] == 0:
            w = self.mandlebrotSet.getWidth()
            h = self.mandlebrotSet.getHeight()
        elif bookmark[4] == 1:
            w = self.juliaSet.getWidth()
            h = self.juliaSet.getHeight()
        
        self.updateClickedPointInfo(self.clickedPointPixel[0], self.clickedPointPixel[1], w, h, bookmark[4])
        
        # Center the mandlebrot set on the point
        self.mandlebrotCustomCoords = [bookmark[0][0] - 2, bookmark[0][1] - 2, bookmark[0][0] + 2, bookmark[0][1] + 2]
        self.drawMandlebrotSet()
        
        self.bookmarksWin.close()
    #endregion

    # Create the control panel elements
    def createControlPanel(self, panelWidth):
        # Controls
        Label("Controls", width = panelWidth)
        
        #region Value change functions
        def mandlebrotIterations(value):
            self.mandlebrotIterations = int(value)
        
        def mandlebrotMethod(value):
            if value == "Threshold":
                self.mandlebrotDrawMethod = 1
            elif value == "Smooth":
                self.mandlebrotDrawMethod = 2
            elif value == "Random":
                self.mandlebrotDrawMethod = 3
        
        def mandlebrotSound():
            self.mandlebrotSounds = self.mandlebrotSoundCheckBox.checked
                    
        def juliaIterations(value):
            self.juliaIterations = int(value)
        
        def juliaMethod(value):
            if value == "Threshold":
                self.juliaDrawMethod = 1
            elif value == "Smooth":
                self.juliaDrawMethod = 2
            elif value == "Random":
                self.juliaDrawMethod = 3
        
        def juliaAutoCompute():
            self.autoComputeJuliaSet = self.autoComputeJuliaCheckBox.checked
        
        def sweeps():
            self.renderSweeps = int(self.sweepsEntry.value)
        #endregion
        
        Label("Mandlebrot Set", width = panelWidth)
        with Stack(relief = 'groove', borderwidth = 2, width = panelWidth * 0.9):
            self.drawMandlebrotButton = Button(text = "Draw", color = (120, 120, 240), width = panelWidth * 0.9, height = 40, cornerRadius = 10, command = self.drawMandlebrotSet)
            Tooltip(self.drawMandlebrotButton, "Draw the Mandlebrot set using the current settings.")
            
            with Stack():
                Label("Iterations: ")
                self.mandlebrotItersEntry = TextBox(width = int(panelWidth * 0.9), height = 20, text = str(self.mandlebrotIterations), inputType = "int", command = mandlebrotIterations)
                Tooltip(self.mandlebrotItersEntry, "The number of iterations to use when computing the set. Higher values will take longer to compute, but will produce a more detailed image.")
            
            with Stack():
                Label("Draw method: ")
                self.mandlebrotMethodOptions = OptionsMenu("Threshold", "Smooth", "Weird", command = mandlebrotMethod)
                self.mandlebrotMethodOptions.option = "Smooth"
                Tooltip(self.mandlebrotMethodOptions, "Threshold: Draw the set using a threshold (two-tone). Smooth: Draw the set using a smooth coloring method. Random: Draw the set using a random coloring method (very cool looking).")

            self.mandlebrotSoundCheckBox = CheckBox(text = "Hear the Mandlebrot Set!", command = mandlebrotSound)
            self.mandlebrotSoundCheckBox.checked = False
            Tooltip(self.mandlebrotSoundCheckBox, "Hear the Mandlebrot Set! (very intersting)")
        
        Label("Julia Set", width = panelWidth)
        with Stack(relief = 'groove', borderwidth = 2, width = panelWidth * 0.9):
            self.drawJuliaButton = Button(text = "Draw", color = (120, 120, 240), width = panelWidth * 0.9, height = 40, cornerRadius = 10, command = self.drawJuliaSet)
            self.drawJuliaButton.disable()
            Tooltip(self.drawJuliaButton, "Click on the Mandlebrot set to select a point to use as the Julia set's seed.")
            
            self.autoComputeJuliaCheckBox = CheckBox(text = "Auto compute", command = juliaAutoCompute)
            self.autoComputeJuliaCheckBox.checked = False
            Tooltip(self.autoComputeJuliaCheckBox, "Automatically compute the Julia set when the mouse is clicked on the Mandlebrot set.")
            
            with Stack():
                Label("Iterations: ")
                self.juliaItersEntry = TextBox(width = int(panelWidth * 0.9), height = 20, text = str(self.juliaIterations), inputType = "int", command = juliaIterations)
                Tooltip(self.juliaItersEntry, "The number of iterations to use when computing the set. Higher values will take longer to compute, but will produce a more detailed image.")
                
            with Stack():
                Label("Draw method: ")
                self.juliaMethodOptions = OptionsMenu("Threshold", "Smooth", "Weird", command = juliaMethod)
                self.juliaMethodOptions.option = "Smooth"
                Tooltip(self.juliaMethodOptions, "Threshold: Draw the set using a threshold (two-tone). Smooth: Draw the set using a smooth coloring method. Random: Draw the set using a random coloring method (very cool looking).")
        
        Label("Render sweeps (default = 4): ")
        self.sweepsEntry = Spinner(value = self.renderSweeps, to = 64, command = sweeps, width = int(panelWidth * 0.9))
        # self.sweepsEntry.value = self.renderSweeps
        Tooltip(self.sweepsEntry, "The number of threads to use for computing the mandlebrot set and julia set. (Default: 16) Warning: Setting this too high may cause your computer to lag!")
        
        # Stats and info
        Label("Stats", width = panelWidth)
        with Stack(relief = 'groove', borderwidth = 2):
            Label("Render time: ")
            
            Label("Zoom: ")
        
        # Selected point
        Label("Selected point")
        with Stack(relief = "groove", borderwidth = 2): 
            self.clickedPointLabel = Label("Clicked point: Nothing")
            self.clickedPointOrbitLabel = Label("Orbit: Nothing")
            self.orbitTooltip = Tooltip(self.clickedPointOrbitLabel, "Orbit: Nothing")
            self.clickedPointItersLabel = Label("Iterations: Nothing")
            self.clickedPointDivergedLabel = Label("Diverged: Nothing")

    # Convert from mandlebrot custom coords to a point (complex) on the mandlebrot set frame
    def getMandlebrotWidgetPoint(self, pos):
        x = remap(pos[0], self.mandlebrotCustomCoords[0], self.mandlebrotCustomCoords[2], 0, self.mandlebrotSet.getWidth())
        y = remap(pos[1], self.mandlebrotCustomCoords[1], self.mandlebrotCustomCoords[3], 0, self.mandlebrotSet.getHeight())
        return (x, y)
    
    # Convert from mandlebrot custom coords to a point (complex) on the mandlebrot set frame
    def getJuliaWidgetPoint(self, pos):
        x = remap(pos[0], self.juliaCustomCoords[0], self.juliaCustomCoords[2], 0, self.juliaSet.getWidth())
        y = remap(pos[1], self.juliaCustomCoords[1], self.juliaCustomCoords[3], 0, self.juliaSet.getHeight())
        return (x, y)

    # Custom close behavior callback
    def close(self):
        print("Exiting")
        self.exiting = True
        
        if self.orbitDrawThread != None:
            self.orbitDrawThread.stop()
        
        if self.mandlebrotRenderThread != None:
            self.mandlebrotRenderThread.stop()
        
        if self.juliaRenderThread != None:
            self.juliaRenderThread.stop()

        self.mainWin.destroy()

        # Delete all tone files
        if os.path.exists("tones"):
            for file in os.listdir("tones"):
                if file.endswith(".wav"):
                    os.remove("tones/" + file)

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

# Get the color from a gradient using a number from 0 to 1
def getGradientColor(val, gradient):
    col = gradient[int(max(0, min(1, val)) * (len(gradient) - 1))]
    return (int(col[0] * 255), int(col[1] * 255), int(col[2] * 255))

# Get the color from a gradient using a complex number
def getGradientColorFromComplex(val, gradient):
    return getGradientColor((val.real ** 2 + val.imag ** 2) ** 0.5, gradient)

# Get a random color using the iterations of a point, its row, and its sweep number
def getRandomColor(val, row, sweep):
    return (int((val + row + sweep) * 0.1) % 255, int((val + row + sweep) * 0.2) % 255, int((val + row + sweep) * 0.3) % 255)

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

class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self, group = None, target = None, name = None, args = (), **kwargs):
        threading.Thread.__init__(self, group, target, name, args, kwargs)
        self._stop_event = threading.Event()
    
    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args,  **self._kwargs)

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

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