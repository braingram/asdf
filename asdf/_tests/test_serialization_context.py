import numpy as np
import pytest

import asdf
from asdf import get_config
from asdf._serialization_context import SerializationContext
from asdf.extension import ExtensionManager


def test_serialization_context():
    extension_manager = ExtensionManager([])
    context = SerializationContext("1.4.0", extension_manager, "file://test.asdf", None)
    assert context.version == "1.4.0"
    assert context.extension_manager is extension_manager
    assert context._extensions_used == set()

    extension = get_config().extensions[0]
    context._mark_extension_used(extension)
    assert context._extensions_used == {extension}
    context._mark_extension_used(extension)
    assert context._extensions_used == {extension}
    context._mark_extension_used(extension.delegate)
    assert context._extensions_used == {extension}

    assert context.url == context._url == "file://test.asdf"

    with pytest.raises(TypeError, match=r"Extension must implement the Extension interface"):
        context._mark_extension_used(object())

    with pytest.raises(ValueError, match=r"ASDF Standard version .* is not supported by asdf==.*"):
        SerializationContext("0.5.4", extension_manager, None, None)


@pytest.mark.parametrize("operation", ["_deserialization", "_serialization"])
def test_extension_used_in_operation(operation):
    extension_manager = ExtensionManager([])
    context = SerializationContext("1.4.0", extension_manager, "file://test.asdf", None)

    if operation == "_serialization":
        args = [object()]
    else:
        args = []
    extension = get_config().extensions[0]
    with getattr(context, operation)(*args) as op_ctx:
        op_ctx._mark_extension_used(extension)
        assert extension in op_ctx._extensions_used
    # check this persists in the parent context
    assert extension in context._extensions_used


def test_get_block_data_callback(tmp_path):
    fn = tmp_path / "test.asdf"

    # make a file with 2 blocks
    arr0 = np.arange(3, dtype="uint8")
    arr1 = np.arange(10, dtype="uint8")
    asdf.AsdfFile({"arr0": arr0, "arr1": arr1}).write_to(fn)

    with asdf.open(fn) as af:
        context = af._create_serialization_context()
        with pytest.raises(NotImplementedError, match="abstract"):
            context.get_block_data_callback(0)

        with context._deserialization() as op_ctx:
            cb0 = op_ctx.get_block_data_callback(0)

            # getting the same callback should pass and return the same object
            assert op_ctx.get_block_data_callback(0) is cb0

            # since we accessed block 0 we shouldn't be allowed to access block 1
            with pytest.raises(OSError, match=r"Converters accessing >1.*"):
                op_ctx.get_block_data_callback(1)

            # unless we use a key
            key = op_ctx.generate_block_key()
            cb1 = op_ctx.get_block_data_callback(1, key)
            assert op_ctx.get_block_data_callback(1, key) is cb1

            # we don't know the order of blocks, so find which block
            # was used for which array by looking at the size
            d0 = cb0()
            d1 = cb1()
            if d0.size == arr1.size:
                arr0, arr1 = arr1, arr0
            np.testing.assert_array_equal(d0, arr0)
            np.testing.assert_array_equal(d1, arr1)

            class Foo:
                pass

            # assign a deserialized object as we accessed blocks and the context
            # will expect this object to be available
            op_ctx._obj = Foo()

        with context._serialization(object()) as op_ctx:
            with pytest.raises(NotImplementedError, match="abstract"):
                op_ctx.get_block_data_callback(0)


def test_find_available_block_index():
    af = asdf.AsdfFile()
    context = af._create_serialization_context()

    def cb():
        return np.arange(3, dtype="uint8")

    with pytest.raises(NotImplementedError, match="abstract"):
        context.find_available_block_index(cb)

    class Foo:
        pass

    with context._serialization(Foo()) as op_ctx:
        assert op_ctx.find_available_block_index(cb) == 0

    with context._deserialization() as op_ctx:
        with pytest.raises(NotImplementedError, match="abstract"):
            op_ctx.find_available_block_index(cb)


def test_generate_block_key():
    af = asdf.AsdfFile()
    context = af._create_serialization_context()

    with pytest.raises(NotImplementedError, match="abstract"):
        context.generate_block_key()

    class Foo:
        pass

    obj = Foo()
    with context._serialization(obj) as op_ctx:
        key = op_ctx.generate_block_key()
        assert key.is_valid()
        assert key.matches_object(obj)

    obj = Foo()
    with context._deserialization() as op_ctx:
        key = op_ctx.generate_block_key()
        # the key does not yet have an assigned object
        assert not key.is_valid()
        op_ctx._obj = obj
    assert key.is_valid()
    assert key.matches_object(obj)
