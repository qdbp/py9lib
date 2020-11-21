from random import random
from time import time
from typing import Any, Callable

import pytest

from py9lib.io_ import ratelimit


def foo():
    return None


def timeit(f: Callable[..., Any], n_calls: int) -> float:
    t0 = time()
    for i in range(n_calls):
        f()
    return time() - t0


def test_basic():

    with pytest.raises(ValueError):
        ratelimit(1, 0)

    with pytest.raises(ValueError):
        ratelimit(0, 1)

    # test we don't crash
    ratelimit(1, 1)(foo)()


def test_simple():

    get_f = lambda: ratelimit(3, 0.1)(foo)

    assert timeit(get_f(), 1) < 0.01
    assert timeit(get_f(), 3) < 0.01
    assert timeit(get_f(), 5) > 0.2

    get_f = ratelimit(1, 0.2)(foo)
    assert timeit(get_f, 1) < 0.01
    assert timeit(get_f, 2) > 0.2


def test_microfuzz():

    for pool in range(1, 4):
        for n_calls in range(1, 4):
            for _ in range(5):
                timeit(ratelimit(pool, 1e-6 + random() * 1e-3)(foo), n_calls)
