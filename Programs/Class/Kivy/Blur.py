from kivy.clock import Clock
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.graphics import RenderContext


fs_multitexture = '''
$HEADER$

uniform vec2 resolution;

void main(void) {
    int radius = 4;
    vec2 d = float(radius) / resolution;
    for (int dx = -radius; dx < radius; dx++)
        for (int dy = -radius; dy < radius; dy++)
            gl_FragColor += texture2D(texture0, tex_coord0 + vec2(float(dx), float(dy)) * d);

    gl_FragColor /= float( 4 * radius * radius);
}
'''


kv = """
<BackgroundBluredImage>:
    canvas:
        Color:
        Rectangle:
            # the shader will apply where the widget draws, so we need a rectangle of the appropriate size/pos
            pos: self.pos
            size: self.size
            # binding the texture to it so we can look it up in the shader and do our thing
            source: "minimapImag.png"

FloatLayout:
    BackgroundBluredImage:
"""


class BackgroundBluredImage(Widget):
    def __init__(self, **kwargs):
        self.canvas = RenderContext()
        self.canvas.shader.fs = fs_multitexture
        super().__init__(**kwargs)
        # We'll update our glsl variables in a clock to run every frame, but you could bind it to relevant events only, like size and pos
        Clock.schedule_interval(self.update_glsl, 0)

    def update_glsl(self, *largs):
        # This is needed for the default vertex shader.
        self.canvas['projection_mat'] = Window.render_context['projection_mat']
        self.canvas['modelview_mat'] = Window.render_context['modelview_mat']
        self.canvas['resolution'] = list(map(float, self.size))


class BluredBackgroundApp(App):
    def build(self):
        return Builder.load_string(kv)


if __name__ == '__main__':
    BluredBackgroundApp().run()