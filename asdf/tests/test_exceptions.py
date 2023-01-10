import pytest

from asdf import exceptions


def test_asdf_provisional_function_default_message():
    @exceptions.asdf_provisional
    def provisional_function(foo, bar=None):
        return (foo, bar)

    with pytest.warns(
        exceptions.AsdfProvisionalAPIWarning, match=r"Function: .* has a Provisional API and is subject to change"
    ):
        assert ("foo", "bar") == provisional_function("foo", bar="bar")


def test_asdf_provisional_class_default_message():
    @exceptions.asdf_provisional
    class ProvisionalClass:
        def __init__(self, foo, bar=None):
            self.foo = foo
            self.bar = bar

    with pytest.warns(
        exceptions.AsdfProvisionalAPIWarning, match=r"Class: .* has a Provisional API and is subject to change"
    ):
        new = ProvisionalClass("foo", bar="bar")
        assert new.foo == "foo"
        assert new.bar == "bar"


def test_asdf_provisional_function_custom_message():
    msg = "This is a custom message"

    @exceptions.asdf_provisional(msg)
    def provisional_function(foo, bar=None):
        return (foo, bar)

    with pytest.warns(exceptions.AsdfProvisionalAPIWarning, match=msg):
        assert ("foo", "bar") == provisional_function("foo", bar="bar")


def test_asdf_provisional_class_custom_message():
    msg = "This is a custom message"

    @exceptions.asdf_provisional(msg)
    class ProvisionalClass:
        def __init__(self, foo, bar=None):
            self.foo = foo
            self.bar = bar

    with pytest.warns(exceptions.AsdfProvisionalAPIWarning, match=msg):
        new = ProvisionalClass("foo", bar="bar")
        assert new.foo == "foo"
        assert new.bar == "bar"


def test_asdf_provisional_error():
    with pytest.raises(TypeError, match=".* is not a valid type for msg."):
        exceptions.asdf_provisional({"foo": "bar"})
