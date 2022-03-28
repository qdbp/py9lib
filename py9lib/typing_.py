from typing import Any, Callable, Hashable, ParamSpec, TypeVar

P = ParamSpec("P")
T = TypeVar("T")
V = TypeVar("V")
F = TypeVar("F", bound=Callable[..., Any])
H = TypeVar("H", bound=Hashable)
