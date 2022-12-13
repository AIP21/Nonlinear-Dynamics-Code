
from Lib.DEgraphics import *


def main():
    winPlot = DEGraphWin(defCoords = [-10,-10,10,10], offsets=[500,50], title = "Graphics Intro", width = 800, height = 800, hasTitlebar = True)
    winPlot.setBackground(color_rgb(0,0,125))

    btnQuit = Button(winPlot, Point(0,0), width = 5, height = 2, edgeWidth = 2, label = "Quit", buttonColors = ["lightgray", "black", "black"], clickedColors = ["white", "red", "black"], font = ("courier", 18), timeDelay = 0.25)
    btnQuit.activate()

    clickPt = winPlot.getMouse()
    while not btnQuit.clicked(clickPt):
        clickPt = winPlot.getMouse()
        
        
    winPlot.close()


if __name__  == "__main__":
    main()