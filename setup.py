from setuptools import setup  # type: ignore

__version__ = "0.6.20201211145450"

setup(
    name="py9lib",
    version=__version__,
    packages=["py9lib"],
    package_data=dict(py9lib=["py.typed"]),
    url="http://github.com/qdbp/py9lib.git",
    license="",
    author="Evgeny Naumov",
    description="utility code",
)
