import os
import subprocess
import time

from colour import Color
from pywinauto import Application
from pywinauto.findwindows import ElementNotFoundError
from pywinauto.win32structures import RECT
from PIL import ImageGrab


def _rect_to_bbox(rect: RECT) -> tuple[int, int, int, int]:
    return (rect.left, rect.top, rect.right, rect.bottom)


def _compare_pixel(pixel: tuple[int, int, int], color: Color) -> bool:
    pixel_r, pixel_g, pixel_b = (
        pixel[0] / 255.0, pixel[1] / 255.0, pixel[2] / 255.0)
    color_r, color_g, color_b = color.get_rgb()
    return (abs(pixel_r - color_r) < 0.01) and (abs(pixel_g - color_g) < 0.01) and (abs(pixel_b - color_b) < 0.01)


class DingusPPC(object):
    def __init__(self, iso: str):
        iso_path = os.path.abspath(iso)
        cwd = os.getcwd()
        os.chdir(os.path.join(os.path.dirname(
            os.path.abspath(__file__)), '../dingusppc'))
        subprocess.Popen([
            'dingusppc.exe',
            '-m', 'imacg3',
            '-b', 'imacboot.u3',
            '--rambank1_size=128',
            '--hdd_img=hd.img',
            '--cdr_img=' + iso_path,
        ])
        os.chdir(cwd)

        self.app = Application()
        self.window = None

    def connect(self) -> None:
        last_err = None
        for _ in range(5):
            time.sleep(1)
            try:
                self.app.connect(title='DingusPPC Display')
                self.window = self.app.top_window()
                return
            except ElementNotFoundError as err:
                last_err = err
                continue

        raise last_err

    def press(self, *args) -> 'DingusPPC':
        for key in args:
            self.window.type_keys('{' + key + ' down}')
            time.sleep(0.1)

        for key in reversed(args):
            self.window.type_keys('{' + key + ' up}')
            time.sleep(0.1)

        return self

    def _wait_color(self, position: tuple[int, int], color: Color, timeout: int) -> None:
        for _ in range(timeout + 1):
            img = ImageGrab.grab(bbox=_rect_to_bbox(
                self.window.client_area_rect()), all_screens=True)
            pixel = img.getpixel((position[0], position[1]))
            if _compare_pixel(pixel, color):
                return

            time.sleep(1)

        raise TimeoutError()

    def wait(self, timeout: int = 15, **kwargs) -> None:
        if 'color' in kwargs.keys():
            return self._wait_color(kwargs['position'], Color(kwargs['color']), timeout)

        raise ValueError('Nobody said what we are waiting for')
