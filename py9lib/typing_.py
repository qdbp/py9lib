from typing import Any, Callable, Hashable, TypeVar

T = TypeVar("T")
V = TypeVar("V")
F = TypeVar("F", bound=Callable[..., Any])
H = TypeVar("H", bound=Hashable)
