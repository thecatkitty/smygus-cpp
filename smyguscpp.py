import cmake
import os
import re
import shutil
import subprocess
import sys
import time

from pywinauto import Application
from pywinauto.findwindows import ElementNotFoundError


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


def make_iso(name: str) -> None:
    print('Creating the disk image...')
    assert 0 == subprocess.call([
        'mkisofs',
        '-o', name,
        '-r',  # Rock Ridge
        '-J',  # Joliet
        DIR_SMYGUS,
    ])


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
            return app
        except ElementNotFoundError as err:
            last_err = err
            continue

    raise last_err


load_vcvars()
copy_sources(sys.argv[1])
cmake_configure()
patch_makefiles({
    CMAKE_EXE: 'echo cmake',
    ':X86': ':PPC',
})
make_iso(sys.argv[2])
launch_dingusppc(sys.argv[2])
