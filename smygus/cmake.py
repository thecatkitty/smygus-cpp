import cmake
import os
import re
import shutil
import subprocess

from . import logger


class CMake(object):
    def __init__(self) -> None:
        self.exe_path = os.path.join(cmake.CMAKE_BIN_DIR, 'cmake.exe')
        self.sources = None
        self.binaries = None

    def configure(self, generator: str, sources: str, binaries: str, defines: dict[str, str] = dict()) -> None:
        logger.log('', newline=False)
        self.sources = sources
        self.binaries = binaries

        shutil.rmtree(binaries, ignore_errors=True)
        subprocess.run([
            self.exe_path,
            '-G', generator,
            '-S', sources,
            '-B', binaries,
        ] + [
            f'-D{key}' if len(value) == 0 else f'-D{key}={value}'
            for key, value in defines.items()],
            check=True,
            env=os.environ)

    def patch_output(self, filenames: list[str], replacements: dict[str, str]):
        escaped = dict((re.escape(k), v) for k, v in replacements.items())
        pattern = re.compile("|".join(escaped.keys()))
        for path, _, files in os.walk(os.path.abspath(self.binaries)):
            for filename in files:
                if filename not in filenames:
                    continue

                full_path = os.path.join(path, filename)
                with open(full_path) as file:
                    content = file.read()

                if not any(key in content for key in replacements.keys()):
                    continue

                logger.log(f'Patching {full_path}')
                new_content = pattern.sub(
                    lambda m: escaped[re.escape(m.group(0))], content)
                with open(full_path, 'w') as file:
                    file.write(new_content)
