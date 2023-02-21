import sys

import pytest

import asdf
from asdf.exceptions import AsdfDeprecationWarning
from asdf.tests.helpers import assert_extension_correctness
from asdf.tests.objects import CustomExtension
from asdf.types import CustomType


def test_custom_type_warning():
    with pytest.warns(AsdfDeprecationWarning, match=r"^.* subclasses the deprecated CustomType .*$"):

        class NewCustomType(CustomType):
            pass


def test_asdf_in_fits_import_warning():
    if "asdf.fits_embed" in sys.modules:
        del sys.modules["asdf.fits_embed"]
    with pytest.warns(AsdfDeprecationWarning, match="AsdfInFits has been deprecated.*"):
        import asdf.fits_embed  # noqa: F401


def test_resolver_module_deprecation():
    with pytest.warns(AsdfDeprecationWarning, match="^asdf.resolver is deprecated.*$"):
        # importlib.reload doesn't appear to work here likely because of the
        # sys.module and __file__ changes in asdf.resolver
        if "asdf.resolver" in sys.modules:
            del sys.modules["asdf.resolver"]
        import asdf.resolver  # noqa: F401


def test_assert_extension_correctness_deprecation():
    extension = CustomExtension()
    with pytest.warns(AsdfDeprecationWarning, match="assert_extension_correctness is deprecated.*"):
        assert_extension_correctness(extension)


def test_type_index_module_deprecation():
    with pytest.warns(AsdfDeprecationWarning, match="^asdf.type_index is deprecated.*$"):
        # importlib.reload doesn't appear to work here likely because of the
        # sys.module and __file__ changes in asdf.type_index
        if "asdf.type_index" in sys.modules:
            del sys.modules["asdf.type_index"]
        import asdf.type_index  # noqa: F401


@pytest.mark.parametrize("attr", ["url_mapping", "tag_mapping", "resolver", "extension_list", "type_index"])
def test_asdffile_legacy_extension_api_attr_deprecations(attr):
    with asdf.AsdfFile() as af, pytest.warns(AsdfDeprecationWarning, match=f"AsdfFile.{attr} is deprecated"):
        getattr(af, attr)


def test_asdfile_run_hook_deprecation():
    with asdf.AsdfFile() as af, pytest.warns(AsdfDeprecationWarning, match="AsdfFile.run_hook is deprecated"):
        af.run_hook("foo")


def test_asdfile_run_modifying_hook_deprecation():
    with asdf.AsdfFile() as af, pytest.warns(AsdfDeprecationWarning, match="AsdfFile.run_modifying_hook is deprecated"):
        af.run_modifying_hook("foo")
