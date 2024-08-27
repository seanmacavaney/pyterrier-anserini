from typing import List, Optional

import pyterrier as pt

import pyterrier_anserini


class AnseriniTokenizer:
    """Represents a tokenizer configuration for Anserini.

    You can provide a ``AnseriniTokenizer`` instance when building an Anserini index to control how text is processed
    during indexing and retrieval.

    You can also use ``AnseriniTokenizer`` to tokenize arbitrary text:

    .. code-block:: python
        :caption: Tokenize text with :class:`~anserini_tokenizer.AnseriniTokenizer`

        >>> from pyterrier_anserini import AnseriniTokenizer
        >>> tokenizer = AnseriniTokenizer.en
        >>> tokenizer.tokenize('Hello, world!')
        ['hello', 'world']

    The following standard tokenizer configurations are available as static members of this class:

    =======================================  ==========================
    Tokenizer                                Description
    =======================================  ==========================
    ``AnseriniTokenizer.ar``                 Arabic
    ``AnseriniTokenizer.bn``                 Bengali
    ``AnseriniTokenizer.da``                 Danish
    ``AnseriniTokenizer.de``                 German
    ``AnseriniTokenizer.en``                 English (Porter stemmer)
    ``AnseriniTokenizer.en_nostem``          English (no stemming)
    ``AnseriniTokenizer.es``                 Spanish
    ``AnseriniTokenizer.fi``                 Finnish
    ``AnseriniTokenizer.fr``                 French
    ``AnseriniTokenizer.hi``                 Hindi
    ``AnseriniTokenizer.hu``                 Hungarian
    ``AnseriniTokenizer.huggingface(name)``  HuggingFace tokenizer
    ``AnseriniTokenizer.id``                 Indonesian
    ``AnseriniTokenizer.it``                 Italian
    ``AnseriniTokenizer.ja``                 Japanese
    ``AnseriniTokenizer.ko``                 Korean
    ``AnseriniTokenizer.nl``                 Dutch
    ``AnseriniTokenizer.no``                 Norwegian
    ``AnseriniTokenizer.pt``                 Portuguese
    ``AnseriniTokenizer.ru``                 Russian
    ``AnseriniTokenizer.sv``                 Swedish
    ``AnseriniTokenizer.te``                 Telugu
    ``AnseriniTokenizer.th``                 Thai
    ``AnseriniTokenizer.tr``                 Turkish
    ``AnseriniTokenizer.tweet``              Twitter
    ``AnseriniTokenizer.whitespace``         Whitespace
    ``AnseriniTokenizer.zh``                 Chinese
    =======================================  ==========================
    """

    def __init__(self, analyzer_class_name: str, analyzer_variant: Optional[str] = None):
        """Initializes the tokenizer.

        Args:
            analyzer_class_name: The name of the analyzer class to use.
            analyzer_variant: The variant of the analyzer to use, if any.
        """
        self._analyzer_class_name = analyzer_class_name
        self._analyzer_variant = analyzer_variant
        self._analyzer = None

    @pt.java.required
    def tokenize(self, inp: str) -> List[str]:
        """Tokenizes the input string.

        Args:
            inp: The input string to tokenize.
        """
        results = pyterrier_anserini.J.AnalyzerUtils.analyze(self.to_lucene_analyzer(), inp)
        return list(results.toArray())

    @pt.java.required
    def to_lucene_analyzer(self):
        """Returns a Java analyzer object that represents this tokenizer."""
        if self._analyzer is None:
            analyzer_cls = pt.java.autoclass(self._analyzer_class_name)
            if self._analyzer_class_name == 'io.anserini.analysis.DefaultEnglishAnalyzer':
                if self._analyzer_variant is None:
                    self._analyzer = analyzer_cls.newNonStemmingInstance()
                else:
                    self._analyzer = analyzer_cls.newStemmingInstance(self._analyzer_variant)
            elif self._analyzer_class_name == 'io.anserini.analysis.HuggingFaceTokenizerAnalyzer':
                if self._analyzer_variant is None:
                    raise ValueError('You must to specify the huggingface tokenizer name when using '
                                     'AnseriniTokenizer.huggingface, e.g., '
                                     'AnseriniTokenizer.huggingface("bert-base-uncased")')
                self._analyzer = analyzer_cls(self._analyzer_variant)
            else:
                if self._analyzer_variant is not None:
                    raise ValueError(f'A variant was specified for {self._analyzer_class_name}, which does not '
                                      'support it')
                self._analyzer = analyzer_cls()
        return self._analyzer

    def __call__(self, variant: Optional[str]):
        return AnseriniTokenizer(self._analyzer_class_name, variant)

    def __reduce__(self):
        # to enable picking without the java-bound _analyzer
        return (AnseriniTokenizer, (self._analyzer_class_name, self._analyzer_variant))

    def __repr__(self):
        if self._analyzer_variant is None:
            return f'AnseriniTokenizer({self._analyzer_class_name!r})'
        return f'AnseriniTokenizer({self._analyzer_class_name!r}, {self._analyzer_variant!r})'


