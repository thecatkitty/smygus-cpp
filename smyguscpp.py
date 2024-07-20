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
