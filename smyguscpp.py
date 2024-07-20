import cmake
import os
import re
import shutil
import subprocess
import sys
import time

from smygus import *


CMAKE_EXE = os.path.join(cmake.CMAKE_BIN_DIR, 'cmake.exe')
VCVARS32_BAT = 'C:\\MSDEV\\BIN\\VCVARS32.BAT'

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


load_vcvars()
copy_sources(sys.argv[1])
cmake_configure()
patch_makefiles({
    CMAKE_EXE: 'echo cmake',
    ':X86': ':PPC',
})
make_iso(sys.argv[2])

dingus = DingusPPC(sys.argv[2])
dingus.connect()

print('Waiting for the ARC firmware boot menu...', end=' ', flush=True)
dingus.wait(color='#00A', position=(8, 8))
print('done')

print('Booting Windows NT...', end=' ', flush=True)
dingus.type_keys('{ENTER down}{ENTER up}')
dingus.wait(color='#00F', position=(8, 100))
print('done')

print('Waiting for the desktop...', end=' ', flush=True)
dingus.wait(color='#008080', position=(1000, 8), timeout=20)
print('done')

print('Waiting for the task bar...', end=' ', flush=True)
dingus.wait(color='#C0C0C0', position=(500, 750))
print('done')

print('Launching the Command Prompt...', end=' ', flush=True)
time.sleep(0.5)
dingus.type_keys('{TAB down}{TAB up}{ENTER down}{ENTER up}')
time.sleep(2)
dingus.type_keys('{UP down}{UP up}{UP down}{UP up}{ENTER down}{ENTER up}')
time.sleep(3)
dingus.type_keys(
    '{c down}{c up}{m down}{m up}{d down}{d up}{ENTER down}{ENTER up}')
print('done')
