from functools import wraps
from time import time
from typing import Callable, Iterable, Type, cast

from py9lib.typing_ import F, P, T, V


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


def suppress(
    exc: Type[Exception],
    retval: T = None,
    *,
    logger: Callable[[str], None] = None,
) -> Callable[[Callable[P, V]], Callable[P, V | T]]:
    """
    An indentaiton-friendly try/catch decorator.

    Suppresses any instance of `exc` in the wrapped function, returning `retval`
    instead when such is caught. Optionally logs suppressions.

    Args:
        exc: type of exception to catch
        retval: value to return when the function raises
        logger: callable accepting a string that will be invoked on suppression.
            Presumably for logging.
    """

    def _wrapper(f: Callable[P, V]) -> Callable[P, T | V]:
        @wraps(f)
        def _wrapped(*args: P.args, **kwargs: P.kwargs) -> T | V:
            try:
                return f(*args, **kwargs)
            except exc as e:
                if logger:
                    logger(f"Suppressed exception in {f.__name__}: '{e}'")
                # mypy can't figure out that if retval is None then T == NoneType
                # satisfying return type == T | V
                return retval  # type: ignore

        return _wrapped

    return _wrapper
