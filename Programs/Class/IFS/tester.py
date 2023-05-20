import random as rnd
import traceback
from Lib.NewDEGraphics import *
from Lib.transform import *
import json
from math import *
from PIL import Image

# Load the transformations from a json file called "ifs.json"
with open("ifs.json") as f:
    ifs_transforms = json.load(f)

# Create a list of points to iterate over
points = [(0, 0)]

# Iterate over the transformations
for transform in ifs_transforms:
    new_points = []
    for point in points:
        new_point = transform.transformPoint(point[0], point[1])
        new_points.append(new_point)
    points = new_points

# Create an image to display the points
image = Image.new('RGB', (512, 512))
for point in points:
    image.putpixel(point, transform.color)

# Display the image
image.show()