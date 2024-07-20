import sys
import time

from smygus import *

pmake = PowerPCCMake()
pmake.configure(sys.argv[1])

dingus = pmake.boot()
print('Launching the Command Prompt...', end=' ', flush=True)
time.sleep(0.5)
dingus.type_keys('{TAB down}{TAB up}{ENTER down}{ENTER up}')
time.sleep(2)
dingus.type_keys('{UP down}{UP up}{UP down}{UP up}')
time.sleep(1)
dingus.type_keys('{ENTER down}{ENTER up}')
time.sleep(1)
dingus.type_keys(
    '{c down}{c up}{m down}{m up}{d down}{d up}{ENTER down}{ENTER up}')
print('done')
