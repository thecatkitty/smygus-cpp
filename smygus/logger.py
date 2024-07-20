_nl = True


def log(message: str, newline: bool = True) -> None:
    global _nl
    if not _nl:
        print()

    print(message, end='\n' if newline else '', flush=True)
    _nl = newline


class ExecutionStep(object):
    def __init__(self, description: str) -> None:
        self.description = description

    def __enter__(self) -> 'ExecutionStep':
        log(self.description + '... ', newline=False)
        return self

    def __exit__(self, type, value, traceback) -> None:
        global _nl
        print('done')
        _nl = True


def step(description: str) -> ExecutionStep:
    return ExecutionStep(description)
