import unittest
import os
import pyterrier as pt
import pyterrier_anserini

class TestAnseriniRetriever(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.here = os.path.dirname(os.path.realpath(__file__))

    def test_anserini_vaswani(self):
        dest_index = os.path.join(self.here, "fixtures", "anserini_index")
        bm25 = pyterrier_anserini.AnseriniRetriever(dest_index)
        qld = pyterrier_anserini.AnseriniRetriever(dest_index, wmodel='QLD')
        tf_idf = pyterrier_anserini.AnseriniRetriever(dest_index, wmodel='TFIDF')
        dataset = pt.get_dataset("vaswani")
        df = pt.Experiment([
                bm25,
                qld,
                tf_idf                
            ], 
            dataset.get_topics(), 
            dataset.get_qrels(), 
            ["map"])
        self.assertEqual(0.2856564466226712, df.iloc[0]["map"])
        for i in df['map']:
            self.assertGreater(i, 0)
        
        # check re-ranking works too
        resIn = tf_idf.search("chemical reactions") 
        resOut = (tf_idf >> bm25).search("chemical reactions")
        self.assertEqual(len(resIn), len(resOut))
