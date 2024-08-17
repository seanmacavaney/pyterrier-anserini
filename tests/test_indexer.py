import tempfile
import unittest

import pyterrier as pt

import pyterrier_anserini


class TestAnseriniIndexer(unittest.TestCase):
    def test_index_vaswani(self):
        with tempfile.TemporaryDirectory() as d:
            index = pyterrier_anserini.AnseriniIndex(f'{d}/index')
            self.assertFalse(index.built())
            indexer = index.indexer()
            ds = pt.get_dataset('irds:vaswani')
            indexer.index(ds.get_corpus_iter())
            self.assertTrue(index.built())
            # Anything else worth asserting?
