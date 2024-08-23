import json
import os
from typing import Dict, Iterable, List, Literal, Union

import pyterrier as pt
import pyterrier_alpha as pta

from pyterrier_anserini import AnseriniIndex


@pt.java.required
class AnseriniIndexer(pt.Indexer):
    """An indexer for Anserini indexes."""
    def __init__(self,
        index: Union[AnseriniIndex, str],
        *,
        fields: Union[List[str], Literal['*']] = '*',
        verbose: bool = False
    ):
        """Initializes the indexer.

        Args:
            index: The index to index to. If a string, an AnseriniIndex object is created for the path.
            fields: The fields to index. If '*' (default), all fields are indexed. Otherwise, the values of the fields
                provided in this argumetn are concatenated and indexed.
            verbose: Whether to display a progress bar when indexing.
        """
        self._index = index if isinstance(index, AnseriniIndex) else AnseriniIndex(index)
        self.fields = fields
        self.verbose = verbose

    __repr__ = pta.transformer_repr

    def index(self, inp: Iterable[Dict]) -> pta.Artifact:
        """Indexes the input documents to the index.

        Args:
            inp: An iterable of documents to index.

        Returns:
            The index that was indexed to.
        """
        assert not self._index.built()
        from pyserini.index.lucene import LuceneIndexer
        args = ['-index', self._index.path, '-storeContents', '-storeDocvectors']
        indexer = LuceneIndexer(self._index.path, args=args)
        # create directory and metadata file
        if not os.path.exists(os.path.join(self._index.path, 'pt_meta.json')):
            os.makedirs(self._index.path, exist_ok=True)
            with open(os.path.join(self._index.path, 'pt_meta.json'), 'wt') as fout:
                json.dump({
                    'type': 'sparse_index',
                    'format': 'anserini',
                    'package_hint': 'pyterrier-anserini',
                    # TODO: other stuff (like stemmer used) in due course
                }, fout)

        if self.verbose:
            inp = pt.tqdm(inp, unit='docs', desc='AnseriniIndexer')

        for doc in inp:
            indexer.add_doc_dict(self._map_doc(doc))

        # commit
        indexer.close()

        return self._index

    def _map_doc(self, doc: Dict) -> Dict:
        if self.fields == '*':
            contents = '\n'.join(v for k, v in doc.items() if k != 'docno' and isinstance(v, str))
        else:
            contents = '\n'.join(str(doc[k]) for k in self.fields)
        return {
            'id': doc['docno'],
            'contents': contents
        }
