from random import random
from time import time
from typing import Any, Awaitable, Callable

import pytest

from py9lib.async_ import aratelimit


async def foo():
    return None


async def timeit(f: Callable[..., Awaitable[Any]], n_calls: int) -> float:
    t0 = time()
    for i in range(n_calls):
        await f()
    return time() - t0


@pytest.mark.asyncio
async def test_basic():

    with pytest.raises(ValueError):
        aratelimit(1, 0)

    with pytest.raises(ValueError):
        aratelimit(0, 1)

    # test we don't crash
    await aratelimit(1, 1)(foo)()


@pytest.mark.asyncio
async def test_simple():

    get_f = lambda: aratelimit(3, 0.1)(foo)

    assert await timeit(get_f(), 1) < 0.01
    assert await timeit(get_f(), 3) < 0.01
    assert await timeit(get_f(), 5) > 0.2

    get_f = aratelimit(1, 0.2)(foo)
    assert await timeit(get_f, 1) < 0.01
    assert await timeit(get_f, 2) > 0.2


@pytest.mark.asyncio
async def test_microfuzz():

    for pool in range(1, 4):
        for n_calls in range(1, 4):
            for _ in range(5):
                await timeit(
                    aratelimit(pool, 1e-6 + random() * 1e-3)(foo), n_calls
                )
