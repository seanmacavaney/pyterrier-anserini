"""Provides functionality like indexing and retrieval from the Anserini toolkit.

This module provides a way to use the Anserini toolkit for operations like indexing
and retrieval in PyTerrier.

Typical usage example::

  import pyterrier as pt
  from pyterrier_anserini import AnseriniIndex
  index = AnseriniIndex('my_index.anserini')

  # index a dataset
  indexer = index.indexer()
  indexer.index(pt.get_dataset('vaswani').get_corpus_iter())

  # retrieve using BM25
  retr = index.bm25()
  retr(pt.get_dataset('vaswani').get_topics())
"""

__version__ = '0.1.4'

from pyterrier_anserini._java import J, set_version, check_version # noqa: I001
from pyterrier_anserini._index import AnseriniIndex
from pyterrier_anserini._indexer import AnseriniIndexer
from pyterrier_anserini._legacy import AnseriniBatchRetrieve
from pyterrier_anserini._reranker import AnseriniReRanker
from pyterrier_anserini._retriever import AnseriniRetriever
from pyterrier_anserini._text_loader import AnseriniTextLoader
from pyterrier_anserini._similarity import AnseriniSimilarity

__all__ = [
    'set_version', 'check_version', 'AnseriniIndex', 'AnseriniIndexer', 'AnseriniRetriever', 'AnseriniReRanker',
    'AnseriniBatchRetrieve', 'AnseriniSimilarity', 'AnseriniTextLoader', 'J'
]
