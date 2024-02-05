import os
import pandas as pd

DEFAULT_SEQ_TECH = 'np'
DEFAULT_MINIMAP2_ARGS = ''

def check_samples(samples):
    """
    Check all required columns are present, and that the sample names are unique
    """

    required_columns = ('sample', 'read_file', 'reference_name', 'reference_file')
    if not all([col in samples.columns for col in required_columns]):
        raise ValueError(f'Not all required columns are present in the samples file. Required columns are: {required_columns}')
    
    
    # check read files exist
    for read_file in samples['read_file']:
        if not os.path.exists(read_file):
            raise ValueError(f'Read file {read_file} does not exist')
        
    #check that the same reference name always corresponds to the same parent file
    if len(samples.groupby(['reference_name', 'reference_file'])) != len(samples.groupby('reference_name')):
        raise ValueError("Each reference name (column 'reference_name') must always correspond to the same reference file (column 'reference_file')")
    if len(samples.groupby(['reference_name', 'reference_file'])) != len(samples.groupby('reference_file')):
        raise ValueError("Each reference name (column 'reference_name') must always correspond to the same reference file (column 'reference_file')")
    # check reference files exist
    for reference_file in samples['reference_file']:
        if not os.path.exists(reference_file):
            raise ValueError(f'Reference file {reference_file} does not exist')
        
    # check that combinations of sample names and reference names are unique
    if len(samples.groupby(['sample', 'reference_name'])) != len(samples):
        raise ValueError("Each combination of sample name (column 'sample') and reference name (column 'reference_name') must be unique")
        
    # optional columns
    # check that sequencing technology is either 'np',  'pb', or 'pb-hifi'
    if 'seq_tech' in samples.columns:
        if not set(samples['seq_tech']).issubset(set(['np',  'pb', 'pb-hifi'])):
            raise ValueError("Sequencing technology (column 'seq_tech') must be one of 'np', 'pb-hifi' or 'pb'")
    else:
        # assume nanopore data
        samples['seq_tech'] = DEFAULT_SEQ_TECH
        
    # other minimap2 args
    if 'minimap2_args' in samples.columns:
        samples['minimap2_args'] = samples['minimap2_args'].fillna(DEFAULT_MINIMAP2_ARGS)
    else:
        samples['minimap2_args'] = DEFAULT_MINIMAP2_ARGS

    return samples



def get_samples(config):

    if 'samples' not in config:
        raise ValueError("Please specify a samples file using '--config samples=<path to samples file>'")
    
    # check file extension to determine separator
    ext = os.path.splitext(config['samples'])[1]
    if ext not in {'.tsv', '.csv', '.txt'}:
        raise ValueError('Samples file must be a .tsv or .csv file (with the extension .tsv, .csv, or .txt)')
    if ext in {'.tsv', '.txt'}:
        sep = '\t'
    else:
        sep = ','

    # read samples file
    samples = pd.read_csv(config['samples'], sep=sep)

    samples = check_samples(samples)

    return samples