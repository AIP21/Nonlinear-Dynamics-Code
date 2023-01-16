from math import sin
from re import L
from Lib.DEgraphics import *
import customtkinter as tk


class NewGraphicsTest():
    def __init__(self):
        WIDTH = 720
        HEIGHT = 480

        halfWidth = WIDTH / 2
        halfHeight = HEIGHT / 2

        drawWindow = DEGraphWin(defCoords=[-10, -10, 10, 10],
                                offsets=[100, 100],
                                width=WIDTH,
                                height=HEIGHT,
                                hasTitlebar=True,
                                title="New Graphics Test")

        rectangle1 = Rectangle(Point(0, 0), Point(10, 10))
        rectangle1.setFill(None)
        rectangle1.setOutline("white")
        rectangle1.draw(drawWindow)
        rectangle2 = Rectangle(Point(0, 0), Point(-10, -10))
        rectangle2.setFill(None)
        rectangle2.setOutline("white")
        rectangle2.draw(drawWindow)
        rectangle3 = Rectangle(Point(0, 0), Point(-10, 10))
        rectangle3.setFill(None)
        rectangle3.setOutline("white")
        rectangle3.draw(drawWindow)
        rectangle4 = Rectangle(Point(0, 0), Point(10, -10))
        rectangle4.setFill(None)
        rectangle4.setOutline("white")
        rectangle4.draw(drawWindow)


        # dropDown = DropDown(Point(-10, -10), ["A", "B", "C"])
        # dropDown.draw(drawWindow)

        # slider = Slider(Point(0, 0), 50, 10, 0, 10)
        # slider.draw(drawWindow)

        # entry = Entry(Point(-1, 5), 20)
        # entry.draw(drawWindow)

        # intEntry = IntEntry(Point(-3, 5), 20)
        # intEntry.draw(drawWindow)

        # dblEntry = DblEntry(Point(-5, 5), 20)
        # dblEntry.draw(drawWindow)

        # # Image

        # text = Text(Point(-5, -2), "test")
        # text.draw(drawWindow)

        # polygon = Polygon(Point(1, 1), Point(2, 2), Point(3, 3), Point(5, -6))
        # polygon.draw(drawWindow)

        # line = Line(Point(0, 0), Point(10, 10), style='solid')
        # line.draw(drawWindow)

        # circle = Circle(Point(0, 0), 10)
        # circle.draw(drawWindow)

        # testQuitBtn = ModernButton(Point (0, 0), 10, 10, "Quit", drawWindow.close)
        # testQuitBtn.draw(drawWindow)

        drawWindow.mainloop()


def btnAction():
    print("button clicked")


if __name__ == "__main__":
    graphTest = NewGraphicsTest()
