from typing import Dict, Union

import pandas as pd
import pyterrier as pt
import pyterrier_alpha as pta

from pyterrier_anserini import J
from pyterrier_anserini._index import AnseriniIndex
from pyterrier_anserini._similarity import AnseriniSimilarity


@pt.java.required
class AnseriniReRanker(pt.Transformer):
    """A transformer that scores (i.e., re-ranks) the provided documents from an Anserini index."""
    def __init__(self,
        index: Union[AnseriniIndex, str],
        similarity: Union[str, AnseriniSimilarity],
        similarity_args: Dict = None,
        *,
        verbose: bool = False
    ):
        """Initializes the scorer.

        Args:
            index: The index to score from. If a string, an AnseriniIndex object is created for the path.
            similarity: The similarity function to use for scoring.
            similarity_args: A dictionary of arguments to use for the similarity function.
            verbose: Whether to display a progress bar when scoring.
        """
        self.index = index if isinstance(index, AnseriniIndex) else AnseriniIndex(index)
        self.similarity = AnseriniSimilarity(similarity)
        self.similarity_args = similarity_args
        self.verbose = verbose

    __repr__ = pta.transformer_repr

    def transform(self, inp: pd.DataFrame) -> pd.DataFrame:
        """Scores (i.e., re-ranks) documents from the index for each query in `inp`.

        Args:
            inp: A DataFrame with a 'query' column containing queries and a 'docno' column containing document IDs.

        Returns:
            A DataFrame containing the scored documents, with any columns included in `inp`, plus
            the 'score' and 'rank' of the scored documents.
        """
        with pta.validate.any(inp) as v:
            v.result_frame(['query_lucene'], mode='query_lucene')
            v.result_frame(['query_toks'], mode='query_toks')
            v.result_frame(['query'], mode='query_text')

        sim = AnseriniSimilarity(self.similarity).to_lucene_sim(self.similarity_args)
        index_reader = self.index._searcher().object.reader

        if v.mode == 'query_lucene':
            raise NotImplementedError('query_lucene not yet supported for AnseriniReRanker')
        elif v.mode == 'query_toks':
            raise NotImplementedError('query_toks not yet supported for AnseriniReRanker')
        elif v.mode == 'query_text':
            it = zip(inp['docno'], inp['query'])

        if self.verbose:
            it = pt.tqdm(it, unit='d', total=len(inp), desc='AnseriniScorer')

        scores = [
            J.IndexReaderUtils.computeQueryDocumentScoreWithSimilarity(index_reader, docno, query, sim)
            for docno, query in it
        ]
        res = inp.assign(score=scores)

        return pt.model.add_ranks(res)

