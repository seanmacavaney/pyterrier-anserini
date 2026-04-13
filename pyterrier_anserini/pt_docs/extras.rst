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


Google Search Syntax (GSS)
------------------------------------------------

Queries can be executed using a subset of Google Search's Syntax by providing queries in the ``query_gss`` field.
The index must be built with positions stored in order to use phrase matching.

Example:

.. code-block:: python
   :caption: Using Google Search Syntax

   index = AnseriniIndex('path/to/index')
   retriever = index.bm25()
   retriever(pd.DataFrame([
      {'qid': '0', 'query_gss': '"hello world"'}, # must match phrase "hello world"
      {'qid': '1', 'query_gss': 'hello "world"'}, # must include "world"
      {'qid': '2', 'query_gss': 'hello world -universe'}, # must NOT include "universe"
   ]))

The supported syntax rules are:
 - **Phrase match**: Enclose a sequence of words in double quotes to match the exact phrase. For example, ``"hello world"`` will boost documents containing the exact phrase "hello world".
 - **Required term**: Enclose a single word in double quotes to indicate that it will be boosted.
 - **Prohibited term**: Prefix a single word with a minus sign to indicate that it must not be present in the matching documents. These are ignored when scoring.
