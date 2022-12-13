import sys
import kivy
kivy.require('1.0.6')

from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import RenderContext
from kivy.clock import Clock
from kivy.resources import resource_find
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle
from kivy.properties import StringProperty, ObjectProperty

class Renderer(Widget):
    source = StringProperty('data/logo/kivy-icon-512.png')
    
    def __init__(self, **kwargs):
        self.canvas = RenderContext()
        # self.canvas.shader.source = resource_find('shader.glsl')
        self.canvas.shader.fs = """
        #version 330

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
        uniform float zoom;
        uniform vec2 mouse;

        // Complex Number math by julesb
        // https://github.com/julesb/glsl-util
        // Additions by Johan Karlsson (DonKarlssonSan)

        #define cx_mul(a, b) vec2(a.x*b.x-a.y*b.y, a.x*b.y+a.y*b.x)
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

        vec2 cx_tan(vec2 a) {return cx_div(cx_sin(a), cx_cos(a)); }

        vec2 cx_log(vec2 a) {
            float rpart = sqrt((a.x*a.x)+(a.y*a.y));
            float ipart = atan(a.y,a.x);
            if (ipart > PI) ipart=ipart-(2.0*PI);
            return vec2(log(rpart),ipart);
        }

        vec2 cx_mobius(vec2 a) {
            vec2 c1 = a - vec2(1.0,0.0);
            vec2 c2 = a + vec2(1.0,0.0);
            return cx_div(c1, c2);
        }

        vec2 cx_z_plus_one_over_z(vec2 a) {
            return a + cx_div(vec2(1.0,0.0), a);
        }

        vec2 cx_z_squared_plus_c(vec2 z, vec2 c) {
            return cx_mul(z, z) + c;
        }

        vec2 cx_sin_of_one_over_z(vec2 z) {
            return cx_sin(cx_div(vec2(1.0,0.0), z));
        }

        ////////////////////////////////////////////////////////////
        // end Complex Number math by julesb
        ////////////////////////////////////////////////////////////

        // DonKarlssonSan's additions to complex number math

        #define cx_sub(a, b) vec2(a.x - b.x, a.y - b.y)
        #define cx_add(a, b) vec2(a.x + b.x, a.y + b.y)
        #define cx_abs(a) length(a)
        vec2 cx_to_polar(vec2 a) {
            float phi = atan(a.y / a.x);
            float r = length(a);
            return vec2(r, phi); 
        }
            
        // Complex power
        // Let z = r(cos θ + i sin θ)
        // Then z^n = r^n (cos nθ + i sin nθ)
        vec2 cx_pow(vec2 a, float n) {
            float angle = atan(a.y, a.x);
            float r = length(a);
            float real = pow(r, n) * cos(n*angle);
            float im = pow(r, n) * sin(n*angle);
            return vec2(real, im);
        }


        //// MY CODE ////
        vec2 f(vec2 z) {
            return cx_sub(cx_pow(z, 4), vec2(1, 0));
        }

        vec2 fPrime(vec2 z) {
            return cx_mul(vec2(4, 1), cx_pow(z, 3));
        }

        vec2 newtons(vec2 z) {
            return cx_sub(z, cx_div(f(z), fPrime(z)));
        }

        vec2 iterate(vec2 z0, int n) {
            for(int i = 0; i < n; i++) {
                z0 = newtons(z0);
            }
            return z0;
        }


        // Main glsl function
        void main() {
            vec2 offset = vec2(resolution.x / 2, resolution.y / 2);
            vec2 pt = vec2((gl_FragCoord.x - offset.x) / zoom, (gl_FragCoord.y - offset.y) / zoom);
            
            vec2 iterResult = iterate(pt, 100);
            
            gl_FragColor = vec4(iterResult, 0.6, 1);
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
        super(Renderer, self).__init__(**kwargs)
        Clock.schedule_interval(self.update_shader, 1)

    def update_shader(self, *args):
        with self.canvas:
            rect = Rectangle(size = self.size, pos = self.pos, source = self.source)
            
        self.canvas['projection_mat'] = Window.render_context['projection_mat']
        self.canvas['time'] = Clock.get_boottime()
        self.canvas['resolution'] = list(map(float, self.size))
        self.canvas['zoom'] = 2.0
        self.canvas.ask_update()

class ShaderEditorApp(App):
    def build(self):
        return Renderer()


if __name__ == "__main__":
    ShaderEditorApp().run()