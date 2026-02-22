Anserini How-To Guides
============================================================

This page provides a set of how-to guides for using Anserini with PyTerrier.

.. how-to:: How do I index a standard corpus?

    .. _anserini:how-to:index-standard:
    .. related:: pyterrier_anserini.AnseriniIndex.index

    .. code-block:: python
        :caption: Indexing a standard corpus with Anserini

        import pyterrier as pt
        from pyterrier_anserini import AnseriniIndex
        dataset = pt.datasets.get_dataset("irds:msmarco-passage") # :footnote: Select your dataset here. If the corpus is not available in PyTerrier datasets, see :ref:`anserni:how-to:index-custom`
        my_index = AnseriniIndex('/path/to/index/location.anserini') # :footnote: Specify the location where you want to store the Anserini index. The location must not yet exist. We recommend using the ``.anserini`` extension, though this is not required.
        my_index.index(dataset.get_corpus_iter()) # :footnote: This performs indexing with default settings. If you need more control over the indexing settings, see :meth:`~pyterrier_anserini.AnseriniIndex.indexer` for advanced options.



.. how-to:: How do I index a custom collection?

    .. _anserini:how-to:index-custom:
    .. related:: pyterrier_anserini.AnseriniIndex.indexer

    .. code-block:: python
        :caption: Indexing a custom collection with Anserini

        import pyterrier as pt
        my_collection = [ # :footnote: Each document should be a dictionary with ``docno`` (a unique identifier) and additional text fields. Your collection can be any iterable type (list, generator, etc.).
            {"docno": "doc1", "title": "This is the text of document one.", "body": "This is the body of document one."},
            {"docno": "doc2", "title": "This is the text of document two.", "body": "This is the body of document two."},
            {"docno": "doc3", "title": "This is the text of document three.", "body": "This is the body of document three."}
        ]
        my_index = AnseriniIndex('/path/to/index/location.anserini') # :footnote: Specify the location where you want to store the Anserini index. The location must not yet exist. We recommend using the ``.anserini`` extension, though this is not required.
        indexer = my_index.indexer(fields=["title", "body"]) # :footnote: ``fields=...`` lets you specify which fields to index. If you do not specify this option, all string fields will be merged automatically.
        indexer.index(my_collection)


.. how-to:: How do I retrieve documents from an Anserini index with BM25?

    .. related:: pyterrier_anserini.AnseriniIndex.bm25

    .. code-block:: python
        :caption: Retrieving documents from an Anserini index with BM25

        import pyterrier as pt
        from pyterrier_anserini import AnseriniIndex
        index = AnseriniIndex('/path/to/index.location.anserini') # :footnote: Specify the location of your Anserini index.
        bm25 = index.bm25() # :footnote: This creates a BM25 retriever. You can also create other retrievers or re-rankers using the corresponding factory methods in AnseriniIndex.
        queries = pd.DataFrame([{"qid": "1", "query": "example query"}]) # :footnote: Create a DataFrame with your queries. The DataFrame must have a ``qid`` column for query IDs and a ``query`` column for query text.
        results = bm25(queries) # :footnote: This runs retrieval and returns a DataFrame with results. By default, the results will include the ``docno`` and ``score`` fields, but you can include additional fields using the ``include_fields=...`` option when creating the retriever.
