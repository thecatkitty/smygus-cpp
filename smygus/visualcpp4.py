import os
import subprocess


class VisualCPP4(object):
    def __init__(self, arch: str = 'x86') -> None:
        vcvars32 = subprocess.run(['C:\\MSDEV\\BIN\\VCVARS32.BAT', arch,
                                  '&&', 'set'], stdout=subprocess.PIPE, text=True, shell=True, check=True)
        lines = vcvars32.stdout.splitlines()
        assert lines[0].startswith('Setting environment')
        assert 'x86' in lines[0]

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
