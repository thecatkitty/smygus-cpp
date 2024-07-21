import os
import shutil
import subprocess
import time

from recipes import nt
from smygus import *


@logger.step_func('Configuring the project for the emulated build')
def configure(sources: str, name: str = 'SMYGUS') -> None:
    iso_path = os.path.abspath(f'{name}.iso')
    project_path = os.path.join('C:\\MSDEV\\PROJECTS', name)
    cmake_sources = os.path.join(project_path, 'SOURCE')
    cmake_binaries = os.path.join(project_path, 'BUILD')

    with logger.step(f'Copying sources to {cmake_sources}'):
        shutil.rmtree(project_path, ignore_errors=True)
        os.mkdir(project_path)
        shutil.copytree(sources, cmake_sources)

    with logger.step('Loading Visual C++ configuration'):
        VisualCPP4()

    with logger.step('Configuring the CMake project'):
        cm = CMake()
        cm.configure('NMake Makefiles', cmake_sources, cmake_binaries, {
            'CMAKE_SYSTEM_NAME': 'Windows',
            'CMAKE_BUILD_TYPE': 'Release',
        })

    with logger.step('Patching the build files'):
        cm.patch_output([
            'build.make',
            'CMakeCache.txt',
            'Makefile',
            'Makefile2',
        ], {
            cm.exe_path: 'echo cmake',
            ':X86': ':PPC',
        })

    with logger.step('Creating the disk image'):
        mkisofs = subprocess.run([
            'mkisofs',
            '-o', iso_path,
            '-r',  # Rock Ridge
            '-J',  # Joliet
            project_path,
        ],
            stderr=subprocess.PIPE,
            text=True)
        if 0 != mkisofs.returncode:
            logger.log(mkisofs.stderr)
            exit(mkisofs.returncode)


@logger.step_func('Building the project on the emulated guest')
def build(name: str = 'SMYGUS') -> None:
    iso_path = os.path.abspath(f'{name}.iso')
    if nt.machine is None:
        nt.boot(iso_path)

    with logger.step('Launching the Command Prompt'):
        time.sleep(2)
        nt.machine.press('TAB').press('ENTER')
        nt.machine.wait(color='#C0C0C0', position=(180, 720))
        nt.machine.press('UP')
        nt.machine.wait(color='#000080', position=(180, 720))
        nt.machine.press('UP')
        nt.machine.wait(color='#000080', position=(180, 680))
        nt.machine.press('ENTER')
        nt.machine.wait(color='#000080', position=(300, 570))
        nt.machine.type('cmd').press('ENTER')

    with logger.step('Preparing the working directory'):
        project_path = os.path.join('C:\\MSDEV\\PROJECTS', name)

        time.sleep(2)
        nt.machine.type('xcopy /e /i e:\\*.* "' +
                        project_path + '"').press('ENTER')
        time.sleep(10)
        nt.machine.type('c:\\msdev\\bin\\vcvars32').press('ENTER')
        time.sleep(2)
        nt.machine.type('cd "' + project_path + '\\build"').press('ENTER')

    with logger.step('Building'):
        time.sleep(2)
        nt.machine.type('nmake').press('ENTER')


@logger.step_func('Configuring and building the project on the emulated guest')
def all(sources: str, name: str = 'SMYGUS') -> None:
    configure(sources, name)
    build(name)
