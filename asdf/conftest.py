# This contains pytest fixtures used in asdf tests.
# by importing them here in conftest.py they are discoverable by pytest
# no matter how it is invoked within the source tree.


import pytest

from asdf.exceptions import AsdfCustomTypeDeprecationWarning
from asdf.tests.httpserver import HTTPServer, RangeHTTPServer


@pytest.fixture()
def httpserver(request):
    """
    The returned ``httpserver`` provides a threaded HTTP server
    instance.  It serves content from a temporary directory (available
    as the attribute tmpdir) at randomly assigned URL (available as
    the attribute url).

    * ``tmpdir`` - path to the tmpdir that it's serving from (str)
    * ``url`` - the base url for the server
    """
    server = HTTPServer()
    yield server
    server.finalize()


@pytest.fixture()
def rhttpserver(request):
    """
    The returned ``httpserver`` provides a threaded HTTP server
    instance.  It serves content from a temporary directory (available
    as the attribute tmpdir) at randomly assigned URL (available as
    the attribute url).  The server supports HTTP Range headers.

    * ``tmpdir`` - path to the tmpdir that it's serving from (str)
    * ``url`` - the base url for the server
    """
    server = RangeHTTPServer()
    yield server
    server.finalize()


@pytest.fixture()
def custom_test_type():
    from asdf import CustomType

    with pytest.warns(
        AsdfCustomTypeDeprecationWarning,
        match=r"CustomTestType from .* subclasses the deprecated CustomType class.*",
    ):

        class CustomTestType(CustomType):
            """This class is intended to be inherited by custom types that are used
            purely for the purposes of testing. The methods ``from_tree_tagged`` and
            ``from_tree`` are implemented solely in order to avoid custom type
            conversion warnings.
            """

            @classmethod
            def from_tree_tagged(cls, tree, ctx):
                return cls.from_tree(tree.data, ctx)

            @classmethod
            def from_tree(cls, tree, ctx):
                return tree

    return CustomTestType
