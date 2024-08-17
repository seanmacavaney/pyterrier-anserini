import unittest
import os
import pandas as pd
import pyterrier as pt
import pyterrier_anserini

class TestAnseriniRetriever(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.index = pyterrier_anserini.AnseriniIndex.from_url(os.path.join(os.path.dirname(os.path.realpath(__file__)), "fixtures/vaswani.tar.lz4"))

    def test_vaswani(self):
        bm25 = self.index.bm25()
        qld = self.index.qld()
        tf_idf = self.index.tfidf()
        dataset = pt.get_dataset("vaswani")
        df = pt.Experiment([
                bm25,
                qld,
                tf_idf                
            ], 
            dataset.get_topics(), 
            dataset.get_qrels(), 
            ["map"])
        self.assertAlmostEqual(0.2856, df.iloc[0]["map"], places=4)
        for i in df['map']:
            self.assertGreater(i, 0)
        
        # check re-ranking works too
        resIn = tf_idf.search("chemical reactions") 
        resOut = (tf_idf >> self.index.reranker('BM25') >> self.index.text_loader()).search("chemical reactions")
        self.assertEqual(len(resIn), len(resOut))

    def test_vaswani_impact(self):
        impact = self.index.impact()
        res = impact(pd.DataFrame([
            {'qid': '1', 'query_toks': {'chemical': 5.3, 'reactions': 1.1}},
        ]))
        self.assertEqual(len(res), 52)
        self.assertEqual(res['score'][0], 10.6)
