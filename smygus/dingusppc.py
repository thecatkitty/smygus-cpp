import os
import subprocess
import time
import win32api

from colour import Color
from pywinauto import Application
from pywinauto.findwindows import ElementNotFoundError
from pywinauto.keyboard import CODE_NAMES
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
        self._proc = subprocess.Popen([
            'dingusppc.exe',
            '-m', 'imacg3',
            '-b', 'imacboot.u3',
            '--rambank1_size=128',
            '--hdd_img=hd.img',
            '--cdr_img=' + iso_path,
        ], stdout=subprocess.PIPE)
        os.chdir(cwd)

        self.configuration = dict()
        while self._proc.poll() is None:
            line = self._proc.stdout.readline().decode().rstrip()
            if not ':' in line:
                continue

            key, value = [part.strip() for part in line.split(':', 1)]
            if key == 'Machine settings summary':
                continue

            self.configuration[key] = value
            if key == 'Execution mode':
                break

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

        for key in reversed(args):
            self.window.type_keys('{' + key + ' up}')

        return self

    def type(self, text: str) -> 'DingusPPC':
        for ch in text:
            vk = win32api.VkKeyScan(ch)
            vk_code = vk & 0xFF
            vk_name = CODE_NAMES[vk_code] if vk_code in CODE_NAMES.keys() else ch

            if vk & 0x100:
                self.window.type_keys('{VK_SHIFT down}')
            if vk & 0x200:
                self.window.type_keys('{VK_CONTROL down}')
            if vk & 0x400:
                self.window.type_keys('{VK_MENU down}')

            self.press(vk_name)

            if vk & 0x100:
                self.window.type_keys('{VK_SHIFT up}')
            if vk & 0x200:
                self.window.type_keys('{VK_CONTROL up}')
            if vk & 0x400:
                self.window.type_keys('{VK_MENU up}')

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
