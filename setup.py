from setuptools import setup, find_packages

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
    description="Anserini integration for PyTerrier",
    long_description=open('README.md', 'r').read(),
    long_description_content_type="text/markdown",
    url='https://github.com/terrierteam/pyterrier-anserini',
    packages=find_packages(),
    entry_points={
        'pyterrier.java.init': [
            'pyterrier_anserini.java = pyterrier_anserini.java:AnseriniJavaInit',
        ],
        'pyterrier.modules': [
            'anserini = pyterrier_anserini',
        ],
    },
    install_requires=list(open('requirements.txt', 'rt')),
    python_requires='>=3.8',
)
