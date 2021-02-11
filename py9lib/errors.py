from typing import Literal


def value_assert(cond: bool, msg: str = None) -> Literal[True]:
    if not cond:
        raise ValueError(msg)
    return True


def runtime_assert(cond: bool, msg: str = None) -> Literal[True]:
    if not cond:
        raise RuntimeError(msg)
    return True


class ProgrammingError(BaseException):
    pass
