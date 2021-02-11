from functools import wraps
from time import time
from typing import Callable, Iterable, cast

from py9lib.typing_ import F, T


def take_where(what: Iterable[T], where: Iterable[bool]) -> Iterable[T]:
    """
    Iterates an iterable of values and hits, yielding values with True hints.

    Args:
        what: an iterable of values
        where: an iterable of boolean hints.

    Yields:
        the values from [what] corresponding to indices where [where] was True.
    """
    for it, whether in zip(what, where):
        if whether:
            yield it


def timed(printer: Callable[[str], None] = print) -> Callable[[F], F]:
    def wrapper(f: F) -> F:
        # noinspection PyMissingTypeHints
        @wraps(f)
        def wrapped(*args, **kwargs):  # type: ignore
            t0 = time()
            out = f(*args, **kwargs)
            t1 = time()
            printer(f"{f.__name__} executed in {t1 - t0:.3f} seconds.")
            return out

        return cast(F, wrapped)

    return wrapper
