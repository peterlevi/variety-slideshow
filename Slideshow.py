from gi.repository import Clutter, GLib, GdkPixbuf, Cogl
import logging
import os
import random
import sys
import time

# TODO use OptionParser to read input files and folders and interval setting

IMAGE_TYPES = ('.jpg', '.png', '.bmp')
INTERVAL = 4000
FADE_TIME = INTERVAL / 3
ZOOM_FACTOR = 1.25
PAN_FACTOR = 60
SAFETY_ZOOM = 1.01

random.seed(time.time())
logging.basicConfig()

class Slideshow:
    def __init__(self):
        pass

    def run(self):
        if len(sys.argv) > 1:
            self.folder = sys.argv[1]
        else:
            self.folder = '/usr/share/backgrounds'

        self.files = filter(lambda f: os.path.splitext(f)[1].lower() in IMAGE_TYPES, os.listdir(self.folder))

        Clutter.init(sys.argv)
        Clutter.threads_init()

        self.stage = Clutter.Stage()
        self.stage.set_fullscreen(True)
        self.stage.set_color(Clutter.Color.get_static(Clutter.StaticColor.BLACK))
        self.stage.hide_cursor()

        self.texture = Clutter.Texture.new()
        self.next_texture = None
        self.prev_texture = None
        self.next_data = None

        def quit(*args):
            Clutter.main_quit()

         # Connect signals
        self.stage.connect('destroy', quit)
        self.stage.connect('key-press-event', quit)
        self.stage.connect('button-press-event', quit)
        self.stage.connect('motion-event', quit)

        self.will_enlarge = random.choice((True, False))
        self.prepare_next_data()
        Clutter.threads_add_timeout(GLib.PRIORITY_HIGH_IDLE, 300, self.next, None)
        self.stage.show()

        Clutter.main()

    def next(self, *args):
        try:
            self.will_enlarge = not self.will_enlarge
            self.next_texture = self.create_texture()
            target_size, target_position = self.initialize_pan_and_zoom(self.next_texture)

            self.stage.add_actor(self.next_texture)
            self.toggle(self.texture, False)
            self.toggle(self.next_texture, True)

            self.start_pan_and_zoom(self.next_texture, target_size, target_position)

            if self.prev_texture:
                self.prev_texture.destroy()
            self.prev_texture = self.texture
            self.texture = self.next_texture

            Clutter.threads_add_timeout(GLib.PRIORITY_HIGH_IDLE, INTERVAL, self.next, None)
            self.prepare_next_data()
        except:
            logging.exception('Oops:')
            Clutter.threads_add_timeout(GLib.PRIORITY_HIGH_IDLE, 100, self.next, None)

    def get_ratio_to_screen(self, texture):
        return max(self.stage.get_width() / texture.get_width(), self.stage.get_height() / texture.get_height())

    def prepare_next_data(self):
        self.next_data = self.load_image_data(os.path.join(self.folder, random.choice(self.files)))

    def load_image_data(self, filename):
        pixbuf = GdkPixbuf.Pixbuf.new_from_file(filename)
        return (
            pixbuf.get_pixels(),
            pixbuf.get_has_alpha(),
            pixbuf.get_width(),
            pixbuf.get_height(),
            pixbuf.get_rowstride(),
            4 if pixbuf.get_has_alpha() else 3,
            Clutter.TextureFlags.NONE)

    def create_texture(self, filename=None):
        data = self.next_data if not filename else self.load_image_data(filename)
        texture = Clutter.Texture.new()
        texture.set_from_rgb_data(*data)
        texture.set_opacity(0)
        texture.set_keep_aspect_ratio(True)
        return texture

    def initialize_pan_and_zoom(self, texture):
        rand_pan = lambda: random.choice((-1, 1)) * (PAN_FACTOR + PAN_FACTOR * random.random())
        zoom_factor = ZOOM_FACTOR * (1 + 0.1 * random.random())

        scale = self.get_ratio_to_screen(texture)
        base_w, base_h = texture.get_width() * scale, texture.get_height() * scale

        small_size = base_w * SAFETY_ZOOM, base_h * SAFETY_ZOOM
        big_size = base_w * zoom_factor, base_h * zoom_factor
        small_position = (-(small_size[0] - self.stage.get_width())/2,
                          -(small_size[1] - self.stage.get_height())/2)
        big_position = (-(big_size[0] - self.stage.get_width())/2 + rand_pan(),
                        -(big_size[1] - self.stage.get_height())/2 + rand_pan())

        if self.will_enlarge:
            initial_size, initial_position = small_size, small_position
            target_size, target_position = big_size, big_position
        else:
            initial_size, initial_position = big_size, big_position
            target_size, target_position = small_size, small_position

        # set initial size
        texture.set_size(*initial_size)
        texture.set_position(*initial_position)

        return target_size, target_position

    def start_pan_and_zoom(self, texture, target_size, target_position):
        # start animating to target size
        texture.save_easing_state()
        texture.set_easing_mode(Clutter.AnimationMode.LINEAR)
        texture.set_easing_duration(INTERVAL + FADE_TIME)
        texture.set_size(*target_size)
        texture.set_position(*target_position)

    def toggle(self, actor, visible):
        actor.set_reactive(visible)
        actor.save_easing_state()
        actor.set_easing_mode(Clutter.AnimationMode.EASE_OUT_SINE if visible else Clutter.AnimationMode.EASE_IN_SINE)
        actor.set_easing_duration(FADE_TIME)
        actor.set_opacity(255 if visible else 0)
        if visible:
            self.stage.raise_child(actor, None)


if __name__ == '__main__':
    Slideshow().run()
