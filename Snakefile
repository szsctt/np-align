from scripts.get_samples import get_samples

samples = get_samples(config)

wildcard_constraints:
    sample = "|".join(samples['sample']),
    reference = "|".join(samples['reference_name'])

rule all:
    input:
        expand("out/align/{sample}.{reference}.bam", zip, sample=samples['sample'], reference=samples['reference_name']),
        expand("out/align/{sample}.{reference}.bam.bai", zip, sample=samples['sample'], reference=samples['reference_name']),


include: "rules/align.smk"
