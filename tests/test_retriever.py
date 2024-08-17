import unittest
import os
import pyterrier as pt
import pyterrier_anserini

class TestAnseriniRetriever(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.here = os.path.dirname(os.path.realpath(__file__))

    def test_anserini_vaswani(self):
        index = pyterrier_anserini.AnseriniIndex.from_url(os.path.join(self.here, "fixtures/vaswani.tar.lz4"))
        bm25 = index.bm25()
        qld = index.qld()
        tf_idf = index.tfidf()
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
        resOut = (tf_idf >> index.reranker('BM25') >> index.text_loader()).search("chemical reactions")
        self.assertEqual(len(resIn), len(resOut))
