import pandas as pd
import pyterrier as pt
import pyterrier_alpha as pta
from deprecated import deprecated

import pyterrier_anserini


@deprecated(version='0.0.1', reason='Use AnseriniRetriever or AnseriniReRanker insead')
@pt.java.required
class AnseriniBatchRetrieve(pt.Transformer):
    """A backwards-compatible interface for Anserini retrieval and scoring."""

    def __init__(self, index_location: str, k: int = 1000, similarity: str = "BM25", verbose: bool = False):
        """Construct an AnseriniBatchRetrieve retrieve from pyserini.search.lucene.LuceneSearcher.

        Args:
            index_location: The location of the Anserini index.
            k: number of results to return. Default is 1000.
            similarity: Similarity model supported by Anserini. There are three options:
             * `"BM25"` - the BM25 similarity function
             * `"QLD"`  - Dirichlet language modelling
             *  `"TFIDF"` - Lucene's `ClassicSimilarity <https://lucene.apache.org/core/8_1_0/core/org/apache/lucene/search/similarities/ClassicSimilarity.html>`_.
            verbose: If True, print verbose output. Default is False.
            kwargs: ignored (for backwards compatibility)
        """
        self.index_location = index_location
        self.k = k
        self.similarity = similarity
        self.verbose = verbose

    __repr__ = pta.transformer_repr

    def transform(self, inp: pd.DataFrame) -> pd.DataFrame:
        """Retrieves or scores the values in `inp`.

        When `inp` is a query frame, retrieves documents from the index for each query in `inp`.

        When `inp` is a result set, scores the documents in the result set.
        """
        with pta.validate.any(inp) as v:
            v.query_frame(['query'], mode='retrieve')
            v.result_frame(['query'], mode='rerank')

        if v.mode == 'rerank':
            transformer = pyterrier_anserini.AnseriniReRanker(
                self.index_location,
                similarity=self.similarity,
                verbose=self.verbose)

        elif v.mode == 'retrieve':
            transformer = pyterrier_anserini.AnseriniRetriever(
                self.index_location,
                similarity=self.similarity,
                num_results=self.k,
                verbose=self.verbose)

        return transformer(inp)
