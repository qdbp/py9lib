import asyncio
from asyncio import ensure_future, gather, sleep, wait, wait_for
from functools import wraps
from heapq import heappop, heappush
from time import time
from typing import (
    AsyncGenerator,
    AsyncIterable,
    Awaitable,
    Callable,
    Generic,
    Iterable,
    List,
    Tuple,
    Type,
)

from py9lib.typing_ import T, V
from py9lib.util import value_assert


# noinspection PyPep8Naming
class aratelimit(Generic[V]):
    def __init__(self, cap: int, period: float) -> None:
        value_assert(cap > 0) and value_assert(period > 1e-6)

        self.cap = cap
        self.period = period

        self.__pool: int = cap
        self.__last: float = time()

    # noinspection PyMethodParameters
    def __call__(
        limiter, f: Callable[..., Awaitable[V]]
    ) -> Callable[..., Awaitable[V]]:
        # noinspection PyMissingTypeHints

        async def wrapper(*args, **kwargs) -> V:  # type: ignore
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
                await sleep(to_sleep)

            assert new_pool > 0
            limiter.__pool = new_pool - 1
            limiter.__last = t_call
            return await f(*args, **kwargs)

        return wrapper


async def exec_par_yield_seq(
    args: AsyncGenerator[T, None],
    task: Callable[[T], Awaitable[V]],
    parallelism: int = 5,
    wait_timeout: float = 1.0,
    task_timeout: float = 5.0,
    max_backup: int = None,
) -> AsyncGenerator[V, None]:
    """
    This function takes an async task, and a list of arguments for said task.
    It executes up to [parallelism] instances of the task asynchronously at any
    one time, and yields the results in the same order as the arguments list.

    If tasks finish out of order, results are withheld until the next needed
    task finishes.

    Args:
        args: iterable of arguments, which will be passed to the task
            one at a time
        task: the asynchronous function returning an awaitable for each argument
        parallelism: the number of tasks to try and execute in parallel at
            any given time.
        wait_timeout: how long [asyncio.wait] on the list of tasks scheduled
            to run in parallel at any given iteration.
        task_timeout: the individual tasks will be considered to have timed out
            if not completed in this time.
        max_backup: will stop adding new tasks to the queue if the current
            task index is greater than the next expected return index by this
            amount or more.

    Yields:
        the results of awaiting on [task] on each of the [args], in order of
        [args].
    """

    futures = set()
    max_backup = max_backup or 3 * parallelism

    # noinspection PyShadowingNames
    async def tagged(ix: int, arg: T) -> Tuple[int, V]:
        timeout_ctr = 0
        while True:
            try:
                out = await wait_for(task(arg), timeout=task_timeout)
                return ix, out
            except asyncio.TimeoutError:
                timeout_ctr += 1
                if timeout_ctr == 5:
                    print(f"{arg} timed out 5 times, check your task_timeout")
                continue

    heap: List[Tuple[int, V]] = []
    yield_ix = 0

    async for ix, arg in aenumerate(args):
        futures.add(ensure_future(tagged(ix=ix, arg=arg)))

        if len(futures) < parallelism and ix - yield_ix < max_backup:
            continue

        done, futures = await wait(futures, timeout=wait_timeout)

        for fut in done:
            res_ix, res = fut.result()
            heappush(heap, (res_ix, res))

        while heap and heap[0][0] == yield_ix:
            yield heappop(heap)[1]
            yield_ix += 1

    # once we exhaust our args, we wait for the rest to complete, then yield
    # them in order
    rest = await gather(*futures)
    for ix, res in sorted(rest):
        heappush(heap, (ix, res))

    while heap:
        yield heappop(heap)[1]


async def aenumerate(xs: AsyncIterable[T]) -> AsyncIterable[Tuple[int, T]]:

    ix = 0
    async for x in xs:
        yield ix, x
        ix += 1


def retry(
    catch: Iterable[Type[Exception]],
    backoff_start: float,
    backoff_rate: float,
    max_retries: int = None,
    log_fun: Callable[[str], None] = None,
) -> Callable[[Callable[..., Awaitable[V]]], Callable[..., Awaitable[V]]]:

    catch = tuple(catch)
    cur_backoff = backoff_start
    n_tries = 0

    def wrapper(f: Callable[..., Awaitable[V]]) -> Callable[..., Awaitable[V]]:
        @wraps(f)
        async def wrapped(*args, **kwargs) -> V:  # type: ignore
            nonlocal n_tries
            nonlocal cur_backoff

            while True:
                try:
                    n_tries += 1
                    return await f(*args, **kwargs)
                except catch as e:  # type: ignore
                    if max_retries is not None and n_tries > max_retries:
                        raise
                    if log_fun is not None:
                        log_fun(f"Retry caught {e}. {n_tries=}, {cur_backoff=}")
                    await sleep(cur_backoff)
                    cur_backoff += backoff_rate

        return wrapped

    return wrapper
