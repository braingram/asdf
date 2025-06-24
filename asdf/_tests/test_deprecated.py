import pytest

import asdf


def test_url_mapping_deprecation():
    with pytest.warns(DeprecationWarning, match="url_mapping is deprecated"):
        asdf.schema.get_validator(url_mapping=lambda s: s)
