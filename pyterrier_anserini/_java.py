import os
from glob import glob
from pathlib import Path
from typing import Optional, Tuple

import pyterrier as pt

configure = pt.java.register_config('pyterrier.anserini', {
    'version': None,
})


class AnseriniJavaInit(pt.java.JavaInitializer):
    def __init__(self):
        self._message = None

    def priority(self) -> int:
        return -10 # needs to be between pt.java.core (-100) and pt.terrier (0) to avoid issues with logger configs

    def pre_init(self, jnius_config): # noqa: ANN001
        if configure['version'] is None:
            jar, version = _get_pyserini_jar()
            self._message = f"version={version} (from pyserini package)"
        else:
            # download and use the anserini version specified by the user
            jar = pt.java.mavenresolver.get_package_jar(
                'io.anserini', "anserini", configure['version'], artifact='fatjar')
            self._message = f"version={configure['version']} (local cache)"

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
def set_version(version: str):
    configure['version'] = version


J = pt.java.JavaClasses(
    ClassicSimilarity = 'org.apache.lucene.search.similarities.ClassicSimilarity',
    BM25Similarity = 'org.apache.lucene.search.similarities.BM25Similarity',
    LMDirichletSimilarity = 'org.apache.lucene.search.similarities.LMDirichletSimilarity',
    IndexReaderUtils = 'io.anserini.index.IndexReaderUtils',
    QueryParser = 'org.apache.lucene.queryparser.classic.QueryParser',
    ImpactSimilarity = 'io.anserini.search.similarity.ImpactSimilarity',
)
