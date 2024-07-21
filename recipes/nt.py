from smygus import *


machine = None


@logger.step_func('Booting to Windows NT')
def boot(cdr: str) -> None:
    with logger.step('Launching the DingusPPC'):
        dingus = DingusPPC(cdr)
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

    global machine
    machine = dingus
