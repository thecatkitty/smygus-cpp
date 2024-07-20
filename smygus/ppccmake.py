import os
import shutil
import subprocess
import sys

from . import *


class PowerPCCMake(object):
    def __init__(self, name: str = 'SMYGUS') -> None:
        self.cm = CMake()
        self.vc = VisualCPP4()
        self.iso_path = os.path.abspath(f'{name}.iso')
        self.project_path = os.path.join(self.vc.projects_path, name)

    def configure(self, sources: str) -> None:
        cmake_sources = os.path.join(self.project_path, 'SOURCE')
        cmake_binaries = os.path.join(self.project_path, 'BUILD')

        print(f'Copying sources to {cmake_sources}...', end=' ')
        shutil.rmtree(self.project_path, ignore_errors=True)
        os.mkdir(self.project_path)
        shutil.copytree(sources, cmake_sources)
        print('done')

        print('Configuring the CMake project...')
        self.cm.configure('NMake Makefiles', cmake_sources, cmake_binaries, {
            'CMAKE_SYSTEM_NAME': 'Windows',
            'CMAKE_BUILD_TYPE': 'Release',
        })
        print('done')

        print('Patching the build files...')
        self.cm.patch_output([
            'build.make',
            'CMakeCache.txt',
            'Makefile',
            'Makefile2',
        ], {
            self.cm.exe_path: 'echo cmake',
            ':X86': ':PPC',
        })
        print('done')

        print('Creating the disk image...', end=' ', flush=True)
        mkisofs = subprocess.run([
            'mkisofs',
            '-o', self.iso_path,
            '-r',  # Rock Ridge
            '-J',  # Joliet
            self.project_path,
        ],
            stderr=subprocess.PIPE,
            text=True)
        if 0 != mkisofs.returncode:
            print(mkisofs.stderr, file=sys.stderr)
            exit(mkisofs.returncode)
        print('done')

    def boot(self) -> DingusPPC:
        print('Launching the DingusPPC...', end=' ', flush=True)
        dingus = DingusPPC(self.iso_path)
        dingus.connect()
        print('done')

        print('Waiting for the ARC firmware boot menu...', end=' ', flush=True)
        dingus.wait(color='#00A', position=(8, 8))
        print('done')

        print('Booting Windows NT...', end=' ', flush=True)
        dingus.press('ENTER')
        dingus.wait(color='#00F', position=(8, 100))
        print('done')

        print('Waiting for the desktop...', end=' ', flush=True)
        dingus.wait(color='#008080', position=(1000, 8), timeout=20)
        print('done')

        print('Waiting for the task bar...', end=' ', flush=True)
        dingus.wait(color='#C0C0C0', position=(500, 750))
        print('done')

        return dingus
