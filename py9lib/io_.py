import json
import pickle
from functools import wraps
from pathlib import Path
from time import sleep, time
from typing import Any, Generic, Union, cast

from py9lib.errors import value_assert
from py9lib.typing_ import F


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
