from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse
import logging

class MyPaintWidget(Widget):

    def on_touch_down(self, touch):
        with self.canvas:
            Color(1, 1, 0)
            d = 1
            touch.ud['dot'] = Ellipse(pos=(touch.x - d / 2, touch.y - d / 2), size=(d, d))
            touch.ud['origin'] = [touch.x, touch.y]

    def on_touch_move(self, touch):
        touch.ud['dot'].size = [touch.x - touch.ud['origin'][0], touch.y - touch.ud['origin'][1]]
        logging.info("test")


class MyPaintApp(App):

    def build(self):
        return MyPaintWidget()


if __name__ == '__main__':
    logging.basicConfig(format="%(asctime)s %(message)s", encoding="utf-8", level=logging.DEBUG)
    MyPaintApp().run()
    