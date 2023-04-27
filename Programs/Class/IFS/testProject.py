import random
from Lib.NewDEGraphics import *

win = DEGraphWin("Test", 500, 500)

points = []

    

with win:
    canvas = Canvas()
        
    def halfway(pt1, pt2):
        return ((pt1[0] + pt2[0]) / 2, (pt1[1] + pt2[1]) / 2)
    
    def iterate():
        plot = Plot(500, 500)
        
        # Plot a square at all clicked points
        for pt in points:
            for x in range(5):
                for y in range(5):
                    plot.plot(pt[0] + x, pt[1] + y, (0, 0, 255))
        
        randPt = (random.randint(-50000, 50000), random.randint(-50000, 50000))
        
        pt = randPt
        
        plotPoints = []
        
        for i in range(1000):
            randVert = points[random.randint(0, len(points) - 1)]

            halfwayPt = halfway(pt, randVert)
            
            if (halfwayPt[0] < 500 and halfwayPt[0] > 0) and (halfwayPt[1] < 500 and halfwayPt[1] > 0):
                # print(halfwayPt)
                # plotPoints.append((int(halfwayPt[0]), int(halfwayPt[1])))
                plot.plot(int(halfwayPt[0]), int(halfwayPt[1]), (255, 0, 0))
            
            pt = halfwayPt
        
        # plot.plotBulk()
    
    with canvas:
            
        def click(pt):
            print(pt)
            points.append(pt)
            
            indicator = Ellipse(*pt, 5, 5, "red", canvas = canvas)
            indicator.draw()
            
            if len(points) >= 3:
                canvas.destroy()
                iterate()
        
            
        canvas.setOnClick(click)
    
    