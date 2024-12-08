import os

from setuptools import setup


def load_version(version_file_path):
    import re
    file_contents = open(version_file_path, "rt").read()
    version_regex = r"^__version__ = ['\"]([^'\"]*)['\"]"
    match = re.search(version_regex, file_contents, re.M)
    if match:
        return match.group(1)
    else:
        raise RuntimeError(f"Unable to find version string in {version_file_path}")


if os.getenv('LAGOM_SKIP_COMPILE') and os.getenv('LAGOM_COMPILE'):
    raise Exception("Both LAGOM_SKIP_COMPILE and LAGOM_COMPILE ")
elif os.getenv('LAGOM_COMPILE'):
    LAGOM_COMPILE = bool(int(os.environ['LAGOM_COMPILE']))
elif os.getenv('LAGOM_SKIP_COMPILE'):
    LAGOM_COMPILE = not bool(int(bool(int(os.environ['LAGOM_SKIP_COMPILE']))))
else:
    LAGOM_COMPILE = False

if LAGOM_COMPILE:
    from mypyc.build import mypycify
    setup(
        version=load_version("lagom/version.py"),
        ext_modules=mypycify([
            'lagom/container.py',
            'lagom/context_based.py',
            'lagom/definitions.py',
            'lagom/experimental/definitions.py',
            'lagom/updaters.py',
        ])
    )
else:
    setup(
        version=load_version("lagom/version.py")
    )

