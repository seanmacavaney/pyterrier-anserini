from enum import Enum
from typing import Any

from pyterrier_anserini import J

DEFAULT_WMODEL_ARGS = {
    'bm25.k1': 0.9,
    'bm25.b': 0.4,
    'qld.mu': 1000.,
}

class AnseriniSimilarity(Enum):
    bm25 = 'BM25'
    qld = 'QLD'
    tfidf = 'TFIDF'
    impact = 'Impact'

    def to_java_sim(self, **kwargs: Any):
        args = {}
        args.update(DEFAULT_WMODEL_ARGS)
        args.update(kwargs)
        if self == AnseriniSimilarity.bm25:
            return J.BM25Similarity(args['bm25.k1'], args['bm25.b'])
        elif self == AnseriniSimilarity.qld:
            return J.LMDirichletSimilarity(args['qld.mu'])
        elif self == AnseriniSimilarity.tfidf:
            return J.ClassicSimilarity()
        if self == AnseriniSimilarity.impact:
            return J.ImpactSimilarity()
        raise ValueError(f"similarity {self} is not supported")

    def __repr__(self):
        return repr(self.value)
