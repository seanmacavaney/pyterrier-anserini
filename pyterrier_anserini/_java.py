import importlib.metadata
import os
from glob import glob
from pathlib import Path
from typing import Optional, Tuple
from warnings import warn

import pyterrier as pt
from packaging.version import Version

configure = pt.java.register_config('pyterrier.anserini', {
    'version': None,
})
_version = None


class AnseriniJavaInit(pt.java.JavaInitializer):
    def __init__(self):
        self._message = None

    def condition(self) -> bool:
        """Disables loading with anserini >= 0.36 since it introduces incompatible dependencies."""
        try:
            importlib.metadata.version('pyserini')
        except Exception as ex:
            warn(f'error loading anserini java: {ex}')
            return False
        return True

    def pre_init(self, jnius_config): # noqa: ANN001
        global _version
        if configure['version'] is None:
            jar, version = _get_pyserini_jar()
            self._message = f"version={version} (from pyserini package)"
            _version = version
        else:
            # download and use the anserini version specified by the user
            jar = pt.java.mavenresolver.get_package_jar(
                'io.anserini', "anserini", configure['version'], artifact='fatjar')
            self._message = f"version={configure['version']} (local cache)"
            _version = configure['version']

        if jar is None:
            raise RuntimeError('Could not find anserini jar')
        else:
            jnius_config.add_classpath(jar)

    def post_init(self, jnius): # noqa: ANN001
        # Temporarily disable the configure_classpath during pyserini init, otherwise it will try to reconfigure jnius
        import pyserini.setup
        _configure_classpath = pyserini.setup.configure_classpath
        try:
            pyserini.setup.configure_classpath = pt.utils.noop
            import pyserini.search.lucene  # load the package
        finally:
            pyserini.setup.configure_classpath = _configure_classpath

    def message(self):
        return self._message


def _get_pyserini_jar() -> Optional[Tuple[str, str]]:
    # find the anserini jar distributed with pyserini
    # Adapted from pyserini/setup.py and pyserini/pyclass.py
    import pyserini.setup
    jar_root = os.path.join(os.path.split(pyserini.setup.__file__)[0], 'resources/jars/')
    paths = glob(os.path.join(jar_root, 'anserini-*-fatjar.jar'))
    if not paths:
        return None, None
    latest_jar = max(paths, key=os.path.getctime)
    version = Path(latest_jar).name.split('-')[-2]
    return latest_jar, version


@pt.java.before_init
def set_version(version: Optional[str] = None):
    """Set the version of Anserini to use.

    If version is ``None`` (default), the version of Anserini distributed with the pyserini package is used. Otherwise,
    the specified version is downloaded from Maven and used insead.

    Note that this function must be run before Java is initialized.
    """
    configure['version'] = version


@pt.java.required
def check_version(min_version: str) -> bool:
    return Version(min_version) <= Version(_version)


J = pt.java.JavaClasses(
    ClassicSimilarity = 'org.apache.lucene.search.similarities.ClassicSimilarity',
    BM25Similarity = 'org.apache.lucene.search.similarities.BM25Similarity',
    LMDirichletSimilarity = 'org.apache.lucene.search.similarities.LMDirichletSimilarity',
    IndexReaderUtils = 'io.anserini.index.IndexReaderUtils',
    QueryParser = 'org.apache.lucene.queryparser.classic.QueryParser',
    ImpactSimilarity = 'io.anserini.search.similarity.ImpactSimilarity',
)
