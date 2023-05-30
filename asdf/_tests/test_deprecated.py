import sys

import pytest

import asdf
import asdf._types
import asdf.extension
import asdf.testing.helpers
from asdf._tests._helpers import assert_extension_correctness
from asdf._tests.objects import CustomExtension
from asdf._types import CustomType
from asdf.exceptions import AsdfDeprecationWarning

from .test_entry_points import _monkeypatch_entry_points, mock_entry_points  # noqa: F401


def test_custom_type_warning():
    with pytest.warns(AsdfDeprecationWarning, match=r"^.* subclasses the deprecated CustomType .*$"):

        class NewCustomType(CustomType):
            pass


def test_assert_extension_correctness_deprecation():
    extension = CustomExtension()
    with pytest.warns(AsdfDeprecationWarning, match="assert_extension_correctness is deprecated.*"):
        assert_extension_correctness(extension)


def test_asdf_type_format_tag():
    with pytest.warns(AsdfDeprecationWarning, match="asdf.types.format_tag is deprecated"):
        asdf._types.format_tag
    asdf.testing.helpers.format_tag


def test_asdf_tests_helpers_deprecation():
    with pytest.warns(AsdfDeprecationWarning, match="asdf.tests.helpers is deprecated"):
        if "asdf.tests.helpers" in sys.modules:
            del sys.modules["asdf.tests.helpers"]
        import asdf.tests.helpers
    from asdf._tests import _helpers

    for attr in _helpers.__all__:
        with pytest.warns(AsdfDeprecationWarning, match="asdf.tests.helpers is deprecated"):
            getattr(asdf.tests.helpers, attr)
