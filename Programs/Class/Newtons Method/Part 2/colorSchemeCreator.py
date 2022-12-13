import seaborn as sns
from PIL import Image
from matplotlib import pyplot as plt
import json

palettes = ["tab10", "hls", "husl", "Paired", "Accent", "Dark2", "bright", "dark", "Pastel1", "Pastel2", "Set1", "Set2", "Set3", "colorblind"]
paletteNames = ["Accented", "Rainbow", "Muted", "Contrasty", "Summer", "Bright", "Dark 1", "Dark 2", "Pastel 1", "Pastel 2", "Pastel 3", "Set 1", "Set 2", "Set 3", "Colorblind"]
paletteLength = 15

paletteDictionary = {}

for (ind, palette) in enumerate(palettes):
    seabornPallete = sns.color_palette(palette, paletteLength)
    rgbPalette = list(reversed(seabornPallete))
    hexPalette = list(reversed(seabornPallete.as_hex()))
    paletteDictionary.update({paletteNames[ind]: hexPalette})

    new = Image.new(mode = "RGB", size = (255, 2))

    for i in range(paletteLength):
        newt = Image.new(mode = "RGB", size = (255 // paletteLength, 2), color = hexPalette[i])
        new.paste(newt, (i * 255 // paletteLength, 0))

    new.save("Programs/Class/Newtons Method/Part 2/assets/colorPalettes/" + f"{paletteNames[ind]}.png")
 
# Serializing json
json_object = json.dumps(paletteDictionary, indent = 4)
 
# Writing to palettes.json
with open("Programs/Class/Newtons Method/Part 2/assets/colorSchemePreviews/palettes.json", "w") as outfile:
    outfile.write(json_object)