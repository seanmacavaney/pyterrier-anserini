import unittest

import pyterrier as pt
import pyterrier_alpha as pta

import pyterrier_anserini


class TestGss(unittest.TestCase):
    def test_gss_to_lucene(self):
        # This tests a few things: that the anserini: parser is working, that the metadata adapter works, etc.
        analyzer = pyterrier_anserini.J.StandardAnalyzer()
        self.assertEqual('contents:hello contents:world', pyterrier_anserini.gss_to_lucene('hello world', analyzer).toString())
        self.assertEqual('contents:hello +contents:world', pyterrier_anserini.gss_to_lucene('hello "world"', analyzer).toString())
        self.assertEqual('+contents:"hello world"', pyterrier_anserini.gss_to_lucene('"hello world"', analyzer).toString())
        self.assertEqual('+contents:"hello world" -contents:universe', pyterrier_anserini.gss_to_lucene('"hello world" -universe', analyzer).toString())
        self.assertEqual('contents:hello contents:world', pyterrier_anserini.gss_to_lucene('hello world', analyzer, mode='boost').toString())
        self.assertEqual('contents:hello (contents:world)^10.0', pyterrier_anserini.gss_to_lucene('hello "world"', analyzer, mode='boost').toString())
        self.assertEqual('(contents:"hello world")^10.0 contents:hello contents:world', pyterrier_anserini.gss_to_lucene('"hello world"', analyzer, mode='boost').toString())
        self.assertEqual('(contents:"hello world")^10.0 contents:hello contents:world', pyterrier_anserini.gss_to_lucene('"hello world" -universe', analyzer, mode='boost').toString())
