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


if not bool(int(os.getenv('LAGOM_SKIP_COMPILE', '0'))):
    from mypyc.build import mypycify
    setup(
        version=load_version("lagom/version.py"),
        ext_modules=mypycify([
            'lagom/container.py',
            'lagom/context_based.py',
            'lagom/definitions.py',
            'lagom/updaters.py',
        ])
    )
else:
    setup(
        version=load_version("lagom/version.py")
    )

