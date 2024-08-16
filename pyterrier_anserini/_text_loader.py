from typing import List, Optional, Union

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
                 fields: Optional[Union[str, List[str]]] = None,
                 *,
                 verbose: bool = False):
        """Initializes the text loader.

        Args:
            index: The index to provide text from. If a string, an AnseriniIndex object is created for the path.
            fields: The fields to provide. If None, all fields are provided. If a string, the value of the field is
                provided. If a list, the values of the fields are provided.
            verbose: Whether to display a progress bar when providing text.
        """
        self.index = index if isinstance(index, AnseriniIndex) else AnseriniIndex(index)
        self.fields = fields
        self.verbose = verbose

    def transform(self, inp: pd.DataFrame) -> pd.DataFrame:
        """Provides text from the index for each document in `inp`.

        Args:
            inp: A DataFrame with a 'docno' column containing document IDs.
        """
        pta.validate.columns(inp, includes=['docno'])

        searcher = self.index._searcher()
        utils = pyterrier_anserini.J.IndexReaderUtils
        indexreader = searcher.object.reader

        if self.fields is None:
            fields = [k for k in utils.getFieldInfo(indexreader) if k != 'id']
        elif isinstance(self.fields, str):
            fields = [fields]
        else:
            fields = self.fields

        results = pta.DataFrameBuilder(['_index'] + fields)

        it = enumerate(inp['docno'])
        if self.verbose:
            it = pt.tqdm(it, unit='d', total=len(inp), desc='AnseriniTextLoader')

        for i, docno in it:
            doc = utils.document(indexreader, docno)
            res = {f: doc.get(f) for f in fields}
            res['_index'] = [i]
            results.extend(res)

        return results.to_df(merge_on_index=inp)

    def __repr__(self):
        return f"{self.index!r}.text_loader({self.fields!r})"
