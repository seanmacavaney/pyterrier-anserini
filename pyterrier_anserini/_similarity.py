from enum import Enum
from typing import Dict, Optional

from pyterrier_anserini import J

DEFAULT_WMODEL_ARGS = {
    'bm25.k1': 0.9,
    'bm25.b': 0.4,
    'qld.mu': 1000.,
}

class AnseriniSimilarity(Enum):
    """An enum representing the similarity functions available in Anserini."""

    bm25 = 'BM25'
    qld = 'QLD'
    tfidf = 'TFIDF'
    impact = 'Impact'

    def to_lucene_sim(self, sim_args: Optional[Dict[str, float]] = None):
        """Provides a Lucene similarity object that represents this similarity functions, including provided arguments.

        Args:
            sim_args: The arguments of this similarity function. Default values will be used when they are not provided.

        Returns:
            A ``pyjnius`` binding to a ``org.apache.lucene.search.similarities.Similarity`` object.
        """
        args = {}
        args.update(DEFAULT_WMODEL_ARGS)
        if sim_args is not None:
            args.update(sim_args)

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
