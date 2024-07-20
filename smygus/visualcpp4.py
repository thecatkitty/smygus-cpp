import os
import subprocess


class VisualCPP4(object):
    def __init__(self, arch: str = 'x86') -> None:
        vcvars32 = subprocess.Popen(
            ['C:\\MSDEV\\BIN\\VCVARS32.BAT', arch, '&&', 'set'], stdout=subprocess.PIPE, shell=True)
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

        self.projects_path = 'C:\\MSDEV\\PROJECTS'
