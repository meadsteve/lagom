import re, textwrap
from sybil import Region, Sybil

FENCE_START = re.compile(r'```python')
FENCE_END = re.compile(r'```')


def parse_bash_blocks(document):
    for start_match, end_match, source in document.find_region_sources(
            FENCE_START, FENCE_END
    ):
        yield Region(start_match.start(), end_match.end(), source, evaluate_code_block)


def evaluate_code_block(example):
    code = compile(example.parsed, example.document.path, 'exec', dont_inherit=True)
    exec(code, example.namespace)
    # exec adds __builtins__, we don't want it:
    del example.namespace['__builtins__']


pytest_collect_file = Sybil(
    parsers=[parse_bash_blocks],
    pattern='cookbook.md', ).pytest()
