import enum

from asdf._block.key import Key as BlockKey
from asdf._helpers import validate_version
from asdf.extension._extension import ExtensionProxy


class SerializationContext:
    """
    Container for parameters of the current (de)serialization.

    This class should not be instantiated directly and instead
    will be created by the AsdfFile object and provided to extension
    classes (like Converters) via method arguments.
    """

    def __init__(self, version, extension_manager, url, blocks):
        self._version = validate_version(version)
        self._extension_manager = extension_manager
        self._url = url
        self._blocks = blocks
        self._obj = None

        self.__extensions_used = set()

    @property
    def url(self):
        """
        The URL (if any) of the file being read or written.

        Used to compute relative locations of external files referenced by this
        ASDF file. The URL will not exist in some cases (e.g. when the file is
        written to an `io.BytesIO`).

        Returns
        -------
        str or None
        """
        return self._url

    @property
    def version(self):
        """
        Get the ASDF Standard version.

        Returns
        -------
        str
        """
        return self._version

    @property
    def extension_manager(self):
        """
        Get the ExtensionManager for enabled extensions.

        Returns
        -------
        asdf.extension.ExtensionManager
        """
        return self._extension_manager

    def _mark_extension_used(self, extension):
        """
        Note that an extension was used when reading or writing the file.

        Parameters
        ----------
        extension : asdf.extension.Extension
        """
        self.__extensions_used.add(ExtensionProxy.maybe_wrap(extension))

    @property
    def _extensions_used(self):
        """
        Get the set of extensions that were used when reading or writing the file.

        Returns
        -------
        set of asdf.extension.Extension
        """
        return self.__extensions_used

    def get_block_data_callback(self, index, key=None):
        """
        Generate a callable that when called will read data
        from an ASDF block at the provided index.

        Parameters
        ----------
        index : int
            Index of ASDF block.

        key : BlockKey, optional
            BlockKey generated using self.generate_block_key. Only
            needed for a Converter that uses multiple blocks.

        Returns
        -------
        callback : callable
            A callable that when called (with no arguments) returns
            the block data as a one dimensional array of uint8
        """
        raise NotImplementedError("abstract")

    def find_available_block_index(self, data_callback, key=None):
        """
        Find the index of an available ASDF block to write data.

        This is typically used inside asdf.extension.Converter.to_yaml_tree.

        Parameters
        ----------
        data_callback: callable
            Callable that when called will return data (ndarray) that will
            be written to a block.

        key : BlockKey, optional
            BlockKey generated using self.generate_block_key. Only
            needed for a Converter that uses multiple blocks.

        Returns
        -------
        block_index: int
            Index of the ASDF block where data returned from
            data_callback will be written.
        """
        raise NotImplementedError("abstract")

    def generate_block_key(self):
        """
        Generate a BlockKey used for Converters that wish to use
        multiple blocks

        Returns
        -------
        key : BlockKey
            A hashable object that will be associated with the
            serialized/deserialized object and can be used to
            access multiple blocks within a Converter
        """
        raise NotImplementedError("abstract")

    def assign_object(self, obj):
        self._obj = obj

    def assign_blocks(self):
        pass


class ReadBlocksContext(SerializationContext):
    """
    Perform deserialization (reading) with a `SerializationContext`.

    To allow for block access, `ReadBlocksContext` implements:
        - `SerializationContext.generate_block_key`
        - `SerializationContext.get_block_data_callback`
    and tracks which blocks (and keys) are accessed, assigning them
    to the deserialized object after `assign_object` and
    `assign_blocks` are called.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.assign_object(None)

    def assign_object(self, obj):
        super().assign_object(obj)
        if obj is None:
            self._cb = None
            self._keys_to_assign = {}

    def assign_blocks(self):
        super().assign_blocks()
        if self._cb is not None:
            self._blocks._data_callbacks.assign_object(self._obj, self._cb)
        for key, cb in self._keys_to_assign.items():
            if cb is None:
                msg = "Converter generated a key that was never used"
                raise OSError(msg)
            # now that we have an object, make the key valid
            key._assign_object(self._obj)

            # assign the key to the callback
            self._blocks._data_callbacks.assign_object(key, cb)
        # now that we've assigned blocks, remove the reference to the
        # assigned object
        self.assign_object(None)

    def get_block_data_callback(self, index, key=None):
        if key is None:
            if self._cb is not None:
                # this operation has already accessed a block without using
                # a key so check if the same index was accessed
                if self._cb._index == index:
                    return self._cb
                msg = "Converters accessing >1 block must provide a key for each block"
                raise OSError(msg)
            self._cb = self._blocks._get_data_callback(index)
            return self._cb

        if self._keys_to_assign.get(key, None) is not None:
            return self._keys_to_assign[key]

        cb = self._blocks._get_data_callback(index)
        # mark this as a key to later assign
        self._keys_to_assign[key] = cb
        return cb

    def generate_block_key(self):
        key = BlockKey()
        self._keys_to_assign[key] = None
        return key


class WriteBlocksContext(SerializationContext):
    """
    Perform serialization (writing) with a `SerializationContext`.

    To allow for block access, `WriteBlocksContext` implements:
        - `SerializationContext.generate_block_key`
        - `SerializationContext.find_available_block_index`
    and assigns any accessed blocks (and keys) to the object
    being serialized.
    """

    def find_available_block_index(self, data_callback, key=None):
        if key is None:
            key = self._obj
        return self._blocks.make_write_block(data_callback, None, key)

    def generate_block_key(self):
        return BlockKey(self._obj)


class BlockAccess(enum.Enum):
    """
    Block access enumerated values that define
    how a SerializationContext can access ASDF blocks.
    """

    NONE = SerializationContext
    WRITE = WriteBlocksContext
    READ = ReadBlocksContext


def create(asdf_file, block_access=BlockAccess.NONE):
    """
    Create a SerializationContext instance (or subclass) using
    an AsdfFile instance, asdf_file.

    Parameters
    ----------
    asdf_file : asdf.AsdfFile

    block_access : BlockAccess, optional
        Defaults to BlockAccess.NONE
    """
    return block_access.value(asdf_file.version_string, asdf_file.extension_manager, asdf_file.uri, asdf_file._blocks)
