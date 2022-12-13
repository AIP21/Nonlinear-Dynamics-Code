from kivy.app import App
from kivy.uix.image import AsyncImage
from kivy.uix.scatter import Scatter


class ZoomApp(App):
    def build(self):
        scatter = Scatter(do_translation=True,do_rotation=True)
        image = AsyncImage(source='https://images.unsplash.com/photo-1630629701731-56481a2dd34a?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1502&q=80')
        scatter.add_widget(image)
        return scatter

ZoomApp().run()
