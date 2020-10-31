import pyglet
device_list = []

def refresh():
    global device_list
    device_list.extend(pyglet.input.get_tablets())
    device_list.extend(pyglet.input.get_devices())

