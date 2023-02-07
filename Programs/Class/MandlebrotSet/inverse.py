import time
from PIL import Image

maxIterations = 10
size = (100, 100)
backgroundColor = "white"
resolution = 4
color = "black"
customCoords = [-2.25, -1.5, 0.75, 1.5] # The region of the mandlebrot set to draw

image = Image.new("RGB", size, backgroundColor)

pixels = [backgroundColor for _ in range(size[0] * size[1])]

rMin = customCoords[0]
rMax = customCoords[2]
iMin = customCoords[1]
iMax = customCoords[3]

step = resolution * (rMax - rMin) / size[0]

def posToIndex(pos) -> int:
    return int(pos[0] + (pos[1] * size[0]))

# Compute the mandlebrot's set into an array
print("Computing the mandlebrot's set")
startTime = time.time() * 1000

r = rMin
while r < rMax:
    i = iMin

    while i < iMax:
        result = self.inMSet(complex(r, i), maxIterations)
        pixPos = (int(remap(r, rMin, rMax, 0, size[0])), int(remap(i, iMin, iMax, 0, size[1])))

        if method == 1:
            if result[0]:
                pixels[posToIndex(pixPos)] = color
        elif method == 2:
            if result[0] or result[1] != 1:
                pixels[posToIndex(pixPos)] = getGradientColorTuple(result[1] / maxIterations)
    
        i = i + step

#     r = r + step

print("Finished computing in: " + str((time.time() * 1000) - startTime) + "ms")

print(str(len(pixels)) + " pixels, image dimensions: " + str(image.size))
image.putdata(pixels)

return image