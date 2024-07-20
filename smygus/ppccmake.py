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

        with logger.step(f'Copying sources to {cmake_sources}'):
            shutil.rmtree(self.project_path, ignore_errors=True)
            os.mkdir(self.project_path)
            shutil.copytree(sources, cmake_sources)

        with logger.step('Configuring the CMake project'):
            self.cm.configure('NMake Makefiles', cmake_sources, cmake_binaries, {
                'CMAKE_SYSTEM_NAME': 'Windows',
                'CMAKE_BUILD_TYPE': 'Release',
            })

        with logger.step('Patching the build files'):
            self.cm.patch_output([
                'build.make',
                'CMakeCache.txt',
                'Makefile',
                'Makefile2',
            ], {
                self.cm.exe_path: 'echo cmake',
                ':X86': ':PPC',
            })

        with logger.step('Creating the disk image'):
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
                logger.log(mkisofs.stderr)
                exit(mkisofs.returncode)

    def boot(self) -> DingusPPC:
        with logger.step('Launching the DingusPPC'):
            dingus = DingusPPC(self.iso_path)
            dingus.connect()

        with logger.step('Waiting for the ARC firmware boot menu'):
            dingus.wait(color='#00A', position=(8, 8))

        with logger.step('Booting Windows NT'):
            dingus.press('ENTER')
            dingus.wait(color='#00F', position=(8, 100))

        with logger.step('Waiting for the desktop'):
            dingus.wait(color='#008080', position=(1000, 8), timeout=20)

        with logger.step('Waiting for the task bar'):
            dingus.wait(color='#C0C0C0', position=(500, 750))

        return dingus
