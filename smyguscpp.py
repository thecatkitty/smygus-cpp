import sys
import time

from smygus import *

pmake = PowerPCCMake()
pmake.configure(sys.argv[1])

dingus = pmake.boot()

with logger.step('Launching the Command Prompt'):
    time.sleep(2)
    dingus.press('TAB').press('ENTER')
    dingus.wait(color='#C0C0C0', position=(180, 720))
    dingus.press('UP')
    dingus.wait(color='#000080', position=(180, 720))
    dingus.press('UP')
    dingus.wait(color='#000080', position=(180, 680))
    dingus.press('ENTER')
    dingus.wait(color='#000080', position=(300, 570))
    dingus.type('cmd').press('ENTER')

with logger.step('Preparing the working directory'):
    time.sleep(2)
    dingus.type('xcopy /e /i e:\\*.* "' +
                pmake.project_path + '"').press('ENTER')
    time.sleep(10)
    dingus.type('c:\\msdev\\bin\\vcvars32').press('ENTER')
    time.sleep(2)
    dingus.type('cd "' + pmake.project_path + '\\build"').press('ENTER')

with logger.step('Building'):
    time.sleep(2)
    dingus.type('nmake').press('ENTER')
