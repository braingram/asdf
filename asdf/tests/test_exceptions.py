import pytest

from asdf import exceptions


def test_asdf_provisional_function_default_message():
    @exceptions.provisional
    def provisional_function(foo, bar=None):
        return (foo, bar)

    with pytest.warns(
        exceptions.AsdfProvisionalAPIWarning, match=r"Function: .* has a Provisional API and is subject to change"
    ):
        assert ("foo", "bar") == provisional_function("foo", bar="bar")


def test_asdf_provisional_class_default_message():
    @exceptions.provisional
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

    @exceptions.provisional(msg)
    def provisional_function(foo, bar=None):
        return (foo, bar)

    with pytest.warns(exceptions.AsdfProvisionalAPIWarning, match=msg):
        assert ("foo", "bar") == provisional_function("foo", bar="bar")


def test_asdf_provisional_class_custom_message():
    msg = "This is a custom message"

    @exceptions.provisional(msg)
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
        exceptions.provisional({"foo": "bar"})


def test_asdf_provisional_attribute_default_message():
    class ProvisionalClass:
        foo = exceptions.provisional_attribute("foo")

    new = ProvisionalClass()

    with pytest.warns(
        exceptions.AsdfProvisionalAPIWarning,
        match=r"Setting: foo is Provisional attribute, the API and is subject to change!",
    ):
        new.foo = "bar"
        assert new._foo == "bar"

    with pytest.warns(
        exceptions.AsdfProvisionalAPIWarning,
        match=r"Getting: foo is Provisional attribute, the API and is subject to change!",
    ):
        assert new.foo == "bar"

    with pytest.warns(
        exceptions.AsdfProvisionalAPIWarning,
        match=r"Deleting: foo is Provisional attribute, the API and is subject to change!",
    ):
        del new.foo

        assert not hasattr(new, "_foo")


def test_asdf_provisional_attribute_custom():
    msg = "This is a custom message"

    class ProvisionalClass:
        foo = exceptions.provisional_attribute("foo", alt_name="bar", msg=msg)

    new = ProvisionalClass()

    with pytest.warns(exceptions.AsdfProvisionalAPIWarning, match=f"Setting: {msg}"):
        new.foo = "bar"
        assert new.bar == "bar"

    with pytest.warns(exceptions.AsdfProvisionalAPIWarning, match=f"Getting: {msg}"):
        assert new.foo == "bar"

    with pytest.warns(exceptions.AsdfProvisionalAPIWarning, match=f"Deleting: {msg}"):
        del new.foo

        assert not hasattr(new, "bar")


def test_asdf_provisional_argument_default_message():
    @exceptions.provisional_argument("bar")
    def func1(foo, bar=None):
        return (foo, bar)

    with pytest.warns(
        exceptions.AsdfProvisionalAPIWarning, match=r"bar is a Provisional argument, the API and is subject to change!"
    ):
        assert ("foo", "bar") == func1("foo", "bar")

    with pytest.warns(
        exceptions.AsdfProvisionalAPIWarning, match=r"bar is a Provisional argument, the API and is subject to change!"
    ):
        assert ("foo", "bar") == func1("foo", bar="bar")

    with pytest.warns(
        exceptions.AsdfProvisionalAPIWarning, match=r"bar is a Provisional argument, the API and is subject to change!"
    ):
        assert ("foo", "bar") == func1(foo="foo", bar="bar")

    @exceptions.provisional_argument("foo")
    def func2(foo, bar=None):
        return (foo, bar)

    with pytest.warns(
        exceptions.AsdfProvisionalAPIWarning, match=r"foo is a Provisional argument, the API and is subject to change!"
    ):
        assert ("foo", "bar") == func2("foo", "bar")

    with pytest.warns(
        exceptions.AsdfProvisionalAPIWarning, match=r"foo is a Provisional argument, the API and is subject to change!"
    ):
        assert ("foo", "bar") == func2("foo", bar="bar")

    with pytest.warns(
        exceptions.AsdfProvisionalAPIWarning, match=r"foo is a Provisional argument, the API and is subject to change!"
    ):
        assert ("foo", "bar") == func2(foo="foo", bar="bar")


def test_asdf_provisional_argument_custom_message():
    msg = "This is a custom message"

    @exceptions.provisional_argument("bar", msg)
    def func1(foo, bar=None):
        return (foo, bar)

    with pytest.warns(exceptions.AsdfProvisionalAPIWarning, match=msg):
        assert ("foo", "bar") == func1("foo", "bar")

    with pytest.warns(exceptions.AsdfProvisionalAPIWarning, match=msg):
        assert ("foo", "bar") == func1("foo", bar="bar")

    with pytest.warns(exceptions.AsdfProvisionalAPIWarning, match=msg):
        assert ("foo", "bar") == func1(foo="foo", bar="bar")

    @exceptions.provisional_argument("foo", msg)
    def func2(foo, bar=None):
        return (foo, bar)

    with pytest.warns(exceptions.AsdfProvisionalAPIWarning, match=msg):
        assert ("foo", "bar") == func2("foo", "bar")

    with pytest.warns(exceptions.AsdfProvisionalAPIWarning, match=msg):
        assert ("foo", "bar") == func2("foo", bar="bar")

    with pytest.warns(exceptions.AsdfProvisionalAPIWarning, match=msg):
        assert ("foo", "bar") == func2(foo="foo", bar="bar")


def test_asdf_provisional_argument_error():
    with pytest.raises(ValueError, match=r".* is not a valid argument for .*."):

        @exceptions.provisional_argument("baz")
        def func(foo, bar=None):
            return (foo, bar)