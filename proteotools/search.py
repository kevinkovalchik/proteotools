from proteotools import COMET, TANDEM, MSGF, TPP
from pathlib import Path
from subprocess import Popen, SubprocessError
from proteotools.software import check_for_tandem, check_for_comet, check_for_msgfplus
import proteotools.tpp as tpp


def comet(parameter_file, fasta, *mzml_files):
    check_for_comet()
    for mzml in mzml_files:
        name = Path(mzml).stem
        name = Path(mzml).parent / (name + '-comet')
        command = f'{COMET} -D{fasta} -P{parameter_file} -N{name} {mzml}'.split()
        p = Popen(command)
        _ = p.communicate()

        if p.returncode != 0:
            raise SubprocessError('Something went wrong while running Comet. Inspect the above output.')

        Path(f'{name}.pep.xml').rename(name.parent / f'{name}.pepXML')


def msgfplus(parameter_file, fasta, *mzml_files, decoy_prefix: str = 'rev_', convert_to_pepxml: bool = True,
             memory: str = '8000M'):
    check_for_msgfplus()
    for mzml in mzml_files:
        name = Path(mzml).stem
        mzid = Path(mzml).parent / (name + '-msgf_plus.mzid')
        command = f'java -Xmx{memory} -jar {MSGF} -conf {parameter_file} -decoy {decoy_prefix} -tda 0 ' \
                  f'-d {fasta} -o {mzid} -s {mzml}'.split()
        p = Popen(command)
        _ = p.communicate()

        if p.returncode != 0:
            raise SubprocessError('Something went wrong while running MS-GF+. Inspect the above output.')

        if convert_to_pepxml:
            command = f'singularity exec -B {Path(mzid).parent} {TPP} idconvert {mzid} --pepXML ' \
                      f'-o {Path(mzid).parent} -e -msgf_plus.pepXML'.split()
            p = Popen(command)
            _ = p.communicate()
            if p.returncode != 0:
                raise SubprocessError('Something went wrong while running idconvert. Inspect the above output.')


def tandem(parameter_file, fasta, *mzml_files):
    check_for_tandem()
    output_dir = Path(mzml_files[0]).expanduser().parent
    # we don't convert the tandem xml files to pepxml here. the output doesn't seem to be compatible with TPP tools
    command = f'runtandem -i {parameter_file} -db {fasta} --noconvert --overwrite -o {output_dir} --tandem.exe {TANDEM} -v 2 ' \
              f'{" ".join(mzml_files)}'.split()
    p = Popen(command)
    _ = p.communicate()
    if p.returncode != 0:
        raise SubprocessError('Something went wrong while running X! Tandem. Inspect the above output.')

    # convert to pepXML
    for mzml in mzml_files:
        txml = Path(str(mzml).replace('.mzML', '.t.xml'))
        t_pepxml = str(txml).replace('.t.xml', '-tandem.pepXML')
        bind_point = Path(mzml).parent
        tpp.run_tool('Tandem2XML',
                     f'{txml} {t_pepxml}',
                     path_to_bind=bind_point)


        '''new_pepxml = pepxml.parent / pepxml.name.replace('.pep.xml', '-tandem.pepXML')
        pepxml.rename(new_pepxml)

        # fix the basename tags - they have a .t.xml extension, but should have no extension
        t_xml = Path(str(mzml).replace('.mzML', '.t.xml'))
        incorrect_basename = f'base_name="{t_xml}"'
        correct_basename = f'base_name="{str(t_xml).replace(".t.xml", "")}"'
        with open(new_pepxml, 'r') as f:
            contents = f.read()
        contents = contents.replace(incorrect_basename, correct_basename)
        with open(new_pepxml, 'w') as f:
            f.write(contents)'''
