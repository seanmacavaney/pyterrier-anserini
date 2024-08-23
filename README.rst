.. NOTE: this file was generated from pyterrier_anserini/pt_docs/index.rst. Changes made to README.rst may be reverted.
.. Make any changes to pyterrier_anserini/pt_docs/index.rst instead.

Anserini + PyTerrier
=====================================

`Anserini <https://github.com/castorini/anserini/>`__ is a retrieval toolkit built on top of
`Lucene <https://lucene.apache.org/>`__. ``pyterrier-anserini`` provides a `PyTerrier <https://github.com/terrier-org/pyterrier>`__-compatible
interface to Anserini, allowing you to easily run experiments and combine it with other systems.


Quick Start
-------------------------------------

You can install ``pyterrier-anserini`` with pip:

.. code-block:: console

   $ pip install pyterrier-anserini

``pyterrier_anserini.AnseriniIndex`` is the main class for working with Anserini.
For instance, you can download a pre-built index from HuggingFace and retrieve with BM25 using the following
snippet:

.. code-block:: python

   >>> from pyterrier_anserini import AnseriniIndex
   >>> index = AnseriniIndex.from_hf('macavaney/msmarco-passage.anserini')
   >>> bm25 = index.bm25(include_fields=['contents'])
   >>> bm25.search('terrier breeds')
     qid           query    docno    score  rank                                      contents
   0   1  terrier breeds  5785957  11.9588     0  The Jack Russell Terrier and the Russell ...
   1   1  terrier breeds  7455374  11.9343     1  FCI, ANKC, and IKC recognize the shorts a...
   2   1  terrier breeds  1406578  11.8640     2  Norfolk terrier (English breed of small t...
   3   1  terrier breeds  3984886  11.7518     3  Terrier Group is the name of a breed Grou...
   4   1  terrier breeds  7728131  11.5660     4  The Yorkshire Terrier didn't begin as the...
   ...

Acknowledgements
-------------------------------------

This extension uses the Anserini package. If you use it, please be sure to cite Anserini:

.. code-block:: bibtex

   @inproceedings{DBLP:conf/sigir/Yang0L17,
     author       = {Peilin Yang and
                     Hui Fang and
                     Jimmy Lin},
     title        = {Anserini: Enabling the Use of Lucene for Information Retrieval Research},
     booktitle    = {Proceedings of the 40th International {ACM} {SIGIR} Conference on
                     Research and Development in Information Retrieval, Shinjuku, Tokyo,
                     Japan, August 7-11, 2017},
     pages        = {1253--1256},
     publisher    = {{ACM}},
     year         = {2017},
     url          = {https://doi.org/10.1145/3077136.3080721},
     doi          = {10.1145/3077136.3080721}
   }

This extension was built as part of the PyTerrier project. If you use it, please be sure to cite PyTerrier:

.. code-block:: bibtex

   @inproceedings{DBLP:conf/cikm/MacdonaldTMO21,
     author       = {Craig Macdonald and
                     Nicola Tonellotto and
                     Sean MacAvaney and
                     Iadh Ounis},
     title        = {PyTerrier: Declarative Experimentation in Python from {BM25} to Dense
                     Retrieval},
     booktitle    = {{CIKM} '21: The 30th {ACM} International Conference on Information
                     and Knowledge Management, Virtual Event, Queensland, Australia, November
                     1 - 5, 2021},
     pages        = {4526--4533},
     publisher    = {{ACM}},
     year         = {2021},
     url          = {https://doi.org/10.1145/3459637.3482013},
     doi          = {10.1145/3459637.3482013}
   }

This extension was written by `Sean MacAvaney <https://macavaney.us/>`__ at the University of Glasgow and was based on an
original implementation that was part of PyTerrier, written by `Craig Macdonald <https://www.dcs.gla.ac.uk/~craigm/>`__.
Check out the GitHub for `a full list of contributors <https://github.com/seanmacavaney/pyterrier-anserini/graphs/contributors>`__.
