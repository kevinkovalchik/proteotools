# proteotools

A simple Python package which lets you programmatically convert Thermo raw files using ThermoRawFileParser, run a 
few proteomics search engines (Comet, X! Tandem, MS-GF+), and use Trans-Proteomic Pipeline (TPP) 
binaries without needing to compile them on your computer, all from within Python!

Note that this does not run the entire TPP. For example, you don't get to use the fancy GUI or anything. It is 
simply a way to run compiled TPP tools such as PeptideProphet, InterProphetParser, idconvert, etc without needing to 
compile the entire pipeline on your computer.

TPP tools are run from a Singularity image, so an installation of Singularity is required. ThermoRawFileParser runs 
in Linux using Mono, so you need that too.

## Requirements
`proteotools` only runs in Linux. Mostly the reason for this (in fact, probably entirely) is thatI have not made it 
check the OS and select the appropriate downloads and binaries. I use Ubuntu and I wrote this for myself. If anyone 
wishes to use it on another OS please raise an issue and I'll check it out.

`proteotools` requires Singularity to be installed on the computer. See below.

`ThermoRawFileParser` requires Mono.

## Installation

### Singularity
You will need Singularity installed on your computer to use most of the functionality of proteotools: 
https://sylabs.io/singularity. Apologies to Docker users. Perhaps one day I will create a Docker recipe for the TPP, 
and then everyone can be happy.

### proteotools
I haven't put anything up on PyPI yet, so to install `proteotools` you will need to do the following:
```commandline
cd /path/to/proteotools/repository/after/you/download/it/
pip install .
```

The first time you run `proteotools` you will need to have it install the available search engines and download the
TPP image from the Singularity library. From a running Python interpreter, do this:
```python
from proteotools.software import download_all

download_all()
```

This will download Comet, MS-GF+, X! Tandem, and the TPP Singularity image and install them in 
`~/.proteotools_software`. Note that the installation process isn't very considerate, and will happily overwrite any 
conflicting files in `~/.proteotools_software`, if that directory already exists for some weird reason. If you have 
already run `download_all()` and you run it again, it is going to go through the whole process again. But it doesn't 
take that long unless your internet connection is visiting from 1998.

## Usage
Now that things are ready to go, you can...

### search!
It is assumed that you have some understanding of the search engines and can set up the appropriate parameters files 
by yourself.
```python
import proteotools.search as search
from pathlib import Path

fasta = '/path/to/my/favorite/fasta_file.fasta'
mzml_files = list(Path('/path/to/a/directory/with/ms_files').glob('*.mzML'))

comet_params = '/path/to/an/appropriate/comet.params'
search.comet(parameter_file=comet_params,
             fasta=fasta,
             *mzml_files)

tandem_params = '/path/to/an/appropriate/x_tandem_input_parameter.xml'
# no taxonomy.xml required! (thanks to pyteomics.pepxmltk)
search.tandem(parameter_file=tandem_params,
              fasta=fasta,
              *mzml_files)

msgf_params = '/path/to/an/appropriate/MSGFPlus_parameters.txt'
search.msgfplus(parameter_file=msgf_params,
                fasta=fasta,
                *mzml_files,
                decoy_prefix='rev_',  # Should be changed to whatever you use
                convert_to_pepxml=True,  # Default is True. Of course, we should all be using mzid files instead.
                )
```

### validate!
`tpp.run_prophets` runs InteractParser to fix common pepXML problems, PeptideProphetParser and InterProphetParser. 
There are a few parameters hardcoded in there, so if you want more control see the next section.
```python
import proteotools.tpp as tpp

pepxml_files = list(Path('/path/to/the/folder/with/the/search_results').glob('*.pepXML'))

tpp.run_prophets(pepxml_files=pepxml_files,
                 fasta=fasta,
                 decoy_tag='rev_',
                 enzyme='trypsin',  # needed by InteractParser to correct enzyme names in pepXML files
                 peptide_prophet_flags=('ZERO', 'NONPARAM', 'DECOYPROBS'),  # extra flags for PeptideProphet. see below for more details.
                 iprophet_flags=None,  # same idea as peptide_prophet_flags
                 iprophet_out_filename='interact-iproph.pepXML',  # the final file
                 threads=16,  # How many threads iProphet gets to use
                 iprophet_minprob=0,  # minimum output probability for iProphet
                 mzml_directory='/path/to/a/directory/with/the/searched/ms_files',  # where the original mzML files are located
                 skip_existing_interact_pepxmls=True,  # skips any files that starts with "interact-", because you are probably trying out different parameters and left the output files from a previous run hanging around. I'm not aware that recursive PSM validation is a helpful thing.
                 max_peptide_rank=1  # the max peptide rank to leave in there, if the search engine report, e.g. the top 5 hits
                 )
```

### run any TPP binary!
This is a simple example of running `Tandem2XML`. But you should be able to run any of the compiled TPP binaries.
```python
tpp.run_tool(tool='Tandem2XML',  # because as much as we should be using mzid files instead of pepXML, i would say pepXML are preferable to tandem XML files.
             command='/path/to/my/results/search_results.t.xml /path/to/my/results/desired_pepXML_search_results.pepXML',
             path_to_bind='/path/to/my/results'  # this is important. it tells Singularity that it has permission to access this directory.
             )
```

### get help on any TPP binary!
A convenience function to get the help output for a particular TPP tool.
```python
tpp.tool_help(tool='Tandem2XML')
```
The above will output:
```commandline
Usage: /usr/local/tpp/bin/Tandem2XML [USEDESC] [SCANOFFSETxx] <input-file> [<output-file>] 
OPTIONS:
	DESCOFF:	Don't Use Spectrum Descriptions for Naming Spectra in PepXML, (Default: parse scan number from the description)
	INDEXOFFxx:	TPP assumes scans start at 1; older X!Tandem resultshad scan index starts at 0, add xx when converting to pepXML (Default: 0)
```

## License information

Proteotools is released under the MIT license. Be sure you are aware of the licenses used by the other software tools of
which Proteotools makes use (ThermoRawFileParser, Comet, MS-GF+, X! Tandem, Trans-Proteomic Pipeline).

## Citing Proteotools
If you find Proteotools useful for your research, please find relevant information for citing it in the CITATION.cff 
file in this repository or below:
```text
# This CITATION.cff file was generated with cffinit.
# Visit https://bit.ly/cffinit to generate yours today!

cff-version: 1.2.0
title: Proteotools
message: >-
  If you use this software, please cite it using the
  metadata from this file.
type: software
authors:
  - given-names: Kevin
    family-names: Kovalchik
    email: kevin.kovalchik@gmail.com
    affiliation: 'CHU Sainte-Justine, Université de Montréal'
    orcid: 'https://orcid.org/0000-0002-2541-7721'
```