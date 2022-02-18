from proteotools import TPP
from proteotools.software import check_for_singularity
from typing import Union, List
from subprocess import Popen, SubprocessError
from os import PathLike
from pathlib import Path


def tool_help(tool: str):
    check_for_singularity()

    singularity_command = ['singularity', 'exec', str(TPP), tool]

    p = Popen(singularity_command)
    _ = p.communicate()


def run_tool(tool: str, command: Union[str, List[str]], path_to_bind: Union[str, PathLike] = '~/'):
    check_for_singularity()

    if isinstance(command, str):
        command = command.split()

    singularity_command = ['singularity', 'exec', '-B', str(path_to_bind), str(TPP), tool, *command]

    p = Popen(singularity_command)
    _ = p.communicate()

    if p.returncode != 0:
        raise SubprocessError(f'There was an error running {tool}. See the above output.')


def run_interactparser(pepxml_files: List[Union[str, PathLike]],
                       fasta: Union[str, PathLike],
                       enzyme: str = 'nonspecific',
                       mzml_directory: Union[str, PathLike] = None,
                       max_peptide_rank: int = 1
                       ) -> List[Path]:

    if mzml_directory is None:
        mzml_directory = Path(pepxml_files[0]).parent
    if str(mzml_directory) != str(Path(pepxml_files[0]).parent):
        bind_point = f'{mzml_directory},{Path(pepxml_files[0]).parent}'
    else:
        bind_point = mzml_directory
    interact_output = []
    for pepxml in pepxml_files:
        print(f'InteractParser: {pepxml}')
        pepxml = Path(pepxml)
        output = pepxml.parent / f'interact-{pepxml.name}'
        run_tool('InteractParser',
                 f'{output} {pepxml} -a{mzml_directory} -D{fasta} -E{enzyme} -C -S -R{max_peptide_rank}',
                 path_to_bind=bind_point)
        interact_output.append(output)

    return interact_output


def run_peptideprophet(pepxml_files: List[Union[str, PathLike]],
                       decoy_tag: str = 'rev_',
                       additional_args: List[str] = ('ZERO', 'NONPARAM', 'DECOYPROBS')):
    for pepxml in pepxml_files:
        print(f'PeptideProphet: {pepxml}')
        pepxml = Path(pepxml)
        bind_point = pepxml.parent
        decoy = f' DECOY={decoy_tag}' if decoy_tag is not None else None
        run_tool('PeptideProphetParser',
                 f'{pepxml} {" ".join(additional_args)}{decoy}',
                 path_to_bind=bind_point)


def run_iprophet(pepxml_files: List[Union[str, PathLike]],
                 decoy_tag: str = 'rev_',
                 threads: int = 12,
                 minprob: float = 0,
                 output_filename: str = 'interact-iproph.pep.xml',
                 additional_args: List[str] = None):
    """

    :param pepxml_files: Should all be in the same directory.
    :param decoy_tag:
    :param threads:
    :param minprob:
    :param output_filename:
    :param additional_args:
    :return:
    """
    bind_point = Path(pepxml_files[0]).parent
    output_file = bind_point / output_filename
    if additional_args is not None:
        additional_args = ' ' + ' '.join(additional_args)
    else:
        additional_args = ''
    run_tool('InterProphetParser',
             f'THREADS={threads} DECOY={decoy_tag} MINPROB={minprob}{additional_args} '
             f'{" ".join([str(x) for x in pepxml_files])} {output_file}',
             path_to_bind=bind_point)


def run_prophets(pepxml_files: List[Union[str, PathLike]],
                 fasta: Union[str, PathLike],
                 decoy_tag: str = 'rev_',
                 enzyme: str = 'nonspecific',
                 peptide_prophet_flags: List[str] = ('ZERO', 'NONPARAM', 'DECOYPROBS'),
                 iprophet_flags: List[str] = None,
                 iprophet_out_filename: str = 'interact-iproph.pep.xml',
                 threads: int = 12,
                 iprophet_minprob: float = 0,
                 mzml_directory: Union[str, PathLike] = None,
                 skip_existing_interact_pepxmls: bool = True,
                 max_peptide_rank: int = 1):
    if mzml_directory is None:
        mzml_directory = Path(pepxml_files[0]).parent

    if skip_existing_interact_pepxmls:
        pepxml_files = [x for x in pepxml_files if not Path(x).name.startswith('interact-')]

    interact_files = run_interactparser(pepxml_files=pepxml_files,
                                        fasta=fasta,
                                        enzyme=enzyme,
                                        mzml_directory=mzml_directory,
                                        max_peptide_rank=max_peptide_rank
                                        )

    run_peptideprophet(interact_files,
                       decoy_tag=decoy_tag,
                       additional_args=peptide_prophet_flags)

    run_iprophet(interact_files,
                 decoy_tag=decoy_tag,
                 threads=threads,
                 minprob=iprophet_minprob,
                 additional_args=iprophet_flags,
                 output_filename=iprophet_out_filename)

