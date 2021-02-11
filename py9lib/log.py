from logging import (
    Formatter,
    Handler,
    Logger,
    StreamHandler,
    addLevelName,
    getLogger,
)
from sys import stdout

VERBOSE = 15
addLevelName(VERBOSE, "Verbose")


# class NiceFormatter(Formatter):
#     def format(self, record: LogRecord) -> str:
#
#         msg = super().format(record)
#
#         if hasattr(record, "color"):
#             msg = color(record.color, msg)
#
#         return msg
#
#
# class NiceFilter(Filter):
#     def filter(self, record: LogRecord) -> bool:
#
#         record.levelno


def get_nice_formatter() -> Formatter:
    return Formatter(
        fmt=(
            "{levelname:1.1s} | {asctime} | "
            "{filename}:{lineno}({funcName}) | {msg}"
        ),
        datefmt="%a %d %b %Y %H:%M:%S %Z",
        style="{",
    )


def get_basic_handler() -> Handler:
    return StreamHandler(stdout)


def get_logger(key: str) -> Logger:

    log = getLogger(key)

    log.handlers = [get_basic_handler()]
    log.handlers[0].setFormatter(get_nice_formatter())

    return log
