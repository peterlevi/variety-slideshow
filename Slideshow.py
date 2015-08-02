from gi.repository import Clutter, GLib, GdkPixbuf, Cogl
import logging
import os
import random
import sys
import threading
import time


random.seed(time.time())
logging.basicConfig()

INTERVAL = 4000
FADE_TIME = INTERVAL / 3
ZOOM_FACTOR = 1.2
PAN_FACTOR = 60
SAFETY_ZOOM = 1.05

class Slideshow:
    def __init__(self):
        pass

    def run(self):
        self.folder = '/media/Data/Pics/Wallpapers/Favorites'
        self.files = filter(lambda f: os.path.splitext(f)[1].lower() in ('.jpg', '.png', '.bmp'), os.listdir(self.folder))

        Clutter.init(sys.argv)
        Clutter.threads_init()

        self.stage = Clutter.Stage()
        self.stage.set_fullscreen(True)
        self.stage.set_color(Clutter.Color.get_static(Clutter.StaticColor.BLACK))
        self.stage.hide_cursor()

        self.texture = Clutter.Texture.new()

        def quit(*args):
            Clutter.main_quit()

         # Connect signals
        self.stage.connect('destroy', quit)
        self.stage.connect('key-press-event', quit)
        self.stage.connect('button-press-event', quit)
        self.stage.connect('motion-event', quit)

        self.will_enlarge = random.choice((True, False))
        self.prepare_next_data()
        Clutter.threads_add_timeout(GLib.PRIORITY_HIGH_IDLE, 300, self._after_show, None)
        self.stage.show()

        Clutter.main()

    def _after_show(self, *args):
        global SAFETY_ZOOM
        SAFETY_ZOOM = 1.02 + 1.5 * PAN_FACTOR / min(self.stage.get_width(), self.stage.get_height())

        self.next()

    def next(self, *args):
        try:
            self.will_enlarge = not self.will_enlarge
            self.next_texture = self.create_texture()
            self.stage.add_actor(self.next_texture)

            self.toggle(self.texture, False)
            self.toggle(self.next_texture, True)
            self.start_pan_zoom(self.next_texture)

            if hasattr(self, 'prev_texture'):
                self.prev_texture.destroy()
            self.prev_texture = self.texture
            self.texture = self.next_texture

            Clutter.threads_add_timeout(GLib.PRIORITY_HIGH_IDLE, INTERVAL, self.next, None)
            threading.Thread(target=self.prepare_next_data).start()
        except:
            logging.exception('Oops:')
            Clutter.threads_add_timeout(GLib.PRIORITY_HIGH_IDLE, 100, self.next, None)

    def get_ratio_to_screen(self, texture):
        return max(self.stage.get_width() / texture.get_width(), self.stage.get_height() / texture.get_height())

    def prepare_next_data(self):
        filename = os.path.join(self.folder, random.choice(self.files))
        self.next_image_data = self.load_image_data(filename)

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

    def create_texture(self):
        texture = Clutter.Texture.new()
        texture.set_from_rgb_data(*self.next_image_data)
        texture.set_opacity(0)
        texture.set_keep_aspect_ratio(True)
        scale = self.get_ratio_to_screen(texture)
        zoom_factor = SAFETY_ZOOM if self.will_enlarge else ZOOM_FACTOR * (1 + 0.1 * random.random())
        texture.set_size(texture.get_width() * scale * zoom_factor,
                         texture.get_height() * scale * zoom_factor)
        texture.set_position(-(texture.get_width() - self.stage.get_width())/2,
                             -(texture.get_height() - self.stage.get_height())/2)
        return texture

    def start_pan_zoom(self, texture):
        texture.save_easing_state()
        texture.set_easing_mode(Clutter.AnimationMode.LINEAR)
        texture.set_easing_duration(INTERVAL + FADE_TIME)
        if self.will_enlarge:
            target_zoom_factor = ZOOM_FACTOR * (1 + 0.1 * random.random())
            target_width = texture.get_width() * target_zoom_factor
            target_height = texture.get_height() * target_zoom_factor
        else:
            scale = self.get_ratio_to_screen(texture)
            target_width = texture.get_width() * scale * SAFETY_ZOOM
            target_height = texture.get_height() * scale * SAFETY_ZOOM

        rand_pan = lambda: random.choice((-1, 1)) * (PAN_FACTOR + PAN_FACTOR * random.random())
        texture.set_size(target_width, target_height)
        texture.set_position(-(target_width - self.stage.get_width())/2 + rand_pan(),
                             -(target_height - self.stage.get_height())/2 + rand_pan())

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
