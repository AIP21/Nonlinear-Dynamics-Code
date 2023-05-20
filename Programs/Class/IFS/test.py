import json
import math
import os
import random
import numpy as np

# Remove everything in the Systems folder
for file in os.listdir(os.path.dirname(os.path.realpath(__file__)) + "\\Systems"):
    os.remove(os.path.dirname(os.path.realpath(__file__)) + "\\Systems\\" + file)

    
runDir = os.path.dirname(os.path.realpath(__file__))

with open(runDir + "/INPUT.txt", "r") as f:
    lines = f.readlines()
    
colors = [
    [255, 0, 0],
    [0, 255, 0],
    [0, 0, 255],
    [255, 255, 0],
    [255, 0, 255],
    [0, 255, 255],
    [128, 0, 0],
    [0, 128, 0],
    [0, 0, 128],
    [128, 128, 0],
    [128, 0, 128],
    [0, 128, 128],
    [255, 128, 0],
    [255, 0, 128],
    [0, 255, 128],
    [128, 255, 0],
    [128, 0, 255],
    [0, 128, 255],
    [192, 192, 192],
]

alreadyColors = []

def getRandomColor(index):
  """Returns a random unique color in the format `[r, g, b]`.

  Args:
    index: The index of the color to return.

  Returns:
    A random unique color in the format `[r, g, b]`.
  """

  # Generate a random color.
  r = random.randint(0, 255)
  g = random.randint(0, 255)
  b = random.randint(0, 255)

  # Check if the color is already in use.
  while (r, g, b) in alreadyColors:
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)

  # Add the color to the list of used colors.
  alreadyColors.append((r, g, b))

  # Return the color.
  return [r, g, b]

import numpy as np

def matrixToSR(a, b, c, d):
    """
    Takes in a tuple of four values (they represent a 2x2 matrix) and returns the scale x, scale y, theta, and phi.

    Args:
    matrix: A tuple of four values (they represent a 2x2 matrix).

    Returns:
    A tuple of four values (scale x, scale y, theta, phi).
    """

    # Calculate the scale factors.
    scale_x = math.sqrt(a * a + b * b)
    scale_y = math.sqrt(c * c + d * d)

    # Calculate the rotation angles.
    theta = math.degrees(math.atan2(c, a))
    phi = math.degrees(math.atan2(d, b))
    
    # Rigid rotation so phi = theta
    phi = theta

    # Return the results.
    return a, d, theta, phi

transforms = {}

inTransform = False
curName = ""
curIndex = 0

for line in lines:
    if "{" in line:
        curName = line[0 : line.index("{")].strip()
        transforms = {}
        inTransform = True
        curIndex =  0
        print("NEW: " + curName)
        continue
    
    if line.startswith(";"):
        continue
    
    if line.startswith("}"):
        inTransform = False
        
        # Check if already exists, if so, add a number to the end
        if os.path.exists(runDir + "\\Systems\\" + curName + ".json"):
            i = 1
            
            while os.path.exists(runDir + "\\Systems\\" + curName + str(i) + ".json"):
                i += 1
                
            curName += " " + str(i)
        
        # Remove characters that cannot be in a file name
        curName = curName.replace("\\", "")
        curName = curName.replace("/", "")
        curName = curName.replace(":", "")
        curName = curName.replace("*", "")
        curName = curName.replace("?", "")
        curName = curName.replace("\"", "")
        curName = curName.replace("<", "")
        curName = curName.replace(">", "")
        curName = curName.replace("|", "")
        
        with open(runDir + "/Systems/" + curName + ".json", "w") as f:
            json.dump(transforms, f, indent = 4)
        
        continue
    
    if not inTransform:
        continue

    transform = line.split()
    
    if len(transform) != 7:
        transform.append(1)
    
    print(line + " -> " + str(transform))

    xScale, yScale, theta, phi = matrixToSR(float(transform[0]), float(transform[1]), float(transform[2]), float(transform[3]))
    
    h = float(transform[4])
    k = float(transform[5])
    probability = float(transform[6])
    color = colors[curIndex] if curIndex < len(colors) else getRandomColor(curIndex)

    transform_dict = {
        "r": xScale,
        "s": yScale,
        "theta": theta,
        "phi": phi,
        "e": h,
        "f": k,
        "prob": probability,
        "color": color
    }

    transforms.update({curIndex: transform_dict})
    
    curIndex += 1

# import random
# import matplotlib.pyplot as plt

# from Lib.transform import *

# PI = 3.141592653589793238462643383279502884197169399375105820974944592307816406286

# transforms = [
#     IFS_Transform(xScale=0.85, yScale=0.04, theta=-15, phi=0, h=0, k=0, p=0.85),
#     IFS_Transform(xScale=0.2, yScale=0.26, theta=-67, phi=0, h=0, k=0, p=0.07),
#     IFS_Transform(xScale=0.2, yScale=0.23, theta=120, phi=0, h=0, k=0, p=0.07),
#     IFS_Transform(xScale=1, yScale=1, theta=0, phi=0, h=0, k=0, p=0.01),
# ]

# # Create a random point
# point = (random.random(), random.random())

# # Iterate over the transforms
# for i in range(1000):
#     # Choose a random transform
#     transform = random.choices(transforms, weights=[t.prob for t in transforms])[0]

#     # Apply the transform to the point
#     point = transform.transformPoint(point[0], point[1])

#     # Plot the point
#     plt.plot(point[0], point[1], 'bo')

# # Show the plot
# plt.show()


# import random

# elements = ["a", "b", "c", "d"]
# probabilities = [10, 1, 10, 10]

# aCt = 0
# bCt = 0
# cCt = 0
# dCt = 0

# for i in range(1000):
#     random_element = random.choices(elements, weights = probabilities)[0]
#     if random_element == "a":
#         aCt += 1
#     elif random_element == "b":
#         bCt += 1
#     elif random_element == "c":
#         cCt += 1
#     elif random_element == "d":
#         dCt += 1

# print("a: ", aCt)
# print("b: ", bCt)
# print("c: ", cCt)
# print("d: ", dCt)

# aPercent = aCt / 1000
# bPercent = bCt / 1000
# cPercent = cCt / 1000
# dPercent = dCt / 1000

# print("a%: ", aPercent)
# print("b%: ", bPercent)
# print("c%: ", cPercent)
# print("d%: ", dPercent)

# import turtle
# import random

# pen = turtle.Turtle()
# pen.speed(0)
# pen.color("green")
# pen.penup()

# x = 0
# y = 0
# for n in range(11000):
#     pen.goto(65 * x, 37 * y - 252)  # scale the fern to fit nicely inside the window
#     pen.pendown()
#     pen.dot(3)
#     pen.penup()
#     r = random.random()
#     if r < 0.01:
#         x, y =  0.00 * x + 0.00 * y,  0.00 * x + 0.16 * y + 0.00
#     elif r < 0.86:
#         x, y =  0.85 * x + 0.04 * y, -0.04 * x + 0.85 * y + 1.60
#     elif r < 0.93:
#         x, y =  0.20 * x - 0.26 * y,  0.23 * x + 0.22 * y + 1.60
#     else:
#         x, y = -0.15 * x + 0.28 * y,  0.26 * x + 0.24 * y + 0.44