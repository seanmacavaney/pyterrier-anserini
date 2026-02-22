from typing import List
import re
import pyterrier as pt

import pyterrier_anserini

_gss_re = re.compile(r'-(?P<must_not_match>\S+)|"(?P<must_match>[^"]+)"|(?P<should_match>\S+)')


@pt.java.required
def gss_to_lucene(
    query: str,
    analyzer: object,
    *,
    content_field: str = 'contents',
) -> object:
    """ Parses a query using a subset of Google Search Syntax (GSS) conventions into a Lucene query object.

    This implementation supports the following GSS features:
     - literal query terms: irs w9
     - terms that must match: irs "w9" (here w9 must occur in the document, but irs may or may not occur)
     - phrase matching: "irs w9" (here irs and w9 must occur in the document, and they must be adjacent to each other in the specified order)
     - negative term matching: irs w9 -1040 (1040 must NOT occur in the document, but irs and w9 may or may not occur)

    The method should behave somewhat similarly to Google Search, but a few known differences are present:
     - Lots of features are missing -- e.g., domain filtering (site:irs.gov), etc. These are treated as normal query terms.
     - The parsing almost certainly doesn't work the same exact way, especially for edge cases
     - Quoted matches are exact in Google Search, here the analyzer is applied (e.g., with stemming and such)
     - Similar story for negations -- the analyzer is applied
    """
    J = pyterrier_anserini.J
    query_builder = J.BooleanQueryBuilder()
    for match in _gss_re.finditer(query):
        if match.group('must_not_match'):
            for token in _tokenize(match.group('must_not_match'), analyzer, content_field=content_field):
                query_builder.add(J.TermQuery(J.Term(content_field, token)), J.Occur.MUST_NOT)

        elif match.group('must_match'):
            tokens = _tokenize(match.group('must_match'), analyzer, content_field=content_field)
            if len(tokens) == 1:
                # single-term MUST
                query_builder.add(J.TermQuery(J.Term(content_field, tokens[0])), J.Occur.MUST)
            else:
                # phrase MUST
                phrase_query_builder = J.PhraseQueryBuilder()
                for i, token in enumerate(tokens):
                    phrase_query_builder.add(J.Term(content_field, token), i)
                query_builder.add(phrase_query_builder.build(), J.Occur.MUST)

        elif match.group('should_match'):
            for token in _tokenize(match.group('should_match'), analyzer, content_field=content_field):
                query_builder.add(J.TermQuery(J.Term(content_field, token)), J.Occur.SHOULD)

    return query_builder.build()


def _tokenize(query: str, analyzer: object, *, content_field: str = 'content') -> List[str]:
    stream = analyzer.tokenStream(content_field, query)
    tokens = []

    try:
        term_attrib = stream.addAttribute(pyterrier_anserini.J.CharTermAttribute)
        stream.reset()
        while stream.incrementToken():
            tokens.append(term_attrib.toString())
    finally:
        stream.end()
        stream.close()

    return tokens
