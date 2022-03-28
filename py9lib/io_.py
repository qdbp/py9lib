import json
import pickle
from functools import wraps
from pathlib import Path
from time import sleep, time
from typing import Any, Callable, Generic, Iterable, Type, Union, cast

from py9lib.errors import value_assert
from py9lib.typing_ import F, P, V


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


def retry(
    catch: Iterable[Type[Exception]],
    backoff_start: float,
    backoff_rate: float,
    max_retries: int = None,
    log_fun: Callable[[str], None] = None,
) -> Callable[[Callable[P, V]], Callable[P, V]]:

    catch = tuple(catch)
    cur_backoff = backoff_start
    n_tries = 0

    def wrapper(f: Callable[P, V]) -> Callable[P, V]:
        @wraps(f)
        def wrapped(*args, **kwargs) -> V:  # type: ignore
            nonlocal n_tries
            nonlocal cur_backoff

            while True:
                try:
                    n_tries += 1
                    return f(*args, **kwargs)
                except catch as e:  # type: ignore
                    if max_retries is not None and n_tries > max_retries:
                        raise
                    if log_fun is not None:
                        log_fun(f"Retry caught {e}. {n_tries=}, {cur_backoff=}")
                    sleep(cur_backoff)
                    cur_backoff += backoff_rate

        return wrapped

    return wrapper


AnyPath = Union[str, Path]


def write_pickle(fn: AnyPath, obj: Any) -> None:
    with open(fn, "wb") as f:
        pickle.dump(f, obj)


def read_pickle(fn: AnyPath) -> Any:
    with open(fn, "rb") as f:
        return pickle.load(f)


def read_json(fn: AnyPath) -> dict[str, Any]:
    with open(fn, "rb") as f:
        return cast(dict[str, Any], json.load(f))


def write_json(fn: AnyPath, obj: dict[str, Any]) -> None:
    with open(fn, "w") as f:
        json.dump(obj, f)


def read_yaml(fn: AnyPath) -> dict[str, Any]:
    try:
        import yaml
    except ImportError as e:
        raise NotImplementedError("Yaml not available") from e

    with open(fn, "r") as f:
        return cast(dict[str, Any], yaml.load(f, Loader=yaml.FullLoader))


def write_yaml(fn: AnyPath, obj: dict[str, Any], **kwargs: Any) -> None:
    try:
        import yaml
    except ImportError as e:
        raise NotImplementedError("Yaml not available") from e

    with open(fn, "w") as f:
        yaml.dump(obj, f, default_flow_style=False, **kwargs)
