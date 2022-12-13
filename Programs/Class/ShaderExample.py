class ShaderViewer(Widget):
    # OpenGL base texture to appply the shader to, can be any dummy image, it wont show if the shader is applied
    source = StringProperty('data/logo/kivy-icon-512.png')

    def __init__(self, **kwargs):
        self.canvas = RenderContext()
        self.canvas.shader.fs = """
        #version 330

        #ifdef GL_ES
            precision highp float;
        #endif

        /* Outputs from the vertex shader */
        varying vec2 tex_coord0;

        // Fetch some dynamic values from Kivy openGL
        uniform float time;
        uniform vec2 resolution;
        
        // Fetch the inputs from kivy
        uniform float input;

        // Main glsl function
        void main() {
            // Get the current pixel position, localized to the center of the screen
            vec2 pt = vec2(gl_FragCoord.x - resolution.x / 2, gl_FragCoord.y - resolution.y / 2);
            
            // Get a color from the pixel coords and a kivy input. Transform it with the time
            // a color is a vec4 with 4 values, r, g, b, a
            gl_FragColor = vec4(cos(time) * pt.x, sin(time) * input, 1, 1);
        }
        """
        self.canvas.shader.vs = """
        #version 330
        
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
        super(ShaderViewer, self).__init__(**kwargs) # Call super constructor
        
        # Redraw the widget if resized
        self.bind(pos = self.resizeMoveCallback, size = self.resizeMoveCallback)
        
        with self.canvas:
            self.drawRect = Rectangle(size = self.size, pos = self.pos, source = self.source)

        # Schedule redrawing the shader. 1 / 60.0 = 1/60 of a second or 60 FPS
        Clock.schedule_interval(self.updateShader, 1 / 60.0)
    
    # Callback for resizing or moving this widget
    def resizeMoveCallback(self, instance, value):
        self.drawRect.pos = self.pos
        self.drawRect.size = self.size

    # Update the shader's parameters by passing the current values to the shader
    def updateShader(self, *args):
        self.canvas['projection_mat'] = Window.render_context['projection_mat']
        self.canvas['time'] = Clock.get_boottime()
        self.canvas['resolution'] = list(map(float, self.size))
        
        # Pass any vaues to the shader here
        self.canvas['input'] = 2
        
        self.canvas.ask_update()
