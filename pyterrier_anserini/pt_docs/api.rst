``pyterrir_anserini`` API Documentation
=======================================

``AnseriniIndex`` is the primary class for interacting with Anserini indexes in PyTerrier. It acts as a factory for
creating transformers that can index, retrieve, and re-rank. It also has methods for providing information about the
index and for downloading pre-built indexes.


.. autoclass:: pyterrier_anserini.AnseriniIndex
   :members:

Transformers and Indexers
---------------------------------------

The following transformer classes are returned by corresponding factory methods in
:class:`~pyterrier_anserini.AnseriniIndex`.

.. autoclass:: pyterrier_anserini.AnseriniIndexer
   :members:

.. autoclass:: pyterrier_anserini.AnseriniRetriever
   :members:

.. autoclass:: pyterrier_anserini.AnseriniReRanker
   :members:

.. autoclass:: pyterrier_anserini.AnseriniTextLoader
   :members:

Miscellaneous
---------------------------------------

.. autoenum:: pyterrier_anserini.AnseriniSimilarity
   :members:

.. autofunction:: pyterrier_anserini.set_version

