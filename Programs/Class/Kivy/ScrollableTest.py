from calendar import formatstring
from kivy.base import runTouchApp
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.properties import ListProperty
from kivy.core.window import Window
from random import random
import logging

Builder.load_string('''
<PhysSim>:
    BouncyBall:
        pos: 300, 300
<BouncyBall>:
    canvas:
        Color:
            rgba: 1, 0, 0, 1
        Rectangle:
            pos: self.pos
            size: self.size
''')

class PhysSim(Widget):
    pass

class BouncyBall(Widget):
    velocity = ListProperty([0, 0])
    grounded = False

    def __init__(self, **kwargs):
        super(BouncyBall, self).__init__(**kwargs)
        Clock.schedule_interval(self.update, 1.0 / 60.0)

    def update(self, *args):
        self.x = min(Window.size[0], max(0, self.x + self.velocity[0]))
        self.y = min(Window.size[1], max(0, self.y + self.velocity[1]))
        
        grounded = (Window.size[1] - self.y) == Window.size[1]

        if not grounded:
            self.velocity[1] = max(-9.8, self.velocity[1] - 1)
        else:
            self.velocity[0] /= 1.1
            
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.draggingOnCube = True
            touch.ud['origin'] = [touch.x, touch.y]
        else:
            self.draggingOnCube = False
    
    def on_touch_move(self, touch):
        if self.draggingOnCube:
            dragVec = [(touch.x - self.x), (touch.y - self.y)]
            self.velocity = dragVec
            logging.info([touch.x, self.x, touch.y, self.y])
           

logging.basicConfig(format="%(asctime)s %(message)s", encoding="utf-8", level=logging.DEBUG)
runTouchApp(PhysSim())