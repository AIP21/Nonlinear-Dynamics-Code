from Lib.DEgraphics import *

def main():
    xOffset = 400
    yOffset = 400
    
    width = 400
    height = 700
    splitPercent = 0.33

    barHeight = height / 5
    midHeight = height - (barHeight * 2)
    splitPosition = width * splitPercent

    winTop = DEGraphWin(defCoords = [-10,-10,10,10], offsets=[xOffset - (width / 2), yOffset - barHeight], width = width, height = barHeight, hasTitlebar = False)
    winTop.setBackground(color_rgb(0,0,125))

    winLeft = DEGraphWin(defCoords = [-10,-10,10,10], offsets=[xOffset -  (width / 2), yOffset +  barHeight + midHeight], width = splitPosition, height = midHeight, hasTitlebar = False)
    winLeft.setBackground(color_rgb(0,0,125))

    winRight = DEGraphWin(defCoords = [-10,-10,10,10], offsets=[xOffset - (width / 2) + splitPosition, yOffset + barHeight + midHeight], width = width - splitPosition, height = midHeight, hasTitlebar = False)
    winLeft.setBackground(color_rgb(0,0,125))

    btnQuit = Button(winTop, Point(0,0), width = 5, height = 2, edgeWidth = 2, label = "Quit", buttonColors = ["lightgray", "black", "black"], clickedColors = ["white", "red", "black"], font = ("courier", 18), timeDelay = 0.25)
    btnQuit.activate()

    clickPt = winTop.getMouse()
    while not btnQuit.clicked(clickPt):
        clickPt = winTop.getMouse()
        
    winTop.close()
    winLeft.close()

if __name__  == "__main__":
    main()