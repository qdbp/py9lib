from time import sleep, time
from typing import Generic, cast

from .typing_ import F
from .util import value_assert


class ratelimit(Generic[F]):
    def __init__(self, cap: int, period: float) -> None:
        value_assert(cap > 0) and value_assert(period > 1e-6)

        self.cap = cap
        self.period = period

        self.__pool: int = cap
        self.__last: float = time()

    # noinspection PyMethodParameters
    def __call__(limiter, f: F) -> F:
        def wrapper(*args, **kwargs):
            print(f"call: pool = {limiter.__pool}")
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
                print(f"sleep {to_sleep}")
                sleep(to_sleep)

            assert new_pool > 0
            limiter.__pool = new_pool - 1
            limiter.__last = t_call
            return f(*args, **kwargs)

        return cast(F, wrapper)
