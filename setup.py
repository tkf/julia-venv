from setuptools import setup, find_packages

setup(
    name="julia-venv",
    version="0.0.0",
    packages=find_packages("src"),
    package_dir={"": "src"},
    package_data={"julia_venv": ["*.jl"]},
    author="Takafumi Arakaki",
    author_email="aka.tkf@gmail.com",
    # url="https://github.com/tkf/julia-venv",
    license="MIT",  # SPDX short identifier
    # description="julia-venv - THIS DOES WHAT",
    long_description=open("README.rst").read(),
    # keywords="KEYWORD, KEYWORD, KEYWORD",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        # see: http://pypi.python.org/pypi?%3Aaction=list_classifiers
    ],
    install_requires=[
        "julia",
    ],
    entry_points={
        "console_scripts": [
            "julia-venv = julia_venv.shim:main",
            "julia-venv-manage = julia_venv.manage:main",
        ],
    },
    zip_safe=False,
)
