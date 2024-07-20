import sys
import time

from smygus import *

pmake = PowerPCCMake()
pmake.configure(sys.argv[1])

dingus = pmake.boot()
print('Launching the Command Prompt...', end=' ', flush=True)
time.sleep(0.5)
dingus.press('TAB').press('ENTER')
time.sleep(2)
dingus.press('UP').press('UP')
time.sleep(1)
dingus.press('ENTER')
time.sleep(1)
dingus.type('cmd').press('ENTER')
print('done')

print('Preparing the working directory...', end=' ', flush=True)
time.sleep(0.5)
dingus.type('xcopy /e /i e:\\*.* "' + pmake.project_path + '"').press('ENTER')
time.sleep(10)
dingus.type('c:\\msdev\\bin\\vcvars32').press('ENTER')
time.sleep(1)
dingus.type('cd "' + pmake.project_path + '\\build"').press('ENTER')
print('done')

print('Building...', end=' ', flush=True)
time.sleep(0.5)
dingus.type('nmake').press('ENTER')
print('done')
