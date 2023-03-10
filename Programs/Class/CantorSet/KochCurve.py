from math import *
from Lib.NewDEGraphics import *

win = DEGraphWin("Koch Curve", 600, 600, showScrollbar = False)

def length(lvl):
    return (1/3) ** lvl

# Draw the Koch Curve recursively
def drawKochCurve(origin, angle, length, angleChange, direction, maxDepth, depth, i):
    if depth == maxDepth:
        return
    else:
        # Draw the line
        line = Line(origin[0], origin[1], origin[0] + length * cos(radians(angle)), origin[1] + length * sin(radians(angle))))
        line.draw()
        
        # Draw the next line
        drawKochCurve((origin[0] + length * cos(radians(angle)), origin[1] + length * sin(radians(angle))), angle + angleChange * direction, length, angleChange, direction, maxDepth, depth + 1, i)
        # Draw the next line
        drawKochCurve((origin[0] + length * cos(radians(angle)), origin[1] + length * sin(radians(angle))), angle - angleChange * direction, length, angleChange, direction, maxDepth, depth + 1, i)

with win:
    canvas = Canvas()
    with canvas:
        # Draw Koch Curve
        drawKochCurve((300, 300), 0, 300, 60, 1, 5, 0, 0)

win.update()
win.mainloop()