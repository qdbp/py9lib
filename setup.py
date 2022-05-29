from setuptools import setup  # type: ignore

__version__ = "0.8.0"

setup(
    name="py9lib",
    version=__version__,
    packages=["py9lib"],
    package_data=dict(py9lib=["py.typed"]),
    url="http://github.com/qdbp/py9lib.git",
    license="",
    author="Evgeny Naumov",
    description="utility code",
    extras_require={"yaml": ["pyyaml"]},
    python_requires=">=3.10",
)
