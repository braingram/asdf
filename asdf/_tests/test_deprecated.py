import pytest

import asdf


@pytest.mark.parametrize("value", (True, False))
def test_deprecate_refresh_extension_manager(value):
    af = asdf.AsdfFile({"foo": 1})
    with pytest.warns(DeprecationWarning, match="refresh_extension_manager is deprecated"):
        af.schema_info(refresh_extension_manager=value)
    with pytest.warns(DeprecationWarning, match="refresh_extension_manager is deprecated"):
        af.info(refresh_extension_manager=value)
    sr = af.search("foo")
    with pytest.warns(DeprecationWarning, match="refresh_extension_manager is deprecated"):
        sr.schema_info(refresh_extension_manager=value)
