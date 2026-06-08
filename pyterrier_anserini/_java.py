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
    
    def priority(self) -> int:
        return -105 # run this initializer before ColabJavaInit

    def pre_init(self, jnius_config): # noqa: ANN001
        global _version
        if configure['version'] is None:
            jar, version = _get_pyserini_jar()
            self._version = version
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
        
        # force Google Colab to update Java to at least version 21, which is required by the pyserini
        import pyterrier.java
        try:
            pyterrier.java.set_min_java_version(21)
        except Exception as ex:
            # this requires PyTerrier 1.1 or newer

        jnius_config.classpath = [jar] + jnius_config.classpath
        # see https://github.com/castorini/pyserini/blob/pyserini-2.2.0/pyserini/_jvm.py#L44-L46
        jnius_config.add_options('--add-modules=jdk.incubator.vector')
        # Suppress "WARNING: A restricted method in java.lang.foreign.Linker has been called"
        jnius_config.add_options('--enable-native-access=ALL-UNNAMED')

    def post_init(self, jnius): # noqa: ANN001
        if Version(self._version) < Version('2.1.0'):        
            # Temporarily disable the configure_classpath during pyserini init, otherwise it will try to reconfigure jnius
            import pyserini.setup
            _configure_classpath = pyserini.setup.configure_classpath
            try:
                pyserini.setup.configure_classpath = pt.utils.noop
                import pyserini.search.lucene  # load the package
            finally:
                pyserini.setup.configure_classpath = _configure_classpath
        else:
            # Temporarily disable the configure_classpath during pyserini init, otherwise it will try to reconfigure jnius
            import pyserini._jvm
            _configure_classpath = pyserini._jvm.configure_classpath
            try:
                pyserini._jvm.configure_classpath = pt.utils.noop
                import pyserini.search.lucene  # load the package
            finally:
                pyserini._jvm.configure_classpath = _configure_classpath

    def message(self):
        return self._message


def _get_pyserini_jar() -> Optional[Tuple[str, str]]:
    # find the anserini jar distributed with pyserini
    # Adapted from pyserini/setup.py and pyserini/pyclass.py
    import pyserini
    jar_root = os.path.join(os.path.split(pyserini.__file__)[0], 'resources/jars/')
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
    StandardAnalyzer = 'org.apache.lucene.analysis.standard.StandardAnalyzer',
    BooleanQueryBuilder = 'org.apache.lucene.search.BooleanQuery$Builder',
    PhraseQueryBuilder = 'org.apache.lucene.search.PhraseQuery$Builder',
    Occur = 'org.apache.lucene.search.BooleanClause$Occur',
    TermQuery = 'org.apache.lucene.search.TermQuery',
    BoostQuery = 'org.apache.lucene.search.BoostQuery',
    Term = 'org.apache.lucene.index.Term',
    CharTermAttribute = 'org.apache.lucene.analysis.tokenattributes.CharTermAttribute',
)