AnseriniTokenizer.ar = AnseriniTokenizer('org.apache.lucene.analysis.ar.ArabicAnalyzer')
AnseriniTokenizer.bn = AnseriniTokenizer('org.apache.lucene.analysis.bn.BengaliAnalyzer')
AnseriniTokenizer.zh = AnseriniTokenizer('org.apache.lucene.analysis.cjk.CJKAnalyzer')
AnseriniTokenizer.ko = AnseriniTokenizer('org.apache.lucene.analysis.cjk.CJKAnalyzer')
AnseriniTokenizer.da = AnseriniTokenizer('org.apache.lucene.analysis.da.DanishAnalyzer')
AnseriniTokenizer.nl = AnseriniTokenizer('org.apache.lucene.analysis.nl.DutchAnalyzer')
AnseriniTokenizer.fi = AnseriniTokenizer('org.apache.lucene.analysis.fi.FinnishAnalyzer')
AnseriniTokenizer.fr = AnseriniTokenizer('org.apache.lucene.analysis.fr.FrenchAnalyzer')
AnseriniTokenizer.de = AnseriniTokenizer('org.apache.lucene.analysis.de.GermanAnalyzer')
AnseriniTokenizer.hi = AnseriniTokenizer('org.apache.lucene.analysis.hi.HindiAnalyzer')
AnseriniTokenizer.hu = AnseriniTokenizer('org.apache.lucene.analysis.hu.HungarianAnalyzer')
AnseriniTokenizer.id = AnseriniTokenizer('org.apache.lucene.analysis.id.IndonesianAnalyzer')
AnseriniTokenizer.it = AnseriniTokenizer('org.apache.lucene.analysis.it.ItalianAnalyzer')
AnseriniTokenizer.ja = AnseriniTokenizer('org.apache.lucene.analysis.ja.JapaneseAnalyzer')
AnseriniTokenizer.no = AnseriniTokenizer('org.apache.lucene.analysis.no.NorwegianAnalyzer')
AnseriniTokenizer.pt = AnseriniTokenizer('org.apache.lucene.analysis.pt.PortugueseAnalyzer')
AnseriniTokenizer.ru = AnseriniTokenizer('org.apache.lucene.analysis.ru.RussianAnalyzer')
AnseriniTokenizer.es = AnseriniTokenizer('org.apache.lucene.analysis.es.SpanishAnalyzer')
AnseriniTokenizer.sv = AnseriniTokenizer('org.apache.lucene.analysis.sv.SwedishAnalyzer')
AnseriniTokenizer.te = AnseriniTokenizer('org.apache.lucene.analysis.te.TeluguAnalyzer')
AnseriniTokenizer.th = AnseriniTokenizer('org.apache.lucene.analysis.th.ThaiAnalyzer')
AnseriniTokenizer.tr = AnseriniTokenizer('org.apache.lucene.analysis.tr.TurkishAnalyzer')
AnseriniTokenizer.whitespace = AnseriniTokenizer('org.apache.lucene.analysis.core.WhitespaceAnalyzer')
AnseriniTokenizer.en = AnseriniTokenizer('io.anserini.analysis.DefaultEnglishAnalyzer')('porter')
AnseriniTokenizer.en_nostem = AnseriniTokenizer('io.anserini.analysis.DefaultEnglishAnalyzer')
AnseriniTokenizer.tweet = AnseriniTokenizer('io.anserini.analysis.TweetAnalyzer')
AnseriniTokenizer.huggingface = AnseriniTokenizer('io.anserini.analysis.HuggingFaceTokenizerAnalyzer')
