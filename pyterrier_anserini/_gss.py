import re
from typing import List, Literal

import pyterrier as pt

import pyterrier_anserini

_gss_re = re.compile(r'-(?P<must_not_match>\S+)|"(?P<must_match>[^"]+)"|(?P<should_match>\S+)')


@pt.java.required
def gss_to_lucene(
    query: str,
    analyzer: object,
    *,
    content_field: str = 'contents',
    mode: Literal['strict', 'boost'] = 'strict',
    boost_rate: float = 10.,
) -> object:
    """Parses a query using a subset of Google Search Syntax (GSS) conventions into a Lucene query object.

    This implementation supports the following GSS features:
     - literal query terms: irs w9
     - terms that must match: irs "w9" (here w9 must occur in the document, but irs may or may not occur)
     - phrase matching: "irs w9" (here irs and w9 must occur in the document, and they must be adjacent to each other in
       the specified order)
     - negative term matching: irs w9 -1040 (1040 must NOT occur in the document, but irs and w9 may or may not occur)

    The method should behave somewhat similarly to Google Search, but a few known differences are present:
     - Lots of features are missing e.g., domain filtering (site:irs.gov), etc. They are treated as normal query terms.
     - The parsing almost certainly doesn't work the same exact way, especially for edge cases
     - Quoted matches are exact in Google Search, here the analyzer is applied (e.g., with stemming and such)
     - Similar story for negations -- the analyzer is applied

    There are two "modes":
     - "strict": the query is parsed as described above, with MUST and MUST_NOT clauses. This is more strict in that
       the "should" terms are not actually required to match, and the "must" terms are required to match. This best
       matches actual Google Search behavior, but may result in over-strict matching in some cases.
     - "boost": the query is parsed in a more lenient way, where all terms are added as SHOULD clauses, and the "must"
       and "phrase" matches are boosted by a factor of `boost_rate`. This means that documents that match those terms
       will be scored higher, but documents that don't match them may still be retrieved if they match other SHOULD
       terms.
    """
    assert mode in ('strict', 'boost'), f'Invalid mode: {mode}'
    J = pyterrier_anserini.J # noqa: N806 convention
    query_builder = J.BooleanQueryBuilder()
    for match in _gss_re.finditer(query):
        if match.group('must_not_match'):
            if mode == 'strict':
                for token in _tokenize(match.group('must_not_match'), analyzer, content_field=content_field):
                    query_builder.add(J.TermQuery(J.Term(content_field, token)), J.Occur.MUST_NOT)

        elif match.group('must_match'):
            tokens = _tokenize(match.group('must_match'), analyzer, content_field=content_field)
            if len(tokens) == 1:
                # single-term MUST
                term_query = J.TermQuery(J.Term(content_field, tokens[0]))
                if mode == 'strict':
                    query_builder.add(term_query, J.Occur.MUST)
                elif mode == 'boost':
                    query_builder.add(J.BoostQuery(term_query, boost_rate), J.Occur.SHOULD)
            else:
                # phrase MUST
                phrase_query_builder = J.PhraseQueryBuilder()
                for i, token in enumerate(tokens):
                    phrase_query_builder.add(J.Term(content_field, token), i)
                if mode == 'strict':
                    query_builder.add(phrase_query_builder.build(), J.Occur.MUST)
                elif mode == 'boost':
                    query_builder.add(J.BoostQuery(phrase_query_builder.build(), boost_rate), J.Occur.SHOULD)
                    for token in tokens:
                        query_builder.add(J.TermQuery(J.Term(content_field, token)), J.Occur.SHOULD)

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
