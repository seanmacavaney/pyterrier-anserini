from typing import Union, Dict
from warnings import warn
import pandas as pd
import numpy as np
from deprecated import deprecated
import pyterrier as pt
import pyterrier_alpha as pta
import pyterrier_anserini
from pyterrier_anserini._wmodel import AnseriniWeightModel

@pt.java.required
class AnseriniRetriever(pt.Transformer):
    """
        Allows retrieval from an Anserini index.
    """
    def __init__(self,
        index_location: str,
        wmodel: Union[AnseriniWeightModel, str] = "BM25",
        num_results: int = 1000,
        verbose: bool = False,
        wmodel_args: Dict[str, any] = None,
    ):
        """
            Construct an AnseriniRetriever retrieve from pyserini.search.lucene.LuceneSearcher. 

            Args:
                index_location(str): The location of the Anserini index.
                wmodel(str): Weighting models supported by Anserini. There are three options: 
                num_results(int): number of results to return. Default is 1000.
                verbose(bool): show a progress bar during retrieval?
                wmodel_args(dict): model-specific arguments, like bm25.k1.
        """
        self.index_location = index_location
        self.num_results = num_results
        self.wmodel = wmodel
        self.verbose = verbose
        from pyserini.search.lucene import LuceneSearcher
        self.searcher = LuceneSearcher(index_location)
        self.wmodel_args = wmodel_args or {}

    def __reduce__(self):
        return (
            self.__class__,
            (self.index_location, self.wmodel, self.num_results, self.verbose, self.wmodel_args),
            self.__getstate__()
        )

    def __getstate__(self): 
        return  {}

    def __setstate__(self, d): 
        pass

    def __str__(self):
        return "AnseriniRetriever()"

    def __repr__(self):
        return f"AnseriniRetriever({self.wmodel!r}, {self.k!r})"
    
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

        if v.mode == 'rerank':
            indexreaderutils = pyterrier_anserini.J.IndexReaderUtils
            indexreader = self.searcher.object.reader
            def _score(query, docno):
                return indexreaderutils.computeQueryDocumentScoreWithSimilarity(indexreader, docno, query, sim)
            it = zip(inp['query'], inp['docno'])
            if self.verbose:
                it = pt.tqdm(it, desc=str(self), total=len(inp), unit='d')
            result = inp.assign(score=[_score(query, docno) for query, docno in it])
            result = pt.model.add_ranks(result)
            return result

        if v.mode == 'retrieve':
            self.searcher.object.similarty = sim
            result = pta.DataFrameBuilder(['_index', 'docno', 'score', 'rank'])
            it = enumerate(inp['query'])
            if self.verbose:
                it = pt.tqdm(it, desc=str(self), total=len(inp), unit='d')
            for i, query in it:
                hits = self.searcher.search(query, k=self.num_results)
                result.extend({
                    '_index': i,
                    'docno': [h.docid for h in hits],
                    'score': [h.score for h in hits],
                    'rank': np.arange(len(hits)),
                })
            return result.to_df(merge_on_index=inp)


@deprecated(version='0.0.1', reason='Use AnseriniRetriever insead')
class AnseriniBatchRetrieve(AnseriniRetriever):
    pass
