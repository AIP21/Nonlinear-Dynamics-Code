import random
from Lib.NewDEGraphics import *
from Lib.transform import *

SIZE = 250

win = DEGraphWin("Test", SIZE, SIZE)

pixels = []

point = (random.random() * 10000000.0, random.random() * 10000000.0)

transforms = []
transforms.append(IFS_Transform(xScale = 0.5, yScale = 0.5, theta = 0.0, phi = 0.0, h = 0.0, k = 0.0, p = 1, c = 'red'))
transforms.append(IFS_Transform(xScale = 0.5, yScale = 0.5, theta = 0.0, phi = 0.0, h = 0.5, k = 0.0, p = 1, c = 'blue'))
transforms.append(IFS_Transform(xScale = 0.5, yScale = 0.5, theta = 0.0, phi = 0.0, h = 0.0, k = 0.5, p = 1, c = 'green'))

minX = 10000000
maxX = -10000000
minY = 10000000
maxY = -10000000

for x in range(SIZE):
    col = []
    
    for y in range(SIZE):
        col.append('white')
    
    pixels.append(col)

def remap(value, low1, high1, low2, high2):
    return low2 + (value - low1) * (high2 - low2) / (high1 - low1)

def lerp(a, b, t):
    return a + (b - a) * t

def iterate(plot):
    global transforms, point, pixels, minX, maxX, minY, maxY
    randTransform = transforms[random.randint(0, len(transforms) - 1)]
    
    newPt = randTransform.transformPoint(point[0], point[1])
    
    if plot:
        ptRemap = (lerp(0, SIZE, newPt[0]), lerp(0, SIZE, newPt[1]))
                
        pt = (int(ptRemap[0]), int(ptRemap[1]))
        
        pixels[pt[0]][pt[1]] = 'red'
    else:
        if newPt[0] < minX:
            minX = newPt[0]
        if newPt[0] > maxX:
            maxX = newPt[0]
        if newPt[1] < minY:
            minY = newPt[1]
        if newPt[1] > maxY:
            maxY = newPt[1]
    
    point = newPt
    
with win:
    canvas = Canvas()
    
    with canvas:
        plot = Plot(SIZE, SIZE)
        
        for i in range(100000):
            iterate(False)
        
        print("MinX: " + str(minX))
        print("MaxX: " + str(maxX))
        print("MinY: " + str(minY))
        print("MaxY: " + str(maxY))
        
        for i in range(10000):
            iterate(True)
        
        print("Done iterating")
        
        plot.plotBulk(0, 0, pixels)        
        