from typing import List, Union

import pandas as pd
import pyterrier as pt
import pyterrier_alpha as pta

import pyterrier_anserini
from pyterrier_anserini import AnseriniIndex


@pt.java.required
class AnseriniTextLoader(pt.Transformer):
    """A transformer that provides access to text fields from an Anserini index."""
    def __init__(self,
                 index: Union[AnseriniIndex, str],
                 fields: List[str],
                 *,
                 verbose: bool = False):
        """Initializes the text loader.

        Args:
            index: The index to provide text from. If a string, an AnseriniIndex object is created for the path.
            fields: The fields to load.
            verbose: Whether to display a progress bar when providing text.
        """
        self.index = index if isinstance(index, AnseriniIndex) else AnseriniIndex(index)
        self.fields = fields
        self.verbose = verbose

    __repr__ = pta.transformer_repr

    def transform(self, inp: pd.DataFrame) -> pd.DataFrame:
        """Provides text from the index for each document in `inp`.

        Args:
            inp: A DataFrame with a 'docno' column containing document IDs.
        """
        pta.validate.columns(inp, includes=['docno'])

        utils = pyterrier_anserini.J.IndexReaderUtils
        index_reader = self.index._searcher().object.reader

        results = pta.DataFrameBuilder(['_index'] + self.fields)

        it = enumerate(inp['docno'])
        if self.verbose:
            it = pt.tqdm(it, unit='d', total=len(inp), desc='AnseriniTextLoader')

        for i, docno in it:
            doc = utils.document(index_reader, docno)
            res = {f: doc.get(f) for f in self.fields}
            res['_index'] = i
            results.extend(res)

        return results.to_df(merge_on_index=inp)
