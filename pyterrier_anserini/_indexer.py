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
        threads: int = 8,
        store_doc_vectors: bool = True,
        store_positions: bool = False,
        store_contents: bool = True,
        verbose: bool = False
    ):
        """Initializes the indexer.

        Args:
            index: The index to index to. If a string, an AnseriniIndex object is created for the path.
            fields: The fields to index. If '*' (default), all fields are indexed. Otherwise, the values of the fields
                provided in this argumetn are concatenated and indexed.
            threads: The number of threads to use when indexing.
            store_doc_vectors: Whether to store document vectors. When False, functionality like PRF is disabled.
            store_positions: Whether to store term positions. When False, functionality like SDM are disabled.
            store_contents: Whether to store document contents. When False, functionality like text loading is disabled.
            verbose: Whether to display a progress bar when indexing.
        """
        self._index = index if isinstance(index, AnseriniIndex) else AnseriniIndex(index)
        self.fields = fields
        self.threads = threads
        self.store_doc_vectors = store_doc_vectors
        self.store_positions = store_positions
        self.store_contents = store_contents
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
        args = ['-index', self._index.path]
        if self.store_doc_vectors:
            args.append('-storeDocvectors')
        if self.store_positions:
            args.append('-storePositions')
        if self.store_contents:
            args.append('-storeContents')
        indexer = LuceneIndexer(self._index.path, args=args, threads=self.threads)

        # create directory and metadata file
        if not os.path.exists(os.path.join(self._index.path, 'pt_meta.json')):
            os.makedirs(self._index.path, exist_ok=True)
            with open(os.path.join(self._index.path, 'pt_meta.json'), 'wt') as fout:
                json.dump({
                    'type': 'sparse_index',
                    'format': 'anserini',
                    'package_hint': 'pyterrier-anserini',
                    'store_doc_vectors': self.store_doc_vectors,
                    'store_positions': self.store_positions,
                    'store_contents': self.store_contents,
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
