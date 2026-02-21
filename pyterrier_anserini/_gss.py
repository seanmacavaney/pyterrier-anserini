from typing import List
import re
import pyterrier as pt

_gss_re = re.compile(r'site:(?P<domain_filter>[.a-zA-Z0-9-]+)|"(?P<must_match>[^"]+)"|(?P<should_match>\S+)')


@pt.java.required
def gss_to_lucene(
    query: str,
    analyzer: object,
    *,
    content_field: str = 'content',
    domain_field: str = 'domain',
) -> object:
    """ Parses a query using a subset of Google Search Syntax (GSS) conventions into a Lucene query object.

    This implementation supports the following GSS features:
     - literal query terms: irs w9
     - terms that must match: irs "w9" (here w9 must occur in the document, but irs may or may not occur)
     - phrase matching: "irs w9" (here irs and w9 must occur in the document, and they must be adjacent to each other in the specified order)
     - site filtering: site:irs.gov (matches documents from irs.gov and any subdomains, e.g. forms.irs.gov)

    The method should mostly behave similarly to Google Search, but a few known differences are present:
     - The parsing almost certainly doesn't work the same exact way, especially for edge cases
     - Quoted matches are exact in Google Search, here the analyzer is applied (e.g., with stemming and such)
    """
    query_builder = J.BooleanQueryBuilder()
    for match in _gss_re.finditer(query):
        if match.group('domain_filter'):
            domain_suffix = match.group('domain_filter').lower()
            if domain_suffix.startswith('.'):
                # example: site:.gov -> matches any domain that ends with .gov (freedom.gov, eagle.freedom.gov, etc.)
                query_builder.add(J.WildcardQuery(J.Term(domain_field, f'*{domain_suffix}')), J.Occur.FILTER)
            else:
                # example: site:freedom.gov -> matches freedom.gov and any subdomains (eagle.freedom.gov)
                domain_filter_builder = J.BooleanQueryBuilder()
                domain_filter_builder.add(J.TermQuery(J.Term(domain_field, domain_suffix)), J.Occur.SHOULD)
                domain_filter_builder.add(J.WildcardQuery(J.Term(domain_field, f'*.{domain_suffix}')), J.Occur.SHOULD)
                query_builder.add(domain_filter_builder.build(), J.Occur.FILTER)

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
        term_attrib = stream.addAttribute(J.CharTermAttribute)
        stream.reset()
        while stream.incrementToken():
            tokens.append(term_attrib.toString())
    finally:
        stream.end()
        stream.close()

    return tokens


J = pt.java.JavaClasses(
    BooleanQueryBuilder = 'org.apache.lucene.search.BooleanQuery$Builder',
    PhraseQueryBuilder = 'org.apache.lucene.search.PhraseQuery$Builder',
    Occur = 'org.apache.lucene.search.BooleanClause$Occur',
    TermQuery = 'org.apache.lucene.search.TermQuery',
    WildcardQuery = 'org.apache.lucene.search.WildcardQuery',
    Term = 'org.apache.lucene.index.Term',
    CharTermAttribute = 'org.apache.lucene.analysis.tokenattributes.CharTermAttribute',
)
