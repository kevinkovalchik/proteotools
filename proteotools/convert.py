from proteotools import THERMORAWFILEPARSER
from proteotools.software import check_for_thermorawfileparser
from typing import List, Union, Literal
from os import PathLike
from pathlib import Path
from subprocess import Popen, SubprocessError


def run_thermorawfileparser(input: Union[str, PathLike, List[Union[str, PathLike]]],
                            output_directory: Union[str, PathLike] = None,
                            format: Literal['mgf', 'mzml', 'indexed_mzml', 'parquet'] = 'indexed_mzml',
                            metadata_output_file: Union[str, PathLike] = None,
                            gzip_output: bool = False,
                            no_peak_picking: bool = False,
                            no_zlib_compression: bool = False,
                            clobber: bool = False) -> List[str]:
    check_for_thermorawfileparser()
    mzml_files: List[str] = []
    possible_formats = ['mgf', 'mzml', 'indexed_mzml', 'parquet']

    if isinstance(input, (str, PathLike)):
        input = Path(input)

    if isinstance(input, Path):
        input = [input]

    for i in input:
        if i.is_dir():
            file_list = i.glob('*.raw')
        else:
            file_list = [i]

        for raw_file in file_list:
            if not clobber:
                if raw_file.with_suffix('.mzML').exists():
                    mzml_files.append(str(raw_file.with_suffix('.mzML')))
                    continue
            if output_directory is None:
                out_dir = raw_file.parent
            else:
                out_dir = output_directory
            command = f'mono {THERMORAWFILEPARSER} -i {raw_file} -o {out_dir} -f {possible_formats.index(format)}'
            if metadata_output_file is not None:
                command += f' -c {metadata_output_file}'
            if gzip_output is True:
                command += ' -g'
            if no_peak_picking is True:
                command += ' -p'
            if no_zlib_compression is True:
                command += ' -z'

            p = Popen(command.split())
            _ = p.communicate()
            if p.returncode != 0:
                raise SubprocessError('Something went wrong while running ThermoRawFileParser. '
                                      'Inspect the above output.')

            mzml_files.append(str(raw_file.with_suffix('.mzML')))

    return mzml_files
