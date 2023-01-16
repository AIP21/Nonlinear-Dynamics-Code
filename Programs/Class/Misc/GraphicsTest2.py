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


def tripLength(n):
    
    return steps


def compute(pixels, lengths):
    start = time.time()

    min1 = sys.maxsize
    max1 = ~sys.maxsize
    min2 = sys.maxsize
    max2 = ~sys.maxsize

    pixLen = len(pixels)

    print("s")
    
    steps = 0
    n = pixels[0]
    while n != 1:
        steps += 1
        n = func(n)

    print(steps, n)

    for i in range(pixLen):
        steps = 0
        n = pixels[i]
        while n != 1:
            steps += 1
            n = func(n)

        pixels[i] = n
        lengths[i] = steps

        if min1 > steps:
            min1 = steps

        if max1 < steps:
            max1 = steps

        if min2 > n:
            min2 = n

        if max2 < n:
            max2 = n

        print("iter", i)

    print("pixel computing took:", (time.time() - start), "seconds")

    print("min1", min1, "max1", max1)
    print("min2", min2, "max2", max2)

    return (min1, max1, min2, max2)


def draw(disp, width, height, p, pixels, min, max):
    start = time.time()

    # Create the image to draw every pixel to
    imageObj = Image(p, (width, height))

    # Draw every pixel to the image
    for y in range(height):
        for x in range(width):
            # val = remap(min, max, 0, 1, pixels[(y * width) + x])
            # imageObj.setPixel(x, y, hsvToRgb(val, 1, 1))
            val = int(remap(min, max, 0, 255, pixels[(y * width) + x]))
            imageObj.setPixel(x, y, color_rgb(val, val, val))

    imageObj.draw(disp)

    print("pixel drawing took:", (time.time() - start), "seconds")

    disp.flush()


def init():
    pixels = []
    lengths = []
    disp = DEGraphWin("test", defCoords=[100, 100, -100, -100], offsets=[
        100, 100], width=500, height=500, hasTitlebar=True, hThickness=0, autoflush=False)

    # Populate the pixels array
    width = 50 * 2
    height = 50 * 2
    for y in range(1,height):
        for x in range(1,width):
            pixels.append(x * y)
            lengths.append(0)

    # Compute the final values for all the pixels
    (min1, max1, min2, max2) = compute(pixels, lengths)

    # print(lengths)

    # Do the drawing
    draw(disp, width, height, Point(0, 0), lengths, min1, max1)

    draw(disp, width, height, Point(55, 0), pixels, min2, max2)

    try:
        disp.getKey()
    except:
        disp.close()

    disp.close()


init()
