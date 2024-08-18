import unittest

import pyterrier as pt
import pyterrier_alpha as pta


class TestAnseriniIndex(unittest.TestCase):
    def test_load_from_anserini_url(self):
        # This tests a few things: that the anserini: parser is working, that the metadata adapter works, etc.
        index = pta.Artifact.from_url('anserini:beir-v1.0.0-scifact.flat')
        self.assertEqual(5183, index.num_docs())
