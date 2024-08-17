from typing import Union, Dict
from warnings import warn
import pandas as pd
import numpy as np
from deprecated import deprecated
import pyterrier as pt
import pyterrier_alpha as pta
import pyterrier_anserini
from pyterrier_anserini._index import AnseriniIndex
from pyterrier_anserini._wmodel import AnseriniWeightModel

@pt.java.required
class AnseriniRetriever(pt.Transformer):
    """
        Retrieves from an Anserini index.
    """
    def __init__(self,
        index: Union[AnseriniIndex, str],
        wmodel: Union[AnseriniWeightModel, str] = "BM25",
        wmodel_args: Dict[str, any] = None,
        *,
        num_results: int = 1000,
        verbose: bool = False,
    ):
        """
            Construct an AnseriniRetriever retrieve from pyserini.search.lucene.LuceneSearcher. 

            Args:
                index(str|AnseriniIndex): The Anserini index.
                wmodel(str|AnseriniWeightModel): Weighting models supported by Anserini.
                num_results(int): number of results to return. Default is 1000.
                verbose(bool): show a progress bar during retrieval?
                wmodel_args(dict): model-specific arguments, like bm25.k1.
        """
        if not isinstance(index, AnseriniIndex):
            index = AnseriniIndex(index)
        self.index = index
        self.wmodel = wmodel
        self.wmodel_args = wmodel_args or {}
        self.num_results = num_results
        self.verbose = verbose

    __repr__ = pta.transformer_repr

    def transform(self, inp: pd.DataFrame) -> pd.DataFrame:
        """
        Performs retrieval

        Args:
            A pandas.Dataframe

        Returns:
            pandas.DataFrame with columns=['qid', 'docno', 'rank', 'score']
        """
        with pta.validate.any(inp) as v:
            v.query_frame(extra_columns=['query'], mode='retrieve')
            v.result_frame(extra_columns=['query'], mode='rerank')

        sim = AnseriniWeightModel(self.wmodel).to_java_sim(**self.wmodel_args)
        searcher = self.index._searcher()

        if v.mode == 'rerank':
            indexreaderutils = pyterrier_anserini.J.IndexReaderUtils
            indexreader = searcher.object.reader
            def _score(query, docno):
                return indexreaderutils.computeQueryDocumentScoreWithSimilarity(indexreader, docno, query, sim)
            it = zip(inp['query'], inp['docno'])
            if self.verbose:
                it = pt.tqdm(it, desc=str(self), total=len(inp), unit='d')
            result = inp.assign(score=[_score(query, docno) for query, docno in it])
            result = pt.model.add_ranks(result)
            return result

        if v.mode == 'retrieve':
            searcher.object.similarty = sim
            result = pta.DataFrameBuilder(['_index', 'docno', 'score', 'rank'])
            it = enumerate(inp['query'])
            if self.verbose:
                it = pt.tqdm(it, desc=str(self), total=len(inp), unit='d')
            for i, query in it:
                hits = searcher.search(query, k=self.num_results)
                result.extend({
                    '_index': i,
                    'docno': [h.docid for h in hits],
                    'score': [h.score for h in hits],
                    'rank': np.arange(len(hits)),
                })
            return result.to_df(merge_on_index=inp)


@deprecated(version='0.0.1', reason='Use AnseriniRetriever insead')
class AnseriniBatchRetrieve(AnseriniRetriever):
    def __init__(self, index_location, k=1000, wmodel="BM25", verbose=False):
        super().__init__(index_location, wmodel, num_results=k, verbose=verbose)

    def __repr__(self):
        return f'AnseriniBatchRetrieve({self.index.path!r}, {self.num_results!r}, {str(self.wmodel)!r}, verbose={self.verbose!r})'
