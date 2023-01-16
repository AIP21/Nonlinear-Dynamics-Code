import math
from random import random
from sqlite3 import Time
from Lib.DEgraphics import *
from time import sleep


def func(n):
    if n % 2 == 0:
        return n / 2
    else:
        return 3 * n + 1


def tick(pixels, ones, orbits):
    max = ~sys.maxsize
    min = sys.maxsize

    for i in range(len(pixels)):
        val = func(pixels[i])
        pixels[i] = val

        if i not in ones:
            if val == 1:
                ones.append(i)

            if i in orbits:
                orbits.get(i).insert(0, val)

                if len(orbits.get(i)) > 5:
                    orbits.get(i).pop(5)
            else:
                orbits.setdefault(i, [val])

        if max < val:
            max = val

        if min > val:
            min = val

    return (max, min, ones, orbits)


def draw(disp, width, height, pixels, max, min):
    start = time.time()

    # Create the image to draw every pixel to
    imageObj = Image(Point(0, 0), (width, height))

    # Draw every pixel to the image
    for y in range(height):
        for x in range(width):
            val = remap(min, max, 0, 1, pixels[(y * width) + x])
            imageObj.setPixel(x, y, hsvToRgb(val, 1, 1))

    imageObj.draw(disp)

    print("pixel drawing took:", (time.time() - start), "seconds")

    disp.flush()


def init():
    pixels = []
    ones = []
    orbits = {}
    disp = DEGraphWin("test", defCoords=[10, 10, -10, -10], offsets=[
        100, 100], width=500, height=500, hasTitlebar=True, hThickness=0, autoflush=False)

    # Populate the pixels array
    width = 5 * 2
    height = 5 * 2
    for y in range(height):
        for x in range(width):
            pixels.append(x * y)

    # Iterate all the steps
    for iter in range(1000000):
        (max, min, ones_, orbits_) = tick(pixels, ones, orbits)
        ones = ones_
        orbits = orbits_

        print("Iteration:", iter, " Max:", max,
              "Min:", min, "Ones:", len(ones))
        print(orbits)

        try:
            # Do the drawing
            draw(disp, width, height, pixels, max, min)

            # Wait until we click to move on to the next iteration
            # disp.getMouse()
        except:
            disp.close()
            break

    try:
        disp.getKey()
    except:
        disp.close()

    disp.close()


init()
