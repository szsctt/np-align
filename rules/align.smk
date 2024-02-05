
def get_sample_info(wildcards, column_name):
    
    # get index of row where sample name is equal to wildcards.sample and reference is equal to wildcards.reference
    idx = samples[(samples['sample'] == wildcards.sample) & (samples['reference_name'] == wildcards.reference)].index
    assert len(idx) == 1
    idx = idx[0]

    return samples.loc[idx, column_name]

def get_params(wildcards):
    
    tech_args = {'np': '-x map-ont', 'pb': '-x map-pb', 'pb-hifi': '-x map-hifi'}
    seq_tech = get_sample_info(wildcards, 'seq_tech')
    minimap_extras = get_sample_info(wildcards, 'minimap2_args')

    # output in sam format
    if '-a' not in minimap_extras:
        minimap_extras += ' -a'

    return {
        'tech': tech_args[seq_tech],
        'extra': minimap_extras
    }

rule align_minimap2:
    input:
        reads = lambda wildcards: get_sample_info(wildcards, 'read_file'),
        reference = lambda wildcards: get_sample_info(wildcards, 'reference_file')
    output:
        aln = temp("out/align/{sample}.{reference}.unsorted.sam")
    params:
        extra = lambda wildcards: get_params(wildcards)['extra'],
        tech = lambda wildcards: get_params(wildcards)['tech'],
        threads = lambda wildcards, threads: f"-T {threads}"
    log: "out/logs/align_minimap2/{sample}.{reference}.log"
    container: "docker://quay.io/biocontainers/minimap2:2.26--he4a0461_2"
    conda: "../envs/map.yml"
    threads: 8
    shell:
        "minimap2 {params} {input.reference} {input.reads} > {output.aln}"

rule sort_sam:
    input:
        sam = rules.align_minimap2.output.aln
    output:
        bam = "out/align/{sample}.{reference}.bam"
    log: "out/logs/sort_sam/{sample}.{reference}.log"
    container: "docker://quay.io/biocontainers/samtools:1.19.2--h50ea8bc_0"
    conda: "../envs/map.yml"
    shell:
        "samtools sort -o {output.bam} {input.sam}"

rule index_bam:
    input:
        bam = rules.sort_sam.output.bam
    output:
        bai = "out/align/{sample}.{reference}.bam.bai"
    log: "out/logs/index_bam/{sample}.{reference}.log"
    container: "docker://quay.io/biocontainers/samtools:1.19.2--h50ea8bc_0"
    conda: "../envs/map.yml"
    shell:
        "samtools index {input.bam}"
