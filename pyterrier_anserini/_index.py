import os
from typing import Dict, List, Literal, Optional, Union, Any
import pyterrier as pt
import pyterrier_alpha as pta
import pyterrier_anserini
from pyterrier_anserini import J
from pyterrier_anserini._wmodel import DEFAULT_WMODEL_ARGS, AnseriniWeightModel


@pt.java.required
class AnseriniIndex(pta.Artifact):
    """An Anserini index.

    An Anserini index is a directory containing a Lucene index built with Anserini.

    This object can be used to construct retrieval transformers.
    """

    def __init__(self, path: str):
        """Initializes a new Anserini index.

        Args:
            path: The path to the index.
        """
        self.path = path

    def built(self) -> bool:
        """Checks if this index is built.

        Returns:
            True if this index is built, False otherwise.
        """
        return os.path.exists(self.path)

    def indexer(self,
        *,
        fields: Union[List[str], Literal['*']] = '*',
        verbose: bool = False
    ) -> pt.Indexer:
        """Provides an indexer for this index.

        Args:
            fields: The fields to index. If '*' (default), all fields are indexed. Otherwise, the values of the fields
                provided in this argumetn are concatenated and indexed.
            verbose: Whether to display a progress bar when indexing.

        Category: Transformer Builders
        """
        return pyterrier_anserini.AnseriniIndexer(self,
            fields=fields,
            verbose=verbose)

    def retriever(self,
        wmodel: Union[str, AnseriniWeightModel],
        wmodel_args: Optional[Dict[str, Any]] = None,
        *,
        num_results: int = 1000,
        verbose: bool = False
    ) -> pt.Transformer:
        """Provides a retriever that uses the specified similarity function.

        Args:
            similarity: The similarity function to use.
            similarity_args: The arguments to the similarity function. Defaults to None.
            num_results: The number of results to return. Defaults to 1000.
            verbose: Output verbose logging. Defaults to False.

        Returns:
            A transformer that can be used to retrieve documents from this index.

        Category: Transformer Builders
        """
        return pyterrier_anserini.AnseriniRetriever(
            index=self,
            wmodel=wmodel,
            wmodel_args=wmodel_args,
            num_results=num_results,
            verbose=verbose)

    def bm25(self,
        *,
        k1: float = DEFAULT_WMODEL_ARGS['bm25.k1'],
        b: float = DEFAULT_WMODEL_ARGS['bm25.b'],
        num_results: int = 1000,
        verbose: bool = False
    ) -> pt.Transformer:
        """Providers a retriever that uses BM25 over this index.

        Args:
            k1: The BM25 k1 parameter. Defaults to 0.9.
            b: The BM25 b parameter. Defaults to 0.4.
            num_results: The number of results to return. Defaults to 1000.
            verbose: Output verbose logging. Defaults to False.

        Returns:
            A transformer that can be used to retrieve documents from this index using qld.

        Category: Transformer Builders
        """
        return pyterrier_anserini.AnseriniRetriever(
            index=self,
            wmodel=AnseriniWeightModel.bm25,
            wmodel_args={'bm25.k1': k1, 'bm25.b': b},
            num_results=num_results,
            verbose=verbose)

    def qld(self,
        *,
        mu: float = DEFAULT_WMODEL_ARGS['qld.mu'],
        num_results: int = 1000,
        verbose: bool = False
    ) -> pt.Transformer:
        """Providers a retriever that uses Query Likelihood with Dirichlet smoothing over this index.

        Args:
            mu: The Dirichlet smoothing parameter. Defaults to 1000.
            num_results: The number of results to return. Defaults to 1000.
            verbose: Output verbose logging. Defaults to False.

        Returns:
            A transformer that can be used to retrieve documents from this index using qld.

        Category: Transformer Builders
        """
        return pyterrier_anserini.AnseriniRetriever(
            index=self,
            wmodel=AnseriniWeightModel.qld,
            wmodel_args={'qld_mu': mu},
            num_results=num_results,
            verbose=verbose)

    def tfidf(self,
        *,
        num_results: int = 1000,
        verbose: bool = False
    ) -> pt.Transformer:
        """Provides a TF-IDF retriever over this index.

        Args:
            num_results: The number of results to return. Defaults to 1000.
            verbose: Output verbose logging. Defaults to False.

        Returns:
            A transformer that can be used to retrieve documents from this index using TF-IDF.

        Category: Transformer Builders
        """
        return pyterrier_anserini.AnseriniRetriever(
            index=self,
            wmodel=AnseriniWeightModel.tfidf,
            num_results=num_results,
            verbose=verbose)

    def impact(self,
        *,
        num_results: int = 1000,
        verbose: bool = False
    ) -> pt.Transformer:
        """Provides a retriever for pre-comptued impact scores.

        This is called "quantized" scoring in PISA or "TF" scoring in Terrier.

        Args:
            num_results: The number of results to return. Defaults to 1000.
            verbose: Output verbose logging. Defaults to False.

        Returns:
            A transformer that can be used to retrieve documents from this index using impact scores.

        Category: Transformer Builders
        """
        return pyterrier_anserini.AnseriniRetriever(
            index=self,
            wmodel=AnseriniWeightModel.impact,
            num_results=num_results,
            verbose=verbose)

    def reranker(self,
        wmodel: Union[str, AnseriniWeightModel],
        wmodel_args: Optional[Dict[str, Any]] = None,
        *,
        verbose: bool = False
    ) -> pt.Transformer:
        """Provides a reranker that uses the specified weithing model.

        Args:
            wmodel: The weighting model to use.
            wmodel_args: The arguments to the weight model. Defaults to None.
            verbose: Output verbose logging. Defaults to False.

        Returns:
            A transformer that can be used to score (rerank) documents from this index.

        Category: Transformer Builders
        """
        return pyterrier_anserini.AnseriniReRanker(
            index=self,
            wmodel=wmodel,
            wmodel_args=wmodel_args,
            verbose=verbose)

    def text_loader(self,
        fields: Union[List[str], str, Literal['*']] = '*',
        *,
        verbose: bool = False,
    ) -> pt.Transformer:
        """Provides a transformer that can be used to load the text from this index for each document.

        Args:
            fields: The fields to extract. When the literal '*' (default), extracts all available fields.
            verbose: Output verbose logging. Defaults to False.

        Returns:
            A transformer that can be used to load the text from this index for each document.

        Category: Transformer Builders
        """
        if fields == '*':
            fields = self.fields()
        elif isinstance(fields, str):
            fields = [fields]

        return pyterrier_anserini.AnseriniTextLoader(
            index=self,
            fields=fields,
            verbose=verbose)

    def _searcher(self):
        from pyserini.search.lucene import LuceneSearcher
        assert self.built(), "a searcher object can only be created if the index is built"
        return LuceneSearcher(self.path)

    def fields(self) -> List[str]:
        field_info = J.IndexReaderUtils.getFieldInfo(self._searcher().object.reader)
        return [k for k in field_info if k != 'id']

    def __repr__(self):
        return f"AnseriniIndex({self.path!r})"
