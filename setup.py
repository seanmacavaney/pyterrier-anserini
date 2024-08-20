from setuptools import find_packages, setup


def get_version(rel_path):
    for line in open(rel_path):
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")

setup(
    name='pyterrier-anserini',
    version=get_version('pyterrier_anserini/__init__.py'),
    author='Sean MacAvaney',
    author_email='sean.macavaney@glasgow.ac.uk',
    description="Anserini + PyTerrier",
    long_description=open('README.md', 'r').read(),
    long_description_content_type="text/markdown",
    url='https://github.com/terrierteam/pyterrier-anserini',
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'pyterrier.java.init': [
            'pyterrier_anserini.java = pyterrier_anserini._java:AnseriniJavaInit',
        ],
        'pyterrier.modules': [
            'anserini = pyterrier_anserini',
        ],
        'pyterrier.artifact': [
            'sparse_index.anserini = pyterrier_anserini:AnseriniIndex',
        ],
        'pyterrier.artifact.url_protocol_resolver': [
            'anserini = pyterrier_anserini._util:_anserini_url_resolver',
        ],
        'pyterrier.artifact.metadata_adapter': [
            'sparse_index.anserini = pyterrier_anserini._util:_anserini_metadata_adapter',
        ],
    },
    install_requires=list(open('requirements.txt', 'rt')),
    python_requires='>=3.10',
)
