import tempfile

import pytest
import pandas as pd
from scripts.get_samples import get_samples, check_samples

@pytest.fixture
def sample_file_csv():
    return 'tests/data/config/samples.csv'

@pytest.fixture
def invalid_samples():

    line = {'sample': 'np-aav2', 'read_file': 'tests/data/reads/np-aav2.fastq', 'reference_name': 'AAV2', 'reference_file': 'tests/data/references/AAV2.fa', 'seq_tech': 'np', 'minimap2_args': ''}

    missing_required = []
    for col in 'sample', 'read_file', 'reference_name', 'reference_file':
        tmp = dict(line)
        del tmp[col]
        missing_required.append(pd.DataFrame(tmp, index=[0]))

    # repeated sample/reference name combination
    repeated = pd.DataFrame([line, line], index=[0, 1])

    # same reference for with different name
    line2 = line.copy()
    line2['reference_name'] = 'AAV2_2'
    repeated2 = pd.DataFrame([line, line2], index=[0, 1])

    # different reference with the same name
    line2 = line.copy()
    line2['reference_file'] = 'tests/data/references/AAV2_2.fa'
    repeated3 = pd.DataFrame([line, line2], index=[0, 1])

    # non-existent read file
    line2 = line.copy()
    line2['read_file'] = 'non-existent.fastq'
    non_existent_read = pd.DataFrame([line2], index=[0])

    # non-existent reference file
    line2 = line.copy()
    line2['reference_file'] = 'non-existent.fa'
    non_existent_reference = pd.DataFrame([line2], index=[0])

    # wrong value for seq_tech
    line2 = line.copy()
    line2['seq_tech'] = 'foo'
    wrong_seq_tech = pd.DataFrame([line2], index=[0])
        
    # assemble into a list of tuples
    errors = [
        (repeated, "Each combination of sample name (column 'sample') and reference name (column 'reference_name') must be unique"),
        (repeated2, "Each reference name (column 'reference_name') must always correspond to the same reference file (column 'reference_file')"),
        (repeated3, "Each reference name (column 'reference_name') must always correspond to the same reference file (column 'reference_file')"),
        (non_existent_read, "Read file non-existent.fastq does not exist"),
        (non_existent_reference, "Reference file non-existent.fa does not exist"),
        (wrong_seq_tech, "Sequencing technology (column 'seq_tech') must be one of 'np', 'pb-hifi' or 'pb'"),

    ]
    for df in missing_required:
        errors.append((df, f'Not all required columns are present in the samples file. Required columns are: {("sample", "read_file", "reference_name", "reference_file")}'))
    
    return errors

def example_file_tests(df):
    assert len(df) == 1
    assert df['sample'][0] == 'np-aav2'
    assert df['read_file'][0] == 'tests/data/reads/np-aav2.fastq'
    assert df['reference_name'][0] == 'AAV2'
    assert df['reference_file'][0] == 'tests/data/references/AAV2.fa'
    assert df['seq_tech'][0] == 'np'
    assert df['minimap2_args'][0] == ''

class TestGetSamples:

    def test_get_samples_no_file(self):
        config = {}
        with pytest.raises(ValueError) as e:
            get_samples(config)
        assert str(e.value) == "Please specify a samples file using '--config samples=<path to samples file>'"

    def test_get_samples_invalid_extension(self):
        config = {'samples': 'tests/file.foo'}
        with pytest.raises(ValueError) as e:
            get_samples(config)
        assert str(e.value) == 'Samples file must be a .tsv or .csv file (with the extension .tsv, .csv, or .txt)'

    def test_get_samples_csv(self):

        config = {'samples': 'tests/data/config/samples.csv'}
        samples = get_samples(config)
        assert isinstance(samples, pd.DataFrame)
        example_file_tests(samples)

    @pytest.mark.parametrize('ext', ['.txt', '.tsv'])
    def test_get_samples_tsv(self, sample_file_csv, ext):

        with tempfile.NamedTemporaryFile(suffix=ext) as temp:
            samples = pd.read_csv(sample_file_csv).to_csv(temp.name, sep='\t', index=False)
            
            config = {'samples': temp.name}
            samples = get_samples(config)
            assert isinstance(samples, pd.DataFrame)
            example_file_tests(samples)
            

class TestCheckSamples:

    def test_check_samples(self, sample_file_csv):
        samples = pd.read_csv(sample_file_csv)
        samples = check_samples(samples)
        example_file_tests(samples)


    def test_check_samples_invalid(self, invalid_samples):
        for df, error in invalid_samples:
            with pytest.raises(ValueError) as e:
                check_samples(df)
            assert str(e.value) == error

    def test_check_samples_default_seq_tech(self, sample_file_csv):
        samples = pd.read_csv(sample_file_csv)
        del samples['seq_tech']
        samples = check_samples(samples)
        assert samples['seq_tech'][0] == 'np'
    
    def test_check_samples_default_minimap2_args(self, sample_file_csv):
        samples = pd.read_csv(sample_file_csv)
        del samples['minimap2_args']
        samples = check_samples(samples)
        assert samples['minimap2_args'][0] == ''