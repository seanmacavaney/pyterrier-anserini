from typing import Any
from enum import Enum
from pyterrier_anserini import J

class AnseriniWeightModel(Enum):
    bm25 = 'BM25'
    qld = 'QLD'
    tfidf = 'TFIDF'

    def to_java_sim(self, **kwargs: Any):
        if self == AnseriniWeightModel.bm25:
            return J.BM25Similarity(kwargs.get('bm25.k1', 0.9), kwargs.get('bm25.b', 0.4))
        elif self == AnseriniWeightModel.qld:
            return J.LMDirichletSimilarity(kwargs.get('bm25.mu', 1000.0))
        elif self == AnseriniWeightModel.tfidf:
            return J.ClassicSimilarity()
        raise ValueError("wmodel %s not support in AnseriniRetriever" % wmodel) 
