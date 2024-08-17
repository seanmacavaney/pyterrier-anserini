from typing import Union, Dict, Any
from warnings import warn
import pandas as pd
import numpy as np
from deprecated import deprecated
import pyterrier as pt
import pyterrier_alpha as pta
import pyterrier_anserini
from pyterrier_anserini import J
from pyterrier_anserini._index import AnseriniIndex
from pyterrier_anserini._wmodel import AnseriniWeightModel


def _noop_query_parser(query):
    return query


def _toks_query_parser_factory(parser):
    def wrapped(toks: Dict[str, float]) -> Any:
        res = []
        for tok, weight in toks.items():
            res.append(f'{parser.escape(tok)}^{weight:f}')
        query = ' '.join(res)
        return parser.parse(query)
    return wrapped


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
            pandas.DataFrame with columns=['qid', 'query', 'docno', 'rank', 'score']
        """
        with pta.validate.any(inp) as v:
            v.query_frame(extra_columns=['query_lucene'], mode='query_lucene')
            v.query_frame(extra_columns=['query_toks'], mode='query_toks')
            v.query_frame(extra_columns=['query'], mode='query_text')

        sim = AnseriniWeightModel(self.wmodel).to_java_sim(**self.wmodel_args)
        searcher = self.index._searcher()
        searcher.object.searcher.setSimilarity(sim)

        if v.mode == 'query_lucene':
            parser = J.QueryParser("contents", searcher.object.analyzer)
            q_transform = parser.parse
            it = enumerate(inp['query_lucene'])
        elif v.mode == 'query_toks':
            parser = J.QueryParser("contents", searcher.object.analyzer)
            q_transform = _toks_query_parser_factory(parser)
            it = enumerate(inp['query_toks'])
        elif v.mode == 'query_text':
            q_transform = _noop_query_parser
            it = enumerate(inp['query'])

        if self.verbose:
            it = pt.tqdm(it, desc=str(self), total=len(inp), unit='d')

        result = pta.DataFrameBuilder(['_index', 'docno', 'score', 'rank'])
        for i, query in it:
            hits = searcher.search(q_transform(query), k=self.num_results)
            result.extend({
                '_index': i,
                'docno': [h.docid for h in hits],
                'score': [h.score for h in hits],
                'rank': np.arange(len(hits)),
            })

        return result.to_df(merge_on_index=inp)
