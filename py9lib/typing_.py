from typing import Any, Callable, TypeVar

T = TypeVar("T")
V = TypeVar("V")
F = TypeVar("F", bound=Callable[..., Any])
