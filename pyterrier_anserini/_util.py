from typing import Any, Dict, List, Optional
from urllib.parse import ParseResult

import pyterrier as pt


@pt.java.required
def _anserini_url_resolver(parsed_url: ParseResult) -> str:
    """Resolve URLs like Artifact.from_url("anserini:some-index")."""
    from pyserini.util import download_prebuilt_index
    return download_prebuilt_index(parsed_url.path)


def _anserini_metadata_adapter(path: str, dir_listing: List[str]) -> Optional[Dict[str, Any]]:
    """Guess whether this path is an anserini index.

    There are a few files that seem to be a good indicator. Check for those.

    (Actually, these identify any lucene index, but I guess this is alright.)
    """
    if 'write.lock' in dir_listing and any(x.startswith('segments_') for x in dir_listing):
        return {
            'type': 'sparse_index',
            'format': 'anserini',
            'package_hint': 'pyterrier-anserini',
        }
