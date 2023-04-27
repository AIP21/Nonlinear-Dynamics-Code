import pyglet


window = pyglet.window.Window()
devices = pyglet.input.get_devices()

for d in devices:
    print(d)



@window.event
def on_mouse_press(x, y, button, modifiers):
    print('on_mouse_press(%r, %r, %r, %r' % (x, y, button, modifiers))

@window.event
def on_mouse_release(x, y, button, modifiers):
    print('on_mouse_release(%r, %r, %r, %r' % (x, y, button, modifiers))

pyglet.app.run()