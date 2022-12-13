import logging as Log
import os
import platform

needsRestart = False

# Check if kivy is installed
try:
    from kivy.clock import Clock
except:
    Log("Kivy not installed, installing...")
    os.system("python -m pip install ""kivy[base]"" kivy_examples")
    Log("Kivy installed, queuing restart...")
    needsRestart = True

# Check if kivymd is installed
try:
    from kivymd.app import MDApp
except:
    Log("Kivy not installed, installing...")
    os.system("python pip install kivymd")
    Log("Kivy installed, queuing restart...")
    needsRestart = True

# Make sure it works on MacOS
if platform.system() == "Darwin":
    # Set kivy environment variables so it works on MacOS
    # os.environ['KIVY_GL_BACKEND'] = 'gl'
    # os.environ['KIVY_WINDOW'] = 'sdl2'
    # os.environ['KIVY_AUDIO'] = 'sdl2'
    # os.environ['KIVY_VIDEO'] = 'ffpyplayer'
    # os.environ['KIVY_IMAGE'] = 'sdl2'
    # os.environ['KIVY_TEXT'] = 'sdl2'
    
    # Check if homebrew is installed
    if os.system("brew --version") != 0:
        Log("Kivy dependencies for MacOS are not installed. Homebrew is required to install them.")
        decision = input("Homebrew not installed, would you like to install it? The source for the homebrew application is at: https://github.com/Homebrew/brew (y/n)")
        if decision == "y" or decision == "yes":
            Log("Installing homebrew...")
            os.system("/bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
        else:
            Log("Homebrew not installed, exiting...")
            exit()
        
        Log("Homebrew installed, installing kivy dependencies...")
        decision = input("Would you like to install the kivy dependencies? (y/n)")
        if decision == "y" or decision == "yes":
            Log("Installing kivy dependencies...")
            os.system("brew install pkg-config sdl2 sdl2_image sdl2_ttf sdl2_mixer")
        else:
            Log("Kivy dependencies not installed, exiting...")
            exit()

        Log("Kivy dependencies installed, queuing restart...")
        needsRestart = True

# Restart if needed
if needsRestart:
    Log("Restart required, restarting...")
    os.system("python " + __file__)
    exit()

from kivymd.uix.widget import MDWidget
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.stacklayout import MDStackLayout
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDIconButton, MDRoundFlatIconButton, MDFillRoundFlatIconButton, MDRoundFlatButton, MDFloatingActionButtonSpeedDial, MDFloatingActionButton
from kivy.graphics import Color, Line, RenderContext, Rectangle, RoundedRectangle, Ellipse
from kivymd.uix.textfield import MDTextField
from kivymd.uix.slider import MDSlider
from kivymd.uix.label import MDLabel, MDIcon
from kivymd.uix.tooltip import MDTooltip
from kivymd.uix.fitimage import FitImage
from kivymd.uix.chip import MDChip
from kivymd.uix.taptargetview import MDTapTargetView
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.slider import MDSlider
from kivymd.uix.swiper import MDSwiper, MDSwiperItem
from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.behaviors import (
    CircularRippleBehavior,
    CommonElevationBehavior,
)
from kivymd.theming import ThemableBehavior
from kivy.uix.effectwidget import EffectWidget, HorizontalBlurEffect, VerticalBlurEffect, InvertEffect, ScanlinesEffect, PixelateEffect, FXAAEffect
from kivy.properties import StringProperty, ObjectProperty, ListProperty
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.config import Config
from kivy.metrics import Metrics, dp

import re
from sympy import Symbol, symbols, diff, sympify, solveset, S, srepr
from functools import partial
import pathlib
import json

#region Utils
def hex2rgb(hex: str) -> (3):
    hex = hex.lstrip('#')
    hlen = len(hex)
    return tuple(int(hex[i:i+hlen//3], 16)/255 for i in range(0, hlen, hlen//3))
    
def lerp(a: float, b: float, t: float) -> float:
    """Linearly interpolate on the scale given by a to b, using t as the point on that scale.
    Examples
    --------
        50 == lerp(0, 100, 0.5)
        4.2 == lerp(1, 5, 0.8)
    """
    return (1.0 - t) * a + t * b

def inverseLerp(a: float, b: float, f: float) -> float:
    """Inverse Linar Interpolation, get the fraction between a and b on which v resides.
    Examples
    --------
        0.5 == inv_lerp(0, 100, 50)
        0.8 == inv_lerp(1, 5, 4.2)
    """
    return (f - a) / (b - a)

def remap(min1: float, max1: float, min2: float, max2: float, f: float) -> float:
    """Remap values from one linear scale to another, a combination of lerp and inv_lerp.
    i_min and i_max are the scale on which the original value resides,
    o_min and o_max are the scale to which it should be mapped.
    Examples
    --------
        45 == remap(0, 100, 40, 50, 50)
        6.2 == remap(1, 5, 3, 7, 4.2)
    """
    return lerp(min2, max2, inverseLerp(min1, max1, f))
#endregion

#region Load Assets
# Fetch the images from a folder called "colorPalettes" in the assets folder
palettesPath = str(pathlib.Path(__file__).parent.resolve()) + "/assets/colorPalettes"

# Get the list of color palette files
colorPalettePreviews = []

for f in os.listdir(palettesPath):
    name, ext = os.path.splitext(f)
    if ext == '.png':
        colorPalettePreviews.append(f)
 
# Opening palettes JSON file
with open(palettesPath + '/palettes.json', 'r') as openfile:
    # Reading from json file
    json_object = json.load(openfile)

# Get the list of color schemes
palettes = json_object.keys()

paletteDict = {}

for(i, palette) in enumerate(palettes):
    # Get the color scheme
    paletteColors = json_object[palette]
    
    # Convert the hex colors to rgb using hex2rgb
    paletteColors = [hex2rgb(color) for color in paletteColors]
    
    
    paletteDict.update({palette: paletteColors})
#endregion

#region Sympy function conversion
# Sympy to GLSL operator lookup table
syntaxes = {
        "pow":"cx_pow",
        "mul":"cx_mul", 
        "div":"cx_div",
        "add":"cx_add",
        "sub":"cx_sub", 
        "sin":"cx_sin",
        "cos":"cx_cos",
        "tan":"cx_tan",
        "log":"cx_log"}

# Sympy symbol list
symbols = ['integer', 'symbol', 'x', 'z', 'm']

# GLSL variable list (don't treat these as numbers [dont put inside of a vec2])
variables = ['x', 'z', 'm']

# Convert a sympy function to a GLSL function
def convertSympyToGLSL(toConvert) -> str:
    try:
        
        # Convert the sympy equation to a string
        equationString = srepr(toConvert).lower()
        equationString = equationString.replace("'", "")
        
        # Replace the operators with the glsl operators
        for op in syntaxes:
            equationString = equationString.replace(op, syntaxes[op])
            
        # When converting an equation to a string, sympy converts variables to "symbol(x)" where x is the variable name
        # It also converts numbers to "integer(x)" where x is the number
        # So we need to replace those with "vec2(x, 0)" where x is the number or variable name
        for symbol in symbols:
            # Get a list of every instance in the equation string where "symbol(x)" is used
            instances = re.findall(symbol + r'\(.+?\)', equationString)
                    
            # For every instance of "symbol(x)" in the equation
            for extraX in instances:
                # Find the "(x)" in extraX and remove the parenthesis
                # extraX is in the format "symbol(x)" but we find "(x)" in extraX so the "symbol" part is discarded
                replacement = re.findall(r'\(.+?\)', extraX)[0].replace("(", "").replace(")", "")
                
                # If the x value is a number (not a variable), then convert it to vec2(x, 0) or x + 0j
                if replacement not in variables:
                    replacement = f"vec2({replacement}, 0)"
                
                # Replace that value in the equation tree with the new value
                equationString = equationString.replace(extraX, replacement)
    except:
        Log("Error converting sympy to GLSL")
        return 
    
    return equationString

# Convert a list of roots to a string of vec2
def rootsToGLSL(roots) -> str:
    rootsGLSL = ""
    
    for (i, root) in enumerate(roots):
        tempRoot = root.evalf().as_real_imag()
        
        if (i == len(roots) - 1):
            rootsGLSL += "vec2(" + str(tempRoot[0]) + ", " + str(tempRoot[1]) + ")"
        else:
            rootsGLSL += "vec2(" + str(tempRoot[0]) + ", " + str(tempRoot[1]) + "), "

    return rootsGLSL
#endregion

# Frame that gets pan and zoom inputs
class InputFrame(MDFloatLayout):
    # User input variables
    panPosition = (0, 0)
    panDiff = (0, 0)
    zoom = 1.0
    startedInside = False
    
    # A list of widgets that grab this input
    inputGrabbers = []
    
    def __init__(self, initialZoom = 1.0, initialPanPosition = (0.0, 0.0), **kwargs):
        super().__init__(**kwargs) # Call super constructor
        
        # Set variables
        self.zoom = initialZoom
        self.panPosition = initialPanPosition
    
    #region Input
    def on_touch_down(self, touch):
        # Check if the input is inside this widget
        if self.collide_point(*touch.pos):
            self.startedInside = True
            
            # Check if scrolling with scroll wheel
            if touch.is_mouse_scrolling:
                if touch.button == 'scrolldown':
                    self.zoom = self.zoom / 1.1
                    self.panPosition = (self.panPosition[0] / 1.1, self.panPosition[1] / 1.1)
                elif touch.button == 'scrollup':
                    self.zoom = self.zoom * 1.1
                    self.panPosition = (self.panPosition[0] * 1.1, self.panPosition[1] * 1.1)
            else:
                # Not scrolling, so get panning input
                self.startPos = touch.pos
            
            # Redraw the widget
            self.updateInputs()

            # Propogate the touch to child widgets
            return super().on_touch_down(touch)
        else:
            self.startedInside = False
    
    def on_touch_move(self, touch):
        if self.startedInside: # Check if the input started inside of this widget
            if not touch.is_mouse_scrolling:
                # Not scrolling, so get panning input
                self.panDiff = (touch.pos[0] - self.startPos[0], touch.pos[1] - self.startPos[1])
            
            # Redraw the widget
            self.updateInputs()
            
            # Propogate the touch to child widgets
            return super().on_touch_move(touch)
        
    def on_touch_up(self, touch):
        if self.startedInside: # Check if the input started inside of this widget
            if not touch.is_mouse_scrolling:
                # Not scrolling, so get panning input
                self.panPosition = (self.panPosition[0] + self.panDiff[0], self.panPosition[1] + self.panDiff[1])
                self.panDiff = (0, 0)
            
            # Redraw the widget
            self.updateInputs()
            
            self.startedInside = False
            
            # Propogate the touch to child widgets
            return super().on_touch_up(touch)
    #endregion
    
    # Recenter the input
    def recenter(self):
        self.panPosition = (0, 0)
        self.panDiff = (0, 0)
        self.zoom = 1.0
        self.updateInputs()
    
    # Register a widget for input updates
    def register(self, widget):
        if not widget in self.inputGrabbers:
            self.inputGrabbers.append(widget)
    
    # Update widgets with input information
    def updateInputs(self):
        for widget in self.inputGrabbers:
            widget.inputCallback((self.panPosition[0] + self.panDiff[0], self.panPosition[1] + self.panDiff[1]), self.zoom)

# A widget that displays the shader for the newton's method
class NewtonsMethodViewer(MDWidget):
    # User input variables
    mousePosition = (0, 0)
    panPosition = (0, 0)
    zoom = 1.0
    
    # Parameters for newton's method
    newtonsIterations = 50

    # OpenGL base texture to appply the shader to
    source = StringProperty('data/logo/kivy-icon-512.png')
    
    # The current data in the shader
    currentEquation = "cx_pow(z, vec2(4,0)) - vec2(1, 0)"
    currentDerivative = "cx_mul(vec2(4, 0), cx_pow(z, vec2(3,0)))"
    currentRoots = "vec2(-1, 0), vec2(1, 0), vec2(0, 1), vec2(0, -1)"
    currentColors = "vec3(0, 0, 1), vec3(0, 1, 0), vec3(1, 0, 0), vec3(1, 1, 0)"

    def __init__(self, **kwargs):
        self.canvas = RenderContext()

        # Assign shaders
        self.canvas.shader.fs = """
        #version 410

        #ifdef GL_ES
            precision highp float;
        #endif
        
        // Define PI
        #define PI 3.14

        /* Outputs from the vertex shader */
        varying vec2 tex_coord0;

        // Fetch some dynamic values from Kivy openGL
        uniform float time;
        uniform vec2 resolution;
        uniform vec2 pan;
        uniform float zoom;
        uniform int iterations;

        // Complex Number math by julesb
        // https://github.com/julesb/glsl-util
        // Additions by Johan Karlsson (DonKarlssonSan)

        #define cx_div(a, b) vec2(((a.x*b.x+a.y*b.y)/(b.x*b.x+b.y*b.y)),((a.y*b.x-a.x*b.y)/(b.x*b.x+b.y*b.y)))
        #define cx_modulus(a) length(a)
        #define cx_conj(a) vec2(a.x, -a.y)
        #define cx_arg(a) atan(a.y, a.x)
        #define cx_sin(a) vec2(sin(a.x) * cosh(a.y), cos(a.x) * sinh(a.y))
        #define cx_cos(a) vec2(cos(a.x) * cosh(a.y), -sin(a.x) * sinh(a.y))

        vec2 cx_sqrt(vec2 a) {
            float r = length(a);
            float rpart = sqrt(0.5*(r+a.x));
            float ipart = sqrt(0.5*(r-a.x));
            if (a.y < 0.0) ipart = -ipart;
            return vec2(rpart,ipart);
        }
        
        vec2 cx_mul(vec2 a, vec2 b) {
            return vec2(a.x*b.x-a.y*b.y, a.x*b.y+a.y*b.x);
        }
        
        vec2 cx_mul(vec2 a, vec2 b, vec2 c) {
            return vec2(cx_mul(cx_mul(a,b), c));
        }

        vec2 cx_mul(vec2 a, vec2 b, vec2 c, vec2 d) {
            return vec2(cx_mul(cx_mul(cx_mul(a,b), c), d));
        }

        vec2 cx_mul(vec2 a, vec2 b, vec2 c, vec2 d, vec2 e) {
            return vec2(cx_mul(cx_mul(cx_mul(cx_mul(a,b), c), d), e));
        }

        ////////////////////////////////////////////////////////////
        // end Complex Number math by julesb
        ////////////////////////////////////////////////////////////

        // DonKarlssonSan's additions to complex number math

        #define cx_abs(a) length(a)
        
        vec2 cx_sub(vec2 a, vec2 b){
            return vec2(a.x - b.x, a.y - b.y);
        }
        
        vec2 cx_sub(vec2 a, vec2 b, vec2 c){
            return cx_sub(vec2(a.x - b.x, a.y - b.y), c);
        }
        
        vec2 cx_sub(vec2 a, vec2 b, vec2 c, vec2 d){
            return cx_sub(vec2(a.x - b.x, a.y - b.y), c, d);
        }
        
        vec2 cx_sub(vec2 a, vec2 b, vec2 c, vec2 d, vec2 e){
            return cx_sub(vec2(a.x - b.x, a.y - b.y), c, d, e);
        }
        
        vec2 cx_add(vec2 a, vec2 b){
            return vec2(a.x + b.x, a.y + b.y);
        }
        
        vec2 cx_add(vec2 a, vec2 b, vec2 c){
            return cx_sub(vec2(a.x + b.x, a.y + b.y), c);
        }
        
        vec2 cx_add(vec2 a, vec2 b, vec2 c, vec2 d){
            return cx_sub(vec2(a.x + b.x, a.y + b.y), c, d);
        }
        
        vec2 cx_add(vec2 a, vec2 b, vec2 c, vec2 d, vec2 e){
            return cx_sub(vec2(a.x + b.x, a.y + b.y), c, d, e);
        }
            
        // Complex power
        // Let z = r(cos θ + i sin θ)
        // Then z^n = r^n (cos nθ + i sin nθ)
        vec2 cx_pow(vec2 a, vec2 n) {
            float angle = atan(a.y, a.x);
            float r = length(a);
            float real = pow(r, n.x) * cos(n.x * angle);
            float im = pow(r, n.x) * sin(n.x * angle);
            return vec2(real, im);
        }


        //// MY CODE ////
        // The function to visualize
        vec2 f(vec2 z) {
            return cx_pow(z, vec2(4,0)) - vec2(1, 0); // z^4 - 1
        }

        // The derivative of the function to visualize
        vec2 fPrime(vec2 z) {
            return cx_mul(vec2(4, 0), cx_pow(z, vec2(3,0))); // 4z^3
        }

        vec2 newtons(vec2 z) {
            return cx_sub(z, cx_div(f(z), fPrime(z))); // z - f(z)/f'(z)
        }
        
        vec2 iterate(vec2 z0, int n) {
            for(int i = 0; i < n; i++) {
                z0 = newtons(z0);
            }
            return z0;
        }

        vec2[] roots = vec2[](vec2(-1, 0), vec2(1, 0), vec2(0, 1), vec2(0, -1)); // The roots of the function

        vec3[] colors = vec3[](vec3(0, 0, 1), vec3(0, 1, 0), vec3(1, 0, 0), vec3(1, 1, 0)); // The colors of the roots

        // Get the color of a given number using the roots of the equation
        vec3 getRootColor(vec2 z) {
            float shortestDistance = -1;
            int shortestIndex = 0;
            
            // Find which root z is closest to
            for(int i = 0; i < roots.length(); i++) {
                float distance = cx_abs(cx_sub(z, roots[i]));
                if(shortestDistance == -1 || distance < shortestDistance) {
                    shortestDistance = distance;
                    shortestIndex = i;
                }
            }
            
            return colors[shortestIndex];
        }

        // Main glsl function
        void main() {
            vec2 pt = vec2(((gl_FragCoord.x - resolution.x / 2) - pan.x) / zoom, ((gl_FragCoord.y - resolution.y / 2) - pan.y) / zoom);
            
            // TODO: Optimize by checking if it equals a root while iterating to reduce iteration count
            vec2 iterResult = iterate(pt, iterations);
            
            gl_FragColor = vec4(getRootColor(iterResult), 1);
        }
        """
        self.canvas.shader.vs = """
        #version 410
        
        #ifdef GL_ES
            precision highp float;
        #endif
          
        /* Outputs to the fragment shader */
        varying vec4 frag_color;
        varying vec2 tex_coord0;

        /* vertex attributes */
        attribute vec2     vPosition;
        attribute vec2     vTexCoords0;

        /* uniform variables */
        uniform mat4       modelview_mat;
        uniform mat4       projection_mat;
        uniform vec4       color;

        void main (void) {
            frag_color = color;
            tex_coord0 = vTexCoords0;
            gl_Position = projection_mat * modelview_mat * vec4(vPosition.xy, 0.0, 1.0);
        }
        """
                
        super(NewtonsMethodViewer, self).__init__(**kwargs) # Call super constructor
        
        # Create the draw rect, the shader will draw to this
        with self.canvas:
            self.drawRect = Rectangle(size = self.size, pos = self.pos, source = self.source)
        
        # Redraw the widget if resized
        self.bind(pos = self.resizeMoveCallback, size = self.resizeMoveCallback)
        
        # Do the initial shader update
        self.updateShader()
        
        # Set the default color palette
        self.updateColorPalette("Pastel 3")

    # Callback for resizing or moving this widget
    def resizeMoveCallback(self, instance, value):
        self.drawRect.pos = self.pos
        self.drawRect.size = self.size
        
        self.updateShader()
    
    # Callback to grab inputs from the input frame
    def inputCallback(self, panPosition, zoom):
        self.panPosition = panPosition
        self.zoom = zoom
        
        self.updateShader()
        self.updateGLSL()
    
    # Callback for updating the iterations of newton's method from the slider
    def updateIterations(self, instance, value):
        self.newtonsIterations = int(value)
        
        self.updateShader()

    # Modify the shader's function
    def updateFunction(self, newFunctionString):
        try:
            # Use sympy to parse the function, then get that function's derivative, then evaluate the roots of that function
            z = Symbol('z')
            equation = sympify(newFunctionString)
            derivative = diff(equation, z)
            roots = solveset(equation, z, domain = S.Complexes)
            
            # Convert the sympy funtions and roots to GLSL code as strings
            equationGLSL = convertSympyToGLSL(equation)
            derivativeGLSL = convertSympyToGLSL(derivative)
            rootsGLSL = rootsToGLSL(roots)

            print(equationGLSL)
            print(derivativeGLSL)
            print(rootsGLSL)
            
            # Get the current canvas shader
            fs = self.canvas.shader.fs
            
            # Replace the shader's current equation, derivatives, and roots with the new ones
            fs = fs.replace(self.currentEquation, equationGLSL)
            fs = fs.replace(self.currentDerivative, derivativeGLSL)
            fs = fs.replace(self.currentRoots, rootsGLSL)
                    
            # Set the current equation, derivative, and roots to the new ones
            self.currentEquation = equationGLSL
            self.currentDerivative = derivativeGLSL
            self.currentRoots = rootsGLSL
            
            # Save the fs to a file with utf 8
            with open("shaderDebug.fs", "w", encoding = "utf-8") as file:
                file.write(fs)
            
            file.close()
            
            # Update the shader and the canvas
            self.canvas.shader.fs = fs
            self.updateShader()
            
            return 1
        except:
            print("Error: Invalid function entered")
            return 0
    
    # Update the shader's color palette
    def updateColorPalette(self, name):
        # Get a palette from the global paletteDict using the selected palette name
        self.palette = paletteDict[name]
        self.paletteName = name
        
        # print("Selected new palette: ", self.palette)
        
        # Convert the list of colors to a string of GLSL code
        newColors = ""
        index = 0
        for (r, g, b) in self.palette:
            if(index == len(self.palette) - 1):
                newColors += "vec3(" + str(r) + ", " + str(g) + ", " + str(b) + ")"
            else:
                newColors += "vec3(" + str(r) + ", " + str(g) + ", " + str(b) + "), "
            
            index += 1
                
        # Get the current canvas shader
        fs = self.canvas.shader.fs
        
        # Replace the shader's current colors with the new ones
        fs = fs.replace(self.currentColors, newColors)
        
        # Update the currentColors
        self.currentColors = newColors
        
        # Save the fs to a file with utf 8
        with open("shaderDebug.fs", "w", encoding = "utf-8") as file:
            file.write(fs)
        
        file.close()
        
        # Update the shader and the canvas
        self.canvas.shader.fs = fs
        self.updateShader()

    # Update the shader's parameters by passing the current values to the shader
    def updateShader(self, *args):
        Clock.schedule_once(partial(self.updateGLSL, type), 0)

    # Update the glsl shader
    def updateGLSL(self, *args):
        self.canvas['projection_mat'] = Window.render_context['projection_mat']
        self.canvas['time'] = Clock.get_boottime()
        self.canvas['resolution'] = list(map(float, self.size))
        self.canvas['pan'] = self.panPosition
        self.canvas['zoom'] = self.zoom
        self.canvas['iterations'] = self.newtonsIterations
        self.canvas['mouse'] = self.mousePosition
        self.canvas.ask_update()

    # Save the widget to an image. Ask for a directoryand save it to the images folder.
    def saveImage(self, instance):
        # Ask for a directory to save the image to
        from pathlib import Path
        path = str(Path.cwd()) + '/'  # path to the directory that will be opened in the file manager
        
        self.file_manager = MDFileManager(exit_manager = self.exit_manager, select_path = self.saveImageCallback, selector = 'folder')
        
        self.file_manager.show(path)
    
    # Exit the file manager
    def exit_manager(self):
        self.file_manager.close()
        
    # Callback for when the user enters an image name
    def saveImageCallback(self, instance):
        # The screenshot filename
        filename = instance + "/NewtonsMethodVisualizerScreenshot.png"
        
        # Save the image
        self.export_to_png(filename, 1)
        
        self.exit_manager()

# A widget that displays a minimap of the whole fractal, showing your current view and allowing you to click to move
class Minimap(MDWidget, CommonElevationBehavior):
    # Padding around the minimap [vertical, horizontal]
    padding = [10, 10]
    
    def __init__(self, viewer, **kwargs):
        super(Minimap, self).__init__(**kwargs) # Call super constructor
        
        # Assign variables
        self.viewer = viewer
        
        # Shader stuff
        self.canvas = RenderContext()
        
        with self.canvas:
            # Clear the canvas
            self.canvas.clear()
            
            # Draw the draw rect
            Color(0.3, 0.3, 0.3, 1)
            self.drawRect = RoundedRectangle(size = self.size, pos = self.pos, radius = [15, 15, 15, 15])
        
        # Get the viewer's shader
        self.canvas.shader.fs = self.viewer.canvas.shader.fs
        self.canvas.shader.vs = self.viewer.canvas.shader.vs
        
        # Set shadow properties
        self.elevation = 15
        self.shadow_radius = 20
        self.shadow_softness = 20
        self.shadow_softness_size = 8
        
        # Update minimap data
        self.updateMinimap()
        
        # Redraw the widget if resized
        self.bind(pos = self.resizeMoveCallback, size = self.resizeMoveCallback)
    
    # Callback for resizing or moving this widget
    def resizeMoveCallback(self, instance, value):
        # self.updateMinimap()
        self.drawRect.pos = self.pos
        self.drawRect.size = self.size
    
    # Update the minimap
    def updateMinimap(self):
        # Update the shader
        self.canvas['projection_mat'] = Window.render_context['projection_mat']
        self.canvas['time'] = Clock.get_boottime()
        self.canvas['resolution'] = list(map(float, self.size))
        self.canvas['pan'] = (0, 0)
        self.canvas['zoom'] = 1
        self.canvas['iterations'] = 50
        self.canvas['mouse'] = self.viewer.mousePosition
        self.canvas.ask_update()

# A floating action button with a tooltip
class TooltipMDFloatingActionButton(MDFloatingActionButton, MDTooltip):
    pass

# A chip with an image
class ImageChip(MDRaisedButton):
    # Whether or not this is currently selected
    active = False
    
    def __init__(self, source, **kwargs):
        super(ImageChip, self).__init__(**kwargs) # Call super constructor
        
        # Assign variables
        self.source = source
        self.md_bg_color = (0, 0, 0, 0)
        self.md_bg_color_disabled = (0, 0, 0, 0)
        self.set_radius([20, 20, 20, 20])
        
        # Draw the image to the button's backgound
        self.draw()
        
        # Resize and move callback
        self.bind(pos = self.resizeMoveCallback, size = self.resizeMoveCallback)
    
    # Callback for resizing or moving this widget
    def resizeMoveCallback(self, instance, value):
        self.draw()
    
    # Draw the widget
    def draw(self):
        with self.canvas.before:
            # Clear the canvas
            self.canvas.before.clear()
            
            # Color based on if it's active
            if(self.active):
                Color(0.5, 0.5, 0.5, 1)
            else:
                Color(1, 1, 1, 1)
            
            # Draw the palette preview image
            RoundedRectangle(size = self.size, pos = self.pos, radius = [20, 20, 20, 20], source = self.source)
            
            # Draw the background for the label
            Color(0.5, 0.5, 0.5, 0.85)
            RoundedRectangle(size = (self.width * 0.16, self.height), pos = (self.x + (self.width / 2) - (self.width * 0.08), self.y), radius = [20, 20, 20, 20])

#region Popups
# A widget that slides in and out from the bottom of the screen
class PopupPage(MDWidget, CommonElevationBehavior, ThemableBehavior):
    def __init__(self, title, temporary = False, **kwargs):
        super().__init__(**kwargs) # Call super constructor
        
        self.temp = temporary
        
        # Set shadow properties
        self.elevation = 150
        self.shadow_radius = 40
        self.shadow_softness = 20
        self.shadow_softness_size = 8
        
        # Create the popup's base content
        self.createBaseContent(title)
        
        # Draw the background
        with self.canvas.before:
            # Clear canvas
            self.canvas.before.clear()
            
            # Draw background rectangle
            Color(self.theme_cls.bg_dark)
            self.backgroundRect = RoundedRectangle(size = self.size, pos = self.pos, radius = [40, 40, 40, 40])
        
        # Callback for resizing or moving this widget
        self.bind(pos = self.resizeMoveCallback, size = self.resizeMoveCallback)

    # Redraw the widget if resized or moved
    def resizeMoveCallback(self, instance, value):
        self.area.pos = self.pos
        self.area.size = self.size
        self.backgroundRect.pos = self.pos
        self.backgroundRect.size = self.size
    
    # Create the popup's content
    def createBaseContent(self, title):
        # Create the main area layout
        self.area = MDBoxLayout(orientation = 'vertical', padding = [25, 20, 25, 10], spacing = 10)
        self.add_widget(self.area)
        
        #region Create the header layout that contains the title and the close button
        self.header = MDBoxLayout(orientation = 'horizontal', size_hint = (1, 0.1), spacing = 0)
        self.area.add_widget(self.header)
        
        # Create the title
        self.titleLabel = MDLabel(text = title, theme_text_color = "Primary", size_hint = (0.9, 1), halign = 'center')
        self.header.add_widget(self.titleLabel)
        
        # Create a small close button on the right side of the header
        self.closeButton = MDIconButton(icon = "close", theme_text_color = "Primary", size_hint = (0.1, 1), pos_hint = {'center_y': 0, 'right': 1})
        self.closeButton.bind(on_release = self.close)
        self.header.add_widget(self.closeButton)
        #endregion
        
        # Create the content layout
        self.content = MDStackLayout(orientation = 'lr-tb', padding = [25, 20, 25, 10], spacing = 25)
        self.area.add_widget(self.content)       
    
    # Block touch events over this widget from propagating to the viewer
    def on_touch_down(self, touch):
        # Check if touch point is over the control panel
        if self.collide_point(*touch.pos):            
            # Call super touch event
            super().on_touch_down(touch)
            return True
    
    # Close the popup
    def close(self, instance):
        self.animateOut()

    # Animate the widget into view by sliding it up from the bottom of the screen
    def animateIn(self):
        # Create the animation
        self.animation = Animation(y = 20, duration = 0.5, t = 'out_quad')
        
        # Start the animation
        self.animation.start(self)
    
    # Animate the widget out of view by sliding it down to the bottom of the screen
    def animateOut(self):
        # Create the animation
        self.animation = Animation(y = -600, duration = 0.5, t = 'out_quad')
        
        # Start the animation
        self.animation.start(self)
        
        # When the animation finishes, call destroyThis
        if (self.temp):
            self.animation.bind(on_complete = self.destroyThis)
        
    # Destroy this widget and remove it from parent widget after the animation is complete
    def destroyThis(self, instance, value):
        # Remove the widget from its parent
        self.parent.remove_widget(self)

# A popup that contains the options for the viewer
class OptionsPopup(PopupPage):
    # The newton's method viewer
    viewer = None
    
    def __init__(self, viewer, **kwargs):
        super(OptionsPopup, self).__init__(**kwargs) # Call super constructor
        
        # Assign variables
        self.viewer = viewer
        
        # Create the popup's content
        self.createContent()
    
    # Create the popup's content
    def createContent(self):
        # Create the options box
        self.optionsBox = MDStackLayout(orientation = 'lr-tb', padding = [10, 10, 10, 10], spacing = [25, 10])
        self.content.add_widget(self.optionsBox)
        
        # Create the iterations slider and it's labels
        self.createIterationsSlider()
        
        # Create the function input
        self.createFunctionInput()
        
        # Create the save button
        self.saveButton = TooltipMDFloatingActionButton(icon = "fit-to-screen-outline", tooltip_text = "Screenshot", size_hint = (None, None), size = [dp(10), dp(10)])
        self.saveButton.bind(on_release = self.viewer.saveImage)
        self.optionsBox.add_widget(self.saveButton)
    
    # Create the iterations slider with a title label and min and max labels
    def createIterationsSlider(self):
        # Create the title label
        self.sliderLabel = MDLabel(text = "Iterations", theme_text_color = "Secondary", size_hint = (1, 0.1), halign = 'center')
        self.optionsBox.add_widget(self.sliderLabel)
        
        # Create the min slider label
        self.minLabel = MDLabel(text = "0", theme_text_color = "Hint", size_hint = (0.015, 0.1))
        self.optionsBox.add_widget(self.minLabel)
        
        # Create the slider widget
        self.slider = MDSlider(min = 0, max = 100, value = 50, step = 1, size_hint = (0.935, 0.1))
        self.slider.bind(value = self.viewer.updateIterations)
        self.optionsBox.add_widget(self.slider)
        
        # Create the max slider label
        self.maxLabel = MDLabel(text = str(int(self.slider.max)), theme_text_color = "Hint", size_hint = (0.05, 0.1))
        self.optionsBox.add_widget(self.maxLabel)

    # Create the function input
    # The user inputs their desired function here and sympy automatically converts it to a glsl shader.
    def createFunctionInput(self):
        # Create the title label
        self.functionLabel = MDLabel(text = "Function", theme_text_color = "Secondary", size_hint = (1, 0.1), halign = 'center')
        self.optionsBox.add_widget(self.functionLabel)
        
        # Create the function input
        self.functionInput = MDTextField(text = "z^4 - 1", cursor_blink = True, mode = "fill", helper_text = "Power using ^ and multiply using * (can't do 6z, instead do 6*z)", hint_text = "Enter a function", multiline = False, size_hint = (0.6, 0.1))
        self.functionInput.bind(on_text_validate = self.updateFunction)
        self.optionsBox.add_widget(self.functionInput)
        
        # Create the function submit button
        self.presetsButton = MDRaisedButton(text = "Presets", size_hint = (None, None))
        self.optionsBox.add_widget(self.presetsButton)
        
        # Create a dropdown with a few preset functions
        self.functionDropdown = MDDropdownMenu(caller = self.presetsButton, radius = [20, 20, 20, 20], ver_growth = 'up', position = 'center', width_mult = 6, items = [
            {
                "viewclass": "OneLineListItem",
                "text": "z^4 - 1",
                "on_release": lambda x = "z^4 - 1": self.setPreset(x)
            },
            {
                "viewclass": "OneLineListItem",
                "text": "z^3 - 1",
                "on_release": lambda x = "z^3 - 1": self.setPreset(x)
            },
            {
                "viewclass": "OneLineListItem",
                "text": "z^8 + 15 * z^4 - 16",
                "on_release": lambda x = "z^8 + 15 * z^4 - 16": self.setPreset(x)
            },
            {
                "viewclass": "OneLineListItem",
                "text": "z^6 - z^3 - 5",
                "on_release": lambda x = "z^6 - z^3 - 5": self.setPreset(x)
            }])
        self.functionDropdown.bind()
        self.presetsButton.bind(on_release = self.openDropdown)
    
    # Open the dropdown menu on button click
    def openDropdown(self, instance):
        self.functionDropdown.open()
    
    # Set a preset function
    def setPreset(self, preset):
        self.functionInput.text = preset
        self.functionDropdown.dismiss()
        
        self.viewer.updateFunction(preset)
    
    # Update the viewer's function to the new function
    def updateFunction(self, instance):
        result = self.viewer.updateFunction(self.functionInput.text)
        
        if result == 0:
            self.functionInput.error = True
            self.functionInput.helper_text = "Invalid function. Power using ^ and multiply using * (can't do 6z, instead do 6*z)"
        else:
            self.functionInput.error = False
            self.functionInput.helper_text = "Power using ^ and multiply using * (can't do 6z, instead do 6*z)"

# A popup that contains the color options for the viewer
# The user can choose between a few preset color schemes for the viewer's root colors or create their own
class ColorsPopup(PopupPage, ThemableBehavior):
    # The newton's method viewer
    viewer = None
    
    def __init__(self, viewer, **kwargs):
        super().__init__(**kwargs) # Call super constructor
        
        # Assign variables
        self.viewer = viewer
        
        # Create the popup's content
        self.createContent()
    
    # Create the popup's content
    def createContent(self):
        # Create the options box
        self.optionsBox = MDBoxLayout(orientation = 'vertical', padding = [10, 10, 10, 10], spacing = 20)
        self.content.add_widget(self.optionsBox)
        
        # Create the title label
        self.colorPaletteLabel = MDLabel(text = "Color Palette (swipe to select)", theme_text_color = "Secondary", size_hint = (1, 0.1), halign = 'center')
        self.optionsBox.add_widget(self.colorPaletteLabel)
        
        # Create a swiper for the different color schemes
        self.colorPaletteSwiper = MDSwiper() # width_mult = 3, items_spacing = dp(50)
        self.optionsBox.add_widget(self.colorPaletteSwiper)
        
        self.paletteChips = []
        selectedPaletteIndex = 0
        
        # Each swiper item has a label with the name of the color scheme's file name
        index = 0
        for palettePreview in colorPalettePreviews:            
            # Create the swiper tile
            swiperItem = MDSwiperItem(md_bg_color = self.theme_cls.bg_normal, radius = [20])
            self.colorPaletteSwiper.add_widget(swiperItem)
                        
            # Create the rounded image
            chip = ImageChip(text = palettePreview.split(".")[0], size_hint = (1, 1), source = palettesPath + "/" + palettePreview)
            chip.bind(on_release = self.palleteChipBehavior)
            swiperItem.add_widget(chip)
            self.paletteChips.append(chip)
                        
            if palettePreview.split(".")[0] == self.viewer.paletteName:
                chip.active = True
                chip.draw()
                selectedPaletteIndex = index
            
            index = index + 1
        
        self.colorPaletteSwiper.set_current(selectedPaletteIndex)
    
    # The behavior of the palette chip
    def palleteChipBehavior(self, instance):
        instance.active = True
        instance.draw()
        
        self.viewer.updateColorPalette(instance.text)
        
        # deactive all other chips
        for chip in self.paletteChips:
            if chip != instance:
                chip.active = False
                
                # Redraw the chip
                chip.draw()

# A popup that shows the user controls for the viewer and information about the program
class AboutPopup(PopupPage):
    # Initialize the popup
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Create the popup's content
        self.createContent()
    
    def createContent(self):
        # Create the page box
        self.pageBox = MDBoxLayout(orientation = 'horizontal', padding = [10, 10, 10, 10], spacing = 10)
        self.content.add_widget(self.pageBox)
        
        # Create the controls
        self.createControls()
        
        # Create the about text
        self.createAboutText()
    
    # Create the about text
    def createAboutText(self):
        # Create the about text
        self.aboutText = MDLabel(text = "This project was created by Alexander Irausquin-Petit for his AT Nonlinear Dynamics class. It was created using Python and Kivy. It uses the complex plane to visualuze the application of Newton's Method on any valid function.", theme_text_color = "Secondary", halign = 'center')
        self.pageBox.add_widget(self.aboutText)
    
    # Create the controls
    def createControls(self):
        # Create the controls layout
        self.controlsLayout = MDBoxLayout(orientation = 'vertical', padding = [10, 10, 10, 10], size_hint = (0.5, 1), spacing = 10)
        self.pageBox.add_widget(self.controlsLayout)
        
        # Create the controls
        self.controls = []
        self.controls.append(MDLabel(text = "Left Click + Drag: Pan", theme_text_color = "Secondary", size_hint = (1, 0.1), halign = 'center'))
        self.controls.append(MDLabel(text = "Scroll: Zoom", theme_text_color = "Secondary", size_hint = (1, 0.1), halign = 'center'))

        # Add the controls to the controls box
        for control in self.controls:
            self.controlsLayout.add_widget(control)      
#endregion

# The root widget
class Root(MDFloatLayout, ThemableBehavior):
    def __init__(self, **kwargs):
        super().__init__(**kwargs) # Call super constructor
        
        # Create input frame widget
        self.inputFrame = InputFrame()
        self.add_widget(self.inputFrame)
        
        # Create the newton's method viewer widget
        self.viewerContainer = EffectWidget()
        self.viewer = NewtonsMethodViewer()
        self.inputFrame.register(self.viewer)
        self.viewerContainer.add_widget(self.viewer)
        self.viewerContainer.effects = [HorizontalBlurEffect(size = 25.0), VerticalBlurEffect(size = 25.0)]
        self.add_widget(self.viewerContainer)
        
        # Tell the viewer what the mouse position is
        Window.bind(mouse_pos = lambda w, p: setattr(self.viewer, 'mousePosition', p))
                
        #region Create the speed dial menu
        # Create a floating action speed dial on the bottom right of the screen
        self.speedDial = MDFloatingActionButtonSpeedDial(size_hint = (None, None), hint_animation = True, right_pad = True, root_button_anim = True, size = [dp(56), dp(56)])
        self.speedDial.data = {'Options': ['cog', 'on_release', self.speedDialCallback], 'Colors': ['palette', 'on_release', self.speedDialCallback], 'About': ['information', 'on_release', self.speedDialCallback]}
        self.speedDial.bg_hint_color = self.theme_cls.primary_light
        self.speedDial.y = dp(20)
        self.speedDial.x = Window.width - (dp(56) + dp(20))
        self.speedDial.bind(on_release_stack_button = self.speedDialCallback)
        self.add_widget(self.speedDial)
        
        # Create a tap target view to tell the user what the speed dial button does
        self.tapTargetView = MDTapTargetView(widget = self.speedDial, title_position = 'left', outer_radius = dp(200), draw_shadow = True, stop_on_outer_touch = False, title_text = "Page list", description_text = "Click here to select a page", widget_position = "right_bottom")
        Clock.schedule_once(partial(self.tapTargetView.start, type), 6)
        self.tapTargetView.bind(on_close = self.tapTargetHide)
        
        # Create the popups
        # Create the options popup
        self.optionsPopup = OptionsPopup(viewer = self.viewer, title = "Options", size_hint = (None, None), pos = (20, -600))
        self.add_widget(self.optionsPopup)
        
        # None bc it's temporarily loaded (bc it's a SUPER complex widget that slows things down if it's always loaded)
        self.colorsPopup = None
        
        # Create the about popup
        self.aboutPopup = AboutPopup(title = "About", size_hint = (None, None), pos = (20, -600))
        self.add_widget(self.aboutPopup)
        
        # Create the minimap widget on the top right of the screen
        # self.minimap = Minimap(viewer = self.viewer, size_hint = (None, None))
        # self.add_widget(self.minimap)
        
        # Create a button to recenter the viewer, at the top left of the screen
        self.recenterButton = TooltipMDFloatingActionButton(icon = 'home', tooltip_text = "Recenter view", type = "small", theme_icon_color = "Primary", size_hint = (None, None), size = [dp(56), dp(56)])
        self.add_widget(self.recenterButton)
        self.recenterButton.bind(on_release = self.recenter)
        
        # Redraw the widget if resized
        self.bind(pos = self.resizeMoveCallback, size = self.resizeMoveCallback)
    
    # Tap target hide callback
    def tapTargetHide(self, instance):
        self.viewerContainer.effects = [FXAAEffect()]
    
    # Set the callbakcks for the speed dial
    def speedDialCallback(self, instance):
        if (instance.icon == 'cog'):
            self.optionsPopup.animateIn()
            self.speedDial.close_stack()
            self.resizeMoveCallback(None, None)
        elif (instance.icon == 'palette'):
            # Create the colors popup
            self.colorsPopup = ColorsPopup(self.viewer, title = "Colors", size_hint = (None, None), temporary = True, pos = (20, -600))
            self.add_widget(self.colorsPopup)
            self.colorsPopup.animateIn()
            self.speedDial.close_stack()
            self.resizeMoveCallback(None, None)
        elif (instance.icon == 'information'):
            self.aboutPopup.animateIn()
            self.speedDial.close_stack()
            self.resizeMoveCallback(None, None)
       
    # Callback for resizing or moving this widget
    def resizeMoveCallback(self, instance, value):
        if self.optionsPopup != None:
            self.optionsPopup.size = (self.width - 40, self.height * 0.3)
        if self.colorsPopup != None:
            self.colorsPopup.size = (self.width - 40, self.height * 0.3)
        if self.aboutPopup != None:
            self.aboutPopup.size = (self.width - 40, self.height * 0.3)
        
        # self.minimap.size = (self.width * 0.1, self.width * 0.1)
        # self.minimap.pos = (self.width - (self.minimap.width + 10), self.height - (self.minimap.width + 10))
        self.recenterButton.pos = (30, self.height - 137)
        self.speedDial.y = dp(20)
        self.speedDial.x = Window.width - (dp(56) + dp(20))
        
        # self.controlPanel.size = (self.width - 40, self.height * 0.3)
        # self.controlPanelShadow.size = (self.width - 40, self.height * 0.3)
        pass
    
    # Callback for recentering the view
    def recenter(self, instance):
        self.inputFrame.recenter()
        
        # Redraw the viewer
        self.viewer.updateShader()

class NewtonsMethodExplorer(MDApp):
    def build(self):
        # self.fps_monitor_start()
        
        Window.size = (1600, 1200)
        Window.resizable = 1
        Window.minimum_width = 800
        Window.minimum_height = 600
        Window.clear_color = (0.1, 0.1, 0.1, 1)
        Window.position = 'custom'
        Window.top = 300
        Window.left = 500
                
        self.title = "Newton's Method Explorer"
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Purple"  # "Purple", "Red"
        self.theme_cls.primary_hue = "200"
        
        return Root()

# Main function
if __name__ == '__main__':
    Log.basicConfig(format = "%(asctime)s %(message)s", encoding = "utf-8", level = Log.DEBUG)

    # Fix dpi on windows
    if os.name == "nt":
        from ctypes import windll, c_int64
        windll.user32.SetProcessDpiAwarenessContext(c_int64(-2))
        
    # Set kivy config
    Config.write()
    Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
    Config.set('kivy', 'window_icon', 'appIcon.png')
    Config.set('graphics', 'maxfps', '60')
    Config.set('graphics', 'minimum_width', '150')
    Config.set('graphics', 'minimum_height', '100')
    Config.write()

    Metrics.density = 2

    NewtonsMethodExplorer().run()