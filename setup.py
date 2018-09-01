from setuptools import setup, find_packages

setup(
    name="julia-shim",
    version="0.0.0",
    packages=find_packages("src"),
    package_dir={"": "src"},
    author="Takafumi Arakaki",
    author_email="aka.tkf@gmail.com",
    # url="https://github.com/tkf/julia-shim",
    license="MIT",  # SPDX short identifier
    # description="julia-shim - THIS DOES WHAT",
    long_description=open("README.rst").read(),
    # keywords="KEYWORD, KEYWORD, KEYWORD",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        # see: http://pypi.python.org/pypi?%3Aaction=list_classifiers
    ],
    install_requires=[
        # "SOME_PACKAGE",
    ],
    # entry_points={
    #     "console_scripts": ["PROGRAM_NAME = julia_shim.cli:main"],
    # },
)
