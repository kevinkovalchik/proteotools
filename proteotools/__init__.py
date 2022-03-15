from pathlib import Path

__version__ = '0.2.1'

TOOL_DIR = Path('~/.proteotools_software').expanduser()
COMET = TOOL_DIR / 'comet' / 'comet.linux.exe'
MSGF = TOOL_DIR / 'msgfplus' / 'MSGFPlus.jar'
TANDEM = TOOL_DIR / 'tandem' / 'bin' / 'static_link_ubuntu' / 'tandem.exe'
TPP = TOOL_DIR / 'tpp' / 'tpp_6-0-0.sif'
THERMORAWFILEPARSER = TOOL_DIR / 'ThermoRawFileParser' / 'ThermoRawFileParser.exe'
PROTEOWIZARD = TOOL_DIR / 'proteowizard' / 'proteowizard'
