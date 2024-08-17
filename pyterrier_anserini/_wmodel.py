from typing import Any
from enum import Enum
from pyterrier_anserini import J

DEFAULT_WMODEL_ARGS = {
    'bm25.k1': 0.9,
    'bm25.b': 0.4,
    'qld.mu': 1000.,
}

class AnseriniWeightModel(Enum):
    bm25 = 'BM25'
    qld = 'QLD'
    tfidf = 'TFIDF'
    impact = 'Impact'

    def to_java_sim(self, **kwargs: Any):
        args = {}
        args.update(DEFAULT_WMODEL_ARGS)
        args.update(kwargs)
        if self == AnseriniWeightModel.bm25:
            return J.BM25Similarity(args['bm25.k1'], args['bm25.b'])
        elif self == AnseriniWeightModel.qld:
            return J.LMDirichletSimilarity(args['qld.mu'])
        elif self == AnseriniWeightModel.tfidf:
            return J.ClassicSimilarity()
        if self == AnseriniWeightModel.impact:
            return J.ImpactSimilarity()
        raise ValueError(f"wmodel {wmodel} is not supported") 

    def __repr__(self):
        return repr(self.value)
