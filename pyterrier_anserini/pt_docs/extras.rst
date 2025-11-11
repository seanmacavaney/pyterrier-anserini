Extra Anserini Features
================================================

Anserini-hosted Pre-Built Indexes
------------------------------------------------

Anserini hosts a variety of `pre-built indexes <https://github.com/castorini/pyserini/blob/master/docs/prebuilt-indexes.md>`_.
The ``pyterrier-anserini`` package supports accessing these through :meth:`Artifact.from_url() <pyterrier.Artifact.from_url>`
by using the ``"anserini:"`` URL prefix. For instance, to load the ``msmarco-v1-passage`` index from Anserini, run:

.. code-block:: python
   :caption: Load an Anserini-hosted index

   >>> index = AnseriniIndex.from_url("anserini:msmarco-v1-passage")
   Downloading index at https://rgw.cs.uwaterloo.ca/pyserini/indexes/lucene/lucene-inverted.msmarco-v1-passage.20221004.252b5e.tar.gz...


You can find a list of available indexes `here <https://github.com/castorini/pyserini/blob/master/docs/prebuilt-indexes.md>`_.

Note that you can also load indexes from HuggingFace and share ones you've built through the :ref:`Artifact API <artifacts>`:

.. code-block:: python
   :caption: Load an Anserini index from HuggingFace

   >>> index = AnseriniIndex.from_hf('macavaney/msmarco-passage.anserini')

.. code-block:: python
   :caption: Share an Anserini index to HuggingFace

   >>> my_index.to_hf('username/my_index.anserini')
