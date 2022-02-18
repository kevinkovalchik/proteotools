from pathlib import Path
from subprocess import Popen, PIPE
from zipfile import ZipFile
import os
from proteotools import TOOL_DIR, COMET, TANDEM, MSGF, THERMORAWFILEPARSER


def download_search_engines():

    if not TOOL_DIR.exists():
        TOOL_DIR.mkdir()

    downloads = TOOL_DIR / 'downloads'

    if not downloads.exists():
        downloads.mkdir()

    msgfplus = 'https://github.com/MSGFPlus/msgfplus/releases/download/v2022.01.10/MSGFPlus_v20220107.zip'
    xtandem = 'http://ftp.thegpm.org/projects/tandem/source/tandem-linux-17-02-01-4.zip'
    comet = 'https://github.com/UWPR/Comet/releases/download/v2021.02.0/comet.linux.exe'

    for url in [msgfplus, xtandem, comet]:
        name = Path(url).name

        command = f'wget -O {downloads/name} {url}'.split()
        p = Popen(command)
        _ = p.communicate()
        if p.returncode != 0:
            raise ConnectionError(f"There was a problem downloading {url}. Check the above output.")

        if 'tandem-linux' in name:
            zipfile = ZipFile(downloads / name)
            zipfile.extractall(path=downloads)
            (downloads / 'tandem-linux-17-02-01-4').rename(TOOL_DIR / 'tandem')
            _ = Popen(['chmod', '+x', TANDEM]).communicate()
        elif 'comet.linux' in name:
            if not (TOOL_DIR / 'comet').exists():
                (TOOL_DIR / 'comet').mkdir()
            (downloads / 'comet.linux.exe').rename(TOOL_DIR / 'comet' / 'comet.linux.exe')
            _ = Popen(['chmod', '+x', COMET]).communicate()
        elif 'MSGFPlus' in name:
            zipfile = ZipFile(downloads / name)
            zipfile.extractall(path=TOOL_DIR / 'msgfplus')


def check_for_thermorawfileparser():
    command = 'mono --version'.split()
    p = Popen(command, stdout=PIPE)
    _ = p.communicate()

    if p.returncode != 0:
        raise OSError('Mono does not appear to be installed. Mono is required for running ThermoRawFileParser.')

    command = f'mono {THERMORAWFILEPARSER} --version'.split()
    p = Popen(command, stdout=PIPE)
    _ = p.communicate()

    if p.returncode != 0:
        raise OSError('ThermoRawFileParser does not appear to be installed. It is required to convert Thermo '
                      'raw files.')


def download_thermorawfileparser():
    url = 'https://github.com/compomics/ThermoRawFileParser/releases/download/v1.3.4/ThermoRawFileParser.zip'

    if not TOOL_DIR.exists():
        TOOL_DIR.mkdir()

    downloads = TOOL_DIR / 'downloads'

    if not downloads.exists():
        downloads.mkdir()

    name = Path(url).name

    command = f'wget -O {downloads / name} {url}'.split()
    p = Popen(command)
    _ = p.communicate()
    if p.returncode != 0:
        raise ConnectionError(f"There was a problem downloading {url}. Check the above output.")

    zipfile = ZipFile(downloads / name)
    zipfile.extractall(path=TOOL_DIR / 'ThermoRawFileParser')


def check_for_singularity():
    command = 'singularity --version'.split()
    p = Popen(command, stdout=PIPE)
    _ = p.communicate()

    if p.returncode != 0:
        raise OSError('Singularity does not appear to be installed. Singularity is required for for running TPP tools.')


def check_for_comet():
    if not Path(COMET).exists():
        raise EnvironmentError('Comet not found. If you have not, run "proteotools.software.download_search_engines(). '
                               'Otherwise, check the above output for more information.')


def check_for_tandem():
    if not Path(TANDEM).exists():
        raise EnvironmentError('X! Tandem not found. If you have not, run "proteotools.software.download_search_engines(). '
                               'Otherwise, check the above output for more information.')


def check_for_msgfplus():
    if not Path(MSGF).exists():
        raise EnvironmentError('MS-GF+ not found. If you have not, run "proteotools.software.download_search_engines(). '
                               'Otherwise, check the above output for more information.')


def get_tpp():

    check_for_singularity()

    if not (TOOL_DIR / 'tpp').exists():
        (TOOL_DIR / 'tpp').mkdir()

    command = f'singularity pull library://kkovalchik/tpp/tpp:6-0-0'.split()

    cwd = os.getcwd()
    os.chdir(TOOL_DIR / 'tpp')
    p = Popen(command)
    _ = p.communicate()
    os.chdir(cwd)

    if p.returncode != 0:
        raise OSError('There was a problem pulling the TPP Singularity image. Please see the above output.')


def download_all():
    download_search_engines()
    get_tpp()
    download_thermorawfileparser()

    check_for_thermorawfileparser()
    check_for_msgfplus()
    check_for_tandem()
    check_for_comet()
    check_for_singularity()
