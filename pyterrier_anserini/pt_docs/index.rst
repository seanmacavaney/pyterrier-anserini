Anserini + PyTerrier
=====================================

`Anserini <https://github.com/castorini/anserini/>`__ is a retrieval toolkit built on top of
`Lucene <https://lucene.apache.org/>`__. ``pyterrier-anserini`` provides a `PyTerrier <https://github.com/terrier-org/pyterrier>`__-compatible
interface to Anserini, allowing you to easily run experiments and combine it with other systems.

.. BEGIN_README_SKIP

.. toctree::
   :maxdepth: 1

   Extras <extras>
   API Documentation <api>

.. END_README_SKIP

Quick Start
-------------------------------------

You can install ``pyterrier-anserini`` with pip:

.. code-block:: console
   :caption: Install ``pyterrier-anserini``

   $ pip install pyterrier-anserini

:class:`~pyterrier_anserini.AnseriniIndex` is the main class for working with Anserini.
For instance, you can download a pre-built index from HuggingFace and retrieve with BM25 using the following
snippet:

.. code-block:: python
   :caption: Load an Anserini index from HuggingFace and retrieve using BM25

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

.. cite.dblp:: conf/sigir/Yang0L17

This extension was built as part of the PyTerrier project:

.. cite.dblp:: conf/cikm/MacdonaldTMO21

This extension was written by `Sean MacAvaney <https://macavaney.us/>`__ at the University of Glasgow and was based on an
original implementation that was part of PyTerrier, written by `Craig Macdonald <https://www.dcs.gla.ac.uk/~craigm/>`__.
Check out the GitHub for `a full list of contributors <https://github.com/seanmacavaney/pyterrier-anserini/graphs/contributors>`__.
