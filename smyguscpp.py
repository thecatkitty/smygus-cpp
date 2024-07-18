import cmake
import os
import re
import shutil
import subprocess
import sys
import time

from pywinauto import Application, WindowSpecification
from pywinauto.findwindows import ElementNotFoundError
from pywinauto.win32structures import RECT
from PIL import ImageGrab


CMAKE_EXE = os.path.join(cmake.CMAKE_BIN_DIR, 'cmake.exe')
VCVARS32_BAT = 'C:\\MSDEV\\BIN\\VCVARS32.BAT'

DIR_SCRIPT = os.path.dirname(os.path.abspath(__file__))
DIR_SMYGUS = 'C:\\MSDEV\\PROJECTS\\SMYGUS'
DIR_SOURCE = DIR_SMYGUS + '\\SOURCE'
DIR_BUILD = DIR_SMYGUS + '\\BUILD'

PATCHED_FILES = [
    'build.make',
    'CMakeCache.txt',
    'Makefile',
    'Makefile2',
]

SCALE = 1.0


def load_vcvars() -> None:
    print('Loading Visual C++ environment variables...', end=' ')
    vcvars32 = subprocess.Popen(
        [VCVARS32_BAT, 'x86', '&&', 'set'], stdout=subprocess.PIPE, shell=True)
    output, _ = vcvars32.communicate()
    lines = output.decode().splitlines()
    assert lines[0].startswith('Setting environment')

    env = dict()
    for line in lines:
        if '=' not in line:
            continue

        key, value = line.split('=', 1)
        env[key] = value

    assert 'INCLUDE' in env.keys()
    assert 'LIB' in env.keys()
    os.environ.update(env)
    print('done')


def copy_sources(source_dir: str) -> None:
    print(f'Copying sources to {DIR_SOURCE}...', end=' ')
    if DIR_SOURCE == source_dir.upper():
        print('already there')
        return

    shutil.rmtree(DIR_SMYGUS, ignore_errors=True)
    os.mkdir(DIR_SMYGUS)
    shutil.copytree(source_dir, DIR_SOURCE)
    print('done')


def cmake_configure() -> None:
    print('Configuring the CMake project...')
    shutil.rmtree(DIR_BUILD, ignore_errors=True)
    assert 0 == subprocess.call([
        CMAKE_EXE,
        '-G', 'NMake Makefiles',
        '-S', DIR_SOURCE,
        '-B', DIR_BUILD,
        '-D', 'CMAKE_SYSTEM_NAME=Windows',
        '-D', 'CMAKE_BUILD_TYPE=Release',
    ], env=os.environ)
    print('done')


def patch_makefiles(replacements: dict[str, str]):
    print('Patching build files...')
    escaped = dict((re.escape(k), v) for k, v in replacements.items())
    pattern = re.compile("|".join(escaped.keys()))
    for path, _, files in os.walk(os.path.abspath(DIR_BUILD)):
        for filename in files:
            if filename not in PATCHED_FILES:
                continue

            full_path = os.path.join(path, filename)
            with open(full_path) as file:
                content = file.read()

            if not any(key in content for key in replacements.keys()):
                continue

            print('...', full_path)
            new_content = pattern.sub(
                lambda m: escaped[re.escape(m.group(0))], content)
            with open(full_path, 'w') as file:
                file.write(new_content)
    print('done')


def make_iso(name: str) -> None:
    print('Creating the disk image...')
    assert 0 == subprocess.call([
        'mkisofs',
        '-o', name,
        '-r',  # Rock Ridge
        '-J',  # Joliet
        DIR_SMYGUS,
    ])
    print('done')


def launch_dingusppc(iso: str) -> Application:
    print('Launching the DingusPPC emulator...')
    iso_path = os.path.abspath(iso)
    cwd = os.getcwd()
    os.chdir(os.path.join(DIR_SCRIPT, 'dingusppc'))
    subprocess.Popen([
        'dingusppc.exe',
        '-m', 'imacg3',
        '-b', 'imacboot.u3',
        '--rambank1_size=128',
        '--hdd_img=hd.img',
        '--cdr_img=' + iso_path,
    ])
    os.chdir(cwd)

    app = Application()
    last_err = None
    for _ in range(5):
        time.sleep(1)
        try:
            app.connect(title='DingusPPC Display')
            print('done')
            return app
        except ElementNotFoundError as err:
            last_err = err
            continue

    raise last_err


def wait_for_color(wnd: WindowSpecification, pos: tuple[int, int], color: tuple[int, int, int], timeout: int) -> None:
    for _ in range(timeout + 1):
        img = ImageGrab.grab(bbox=rect_to_bbox(
            wnd.client_area_rect()), all_screens=True)
        pixel = img.getpixel((pos[0] * SCALE, pos[1] * SCALE))
        if pixel == color:
            return

        time.sleep(1)

    raise TimeoutError()


def rect_to_bbox(rect: RECT) -> tuple[int, int, int, int]:
    return (rect.left * SCALE, rect.top * SCALE, rect.right * SCALE, rect.bottom * SCALE)


load_vcvars()
copy_sources(sys.argv[1])
cmake_configure()
patch_makefiles({
    CMAKE_EXE: 'echo cmake',
    ':X86': ':PPC',
})
make_iso(sys.argv[2])

app = launch_dingusppc(sys.argv[2])
wnd = app.top_window()

print('Waiting for the ARC firmware boot menu...', end=' ', flush=True)
wait_for_color(wnd, (8, 8), (0, 0, 170), 15)
print('done')

print('Booting Windows NT...', end=' ', flush=True)
wnd.type_keys('{ENTER}')
wait_for_color(wnd, (8, 100), (0, 0, 255), 15)
print('done')

print('Waiting for the desktop...', end=' ', flush=True)
wait_for_color(wnd, (1000, 8), (0, 128, 128), 20)
print('done')

print('Waiting for the task bar...', end=' ', flush=True)
wait_for_color(wnd, (500, 750), (192, 192, 192), 20)
print('done')
