# np-align

A simple snakemake workflow to align long-read data using minimap2.

### Inputs

Specify data to be aligned in a tab- or comma-separated file (.tsv, .txt or .csv) with the following format:

```
sample,read_file,reference_name,reference_file,seq_tech,minimap2_args
np-aav2,tests/data/reads/np-aav2.fastq,AAV2,tests/data/references/AAV2.fa,np,
```

In this file:
 - `sample` is a name for the sample (required)
 - `read_file` is the path to the file containing the reads in fastq format (required)
 - `reference_name` is a name for the reference (required)
 - `reference_file` is the path to a fasta file containing the reference (required)
 - `seq_tech` is one of 'np', 'pb', 'pb-hifi' (optional, assume np if not specified)
 - `minimap2_args` are additional arguments passed to minimap2 (optional)

Each combination of sample and reference_name must be unique, and each reference file must always have the same name.

### Execution

Running the workflow requires snakemake and either conda/mamba or singularity to supply dependencies.

To run using mamba:
```
snakemake --config samples=<path_to_file> --use-conda
```

To run using conda:
```
snakemake --config samples=<path_to_file> --use-conda --conda-frontend conda
```

To run using singularity:
```
snakemake --config samples=<path_to_file> --use-singularity
```

