from proteotools import PROTEOWIZARD
from proteotools.software import check_for_singularity
from typing import Union, List, Literal
from subprocess import Popen, SubprocessError
from os import PathLike
from pathlib import Path


def tool_help(tool: str):
    check_for_singularity()

    singularity_command = f'singularity exec --writable-tmpfs {PROTEOWIZARD} wine {tool}'.split()

    p = Popen(singularity_command)
    _ = p.communicate()


def run_tool(tool: str,
             command: Union[str, List[str]],
             path_to_bind: Union[str, PathLike] = '~/',
             disable_tmpfs: bool = False):

    check_for_singularity()

    if isinstance(command, list):
        command = ' '.join(command)

    if not disable_tmpfs:
        singularity_command = f'singularity exec --writable-tmpfs -B {path_to_bind} {PROTEOWIZARD} wine {tool} ' \
                              f'{command}'.split()
    else:
        singularity_command = f'singularity exec -B {path_to_bind} {PROTEOWIZARD} wine {tool} {command}'.split()

    p = Popen(singularity_command)
    _ = p.communicate()

    if p.returncode != 0:
        raise SubprocessError(f'There was an error running {tool}. See the above output.')


def run_idconvert(input_file,
                  output_directory,
                  output_extension,
                  format: Literal['pepXML', 'mzIdentML', 'text'] = 'pepXML',
                  disable_tmpfs: bool = False):
    command = f'{input_file} -o {output_directory} -e {output_extension} --{format}'.split()
    run_tool('idconvert', command, path_to_bind=Path(input_file).parent, disable_tmpfs=disable_tmpfs)
