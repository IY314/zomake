from argparse import ArgumentParser
import dataclasses
import os
import subprocess
import sys


@dataclasses.dataclass(kw_only=True)
class Target:
    lang: str = 'c'
    name: str = 'target'
    btype: str = 'exec'

    def __post_init__(self):
        self._warn_flags = []
        self._source_dir = f'{root()}/src'
        self._sources = []
        self._include_dirs = []
        self._libs = []
        self._lib_dirs = []
        self._output_dir = f'{root()}/build'
        self._output = self.name
        self._ext = {
            'c': 'c',
            'cpp': 'cpp',
        }[self.lang]

        self._compiler = {
            'c': 'CC',
            'cpp': 'CXX',
        }[self.lang]

    def warn(self, *flags):
        self._warn_flags = [f'-W{flag}' for flag in flags]

    def include(self, *paths):
        self._include_dirs.extend(paths)

    def link(self, *, paths, libs):
        self._lib_dirs.extend(paths)
        self._libs.extend(libs)

    def sources(self, path, *sources):
        self._source_dir = path
        self._sources.extend((os.path.join(path, src) for src in sources))

    def compile(self, path):
        self._output_dir = path
        self._output = os.path.join(path, self.name)

        if not self._sources:
            raise Exception('No sources specified')

    def __call__(self):
        if len(sys.argv) < 2:
            raise Exception('No command specified')

        parser = ArgumentParser()

        parser.add_argument('-B', '--build-dir', default=f'{root()}/build/ZoMake')
        args, other = parser.parse_known_args(sys.argv[2:])

        self._build_dir = args.build_dir

        if sys.argv[1] == 'init':
            self._build_makefile()
        elif sys.argv[1] == 'build':
            if not os.path.exists(self._build_dir):
                raise Exception('No ZoMake directory found')
            subprocess.run(['make', '-C', self._build_dir, '-B', *other])
        elif sys.argv[1] == 'clean':
            pass

    def _build_makefile(self):
        if not os.path.exists(self._build_dir):
            os.makedirs(self._build_dir, exist_ok=True)
        with open(f'{self._build_dir}/Makefile', 'w') as f:
            if hasattr(self, 'compiler'):
                f.write(f'{self._compiler} := {self.compiler}\n')

            if hasattr(self, 'std'):
                f.write(f'STD := -std={self.std}\n')

            if self._lib_dirs:
                f.write(f'LIBDIRS := {" ".join(self._lib_dirs)}\n')

            if self._libs:
                f.write(f'LIBS := {" ".join(self._libs)}\n')

            if self._include_dirs:
                f.write(f'INCLUDES := {" ".join(self._include_dirs)}\n')

            if self._warn_flags:
                f.write(f'WARN := {" ".join(self._warn_flags)}\n')

            f.write(f'TARGET := {self._output}\n')
            f.write(f'SOURCES := {" ".join(self._sources)}\n')
            f.write(f'OBJECTS := $(patsubst {self._source_dir}/%.{self._ext}, {self._output_dir}/%.o, $(SOURCES))\n')

            f.write(f'all: $(TARGET)\n')

            f.write(f'$(TARGET): $(OBJECTS)\n')
            f.write(f'\t$({self._compiler}) $(WARN) $(STD) $^ $(LIBS) -o $@\n')

            f.write(f'{self._output_dir}/%.o: {self._source_dir}/%.{self._ext} {self._output_dir}\n')
            f.write(f'\t$({self._compiler}) $(WARN) $(STD) $(INCLUDES) -c $< -o $@\n')

            f.write(f'{self._output_dir}:\n')
            f.write(f'\tmkdir -p {self._output_dir}\n')

            f.write(f'clean: clean-obj clean-exec\n')

            f.write(f'clean-obj:\n')
            f.write(f'\trm -f $(OBJECTS)\n')

            f.write(f'clean-exec:\n')
            f.write(f'\trm -f $(TARGET)\n')


def root():
    return os.getcwd()
