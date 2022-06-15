# ZoMake
A Python package to generate Makefiles for C/C++.

Other languages will be added later.

## Installation
```sh
python3 -m pip install zomake
```

## Usage
Create a ZoMakefile.py:
```py
import zo

target = zo.Target(lang='c')

target.sources(f'{zo.root()}/src',
    'main.c'
)

target.include(f'{zo.root()}/include')
target.compile(f'{zo.root()}/build')

target()
```

To generate a Makefile:
```sh
python3 ZoMakeFile.py init
```

To build:
```sh
python3 ZoMakeFile.py build
```
