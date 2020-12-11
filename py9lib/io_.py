import json
import pickle
from functools import wraps
from time import sleep, time
from typing import Any, Dict, Generic, cast

from .typing_ import F
from .util import value_assert


# noinspection PyPep8Naming
class ratelimit(Generic[F]):
    def __init__(self, cap: int, period: float) -> None:
        value_assert(cap > 0) and value_assert(period > 1e-6)

        self.cap = cap
        self.period = period

        self.__pool: int = cap
        self.__last: float = time()

    # noinspection PyMethodParameters
    def __call__(limiter, f: F) -> F:
        # noinspection PyMissingTypeHints
        @wraps(f)
        def wrapper(*args, **kwargs):  # type: ignore
            while (
                new_pool := min(
                    limiter.cap,
                    limiter.__pool
                    + int(
                        ((t_call := time()) - limiter.__last) // limiter.period
                    ),
                )
            ) == 0:
                to_sleep = limiter.__last + limiter.period - t_call
                sleep(to_sleep)

            assert new_pool > 0
            limiter.__pool = new_pool - 1
            limiter.__last = t_call
            return f(*args, **kwargs)

        return cast(F, wrapper)


def write_pickle(fn: str, obj: Any) -> None:
    with open(fn, "wb") as f:
        pickle.dump(f, obj)


def read_pickle(fn: str) -> Any:
    with open(fn, "rb") as f:
        return pickle.load(f)


def read_json(fn: str) -> Dict[str, Any]:
    with open(fn, "rb") as f:
        return cast(Dict[str, Any], json.load(f))


def write_json(fn: str, obj: Dict[str, Any]) -> None:
    with open(fn, "w") as f:
        json.dump(obj, f)
