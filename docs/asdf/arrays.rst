.. currentmodule:: asdf

**********
Array Data
**********


Saving arrays
=============

Beyond the basic data types of dictionaries, lists, strings and numbers, the
most important thing ASDF can save is arrays.  It's as simple as putting a
:mod:`numpy` array somewhere in the tree.  Here, we save an 8x8 array of random
floating-point numbers (using `numpy.random.rand`).  Note that the resulting
YAML output contains information about the structure (size and data type) of
the array, but the actual array content is in a binary block.

.. runcode::

   from asdf import AsdfFile
   import numpy as np

   tree = {'my_array': np.random.rand(8, 8)}
   ff = AsdfFile(tree)
   ff.write_to("array.asdf")

.. note::

   In the file examples below, the first YAML part appears as it
   appears in the file.  The ``BLOCK`` sections are stored as binary
   data in the file, but are presented in human-readable form on this
   page.


.. asdf:: array.asdf

See :ref:`overview_reading` for a description of how to open this file.


Sharing of data
===============

Arrays that are views on the same data automatically share the same
data in the file.  In this example an array and a subview on that same
array are saved to the same file, resulting in only a single block of
data being saved.

.. runcode::

   from asdf import AsdfFile
   import numpy as np

   my_array = np.random.rand(8, 8)
   subset = my_array[2:4,3:6]
   tree = {
       'my_array': my_array,
       'subset':   subset
   }
   ff = AsdfFile(tree)
   ff.write_to("array_with_subset.asdf")

For circumstances where this is undesirable (such as saving
a small view of a large array) this can be disabled by setting
`asdf.config.AsdfConfig.default_array_save_base` (to set the default behavior)
or `asdf.AsdfFile.set_array_save_base` to control the behavior for
a specific array.

.. asdf:: array_with_subset.asdf

Saving inline arrays
====================

For small arrays, you may not care about the efficiency of a binary
representation and just want to save the array contents directly in the YAML
tree.  The `~asdf.AsdfFile.set_array_storage` method can be used to set the
storage type of the associated data. The allowed values are ``internal``,
``external``, and ``inline``.

- ``internal``: The default.  The array data will be
  stored in a binary block in the same ASDF file.

- ``external``: Store the data in a binary block in a separate ASDF file (also
  known as "exploded" format, which discussed below in :ref:`exploded`).

- ``inline``: Store the data as YAML inline in the tree.

.. runcode::

   from asdf import AsdfFile
   import numpy as np

   my_array = np.random.rand(8, 8)
   tree = {'my_array': my_array}
   ff = AsdfFile(tree)
   ff.set_array_storage(my_array, 'inline')
   ff.write_to("inline_array.asdf")

.. asdf:: inline_array.asdf

Alternatively, it is possible to use the ``all_array_storage`` parameter of
`AsdfFile.write_to` and `AsdfFile.update` to control the storage
format of all arrays in the file.

.. code::

    # This controls the output format of all arrays in the file
    ff.write_to("all_inline.asdf", all_array_storage='inline')

For automatic management of the array storage type based on number of elements,
see :ref:`config_options_array_inline_threshold`.

.. _exploded:

Saving external arrays
======================

ASDF files may also be saved in "exploded form", which creates multiple files
corresponding to the following data items:

- One ASDF file containing only the header and tree.

- *n* ASDF files, each containing a single array data block.

Exploded form is useful in the following scenarios:

- Over a network protocol, such as HTTP, a client may only need to
  access some of the blocks.  While reading a subset of the file can
  be done using HTTP ``Range`` headers, it still requires one (small)
  request per block to "jump" through the file to determine the start
  location of each block.  This can become time-consuming over a
  high-latency network if there are many blocks.  Exploded form allows
  each block to be requested directly by a specific URI.

- An ASDF writer may stream a table to disk, when the size of the table
  is not known at the outset.  Using exploded form simplifies this,
  since a standalone file containing a single table can be iteratively
  appended to without worrying about any blocks that may follow it.

To save a block in an external file, set its block type to
``'external'``.

.. runcode::

   from asdf import AsdfFile
   import numpy as np

   my_array = np.random.rand(8, 8)
   tree = {'my_array': my_array}
   ff = AsdfFile(tree)

   # On an individual block basis:
   ff.set_array_storage(my_array, 'external')
   ff.write_to("external.asdf")

   # Or for every block:
   ff.write_to("external.asdf", all_array_storage='external')

.. asdf:: external.asdf

.. asdf:: external0000.asdf

Streaming array data
====================

In certain scenarios, you may want to stream data to disk, rather than
writing an entire array of data at once.  For example, it may not be
possible to fit the entire array in memory, or you may want to save
data from a device as it comes in to prevent data loss.  The ASDF
Standard allows exactly one streaming block per file where the size of
the block isn't included in the block header, but instead is
implicitly determined to include all of the remaining contents of the
file.  By definition, it must be the last block in the file.

To use streaming, rather than including a Numpy array object in the
tree, you include a `asdf.tags.core.Stream` object which sets up the structure
of the streamed data, but will not write out the actual content.  The
file handle's ``write`` method is then used to manually write out the
binary data.

.. runcode::

   from asdf import AsdfFile
   from asdf.tags.core import Stream
   import numpy as np

   tree = {
       # Each "row" of data will have 128 entries.
       'my_stream': Stream([128], np.float64)
   }

   ff = AsdfFile(tree)
   with open('stream.asdf', 'wb') as fd:
       ff.write_to(fd)
       # Write 100 rows of data, one row at a time.  ``write``
       # expects the raw binary bytes, not an array, so we use
       # ``tobytes()``.
       for i in range(100):
           fd.write(np.array([i] * 128, np.float64).tobytes())

.. asdf:: stream.asdf

When reading a file with a streamed block the streamed block will
be treated as a normal non-streamed block. It may be useful to enable
:ref:`memory_mapping` if the corresponding block is too large to hold in memory.

A case where streaming may be useful is when converting large data sets from a
different format into ASDF. In these cases it would be impractical to hold all
of the data in memory as an intermediate step. Consider the following example
that streams a large CSV file containing rows of integer data and converts it
to numpy arrays stored in ASDF:

.. doctest-skip::

    import csv
    import numpy as np
    from asdf import AsdfFile
    from asdf.tags.core import Stream

    tree = {
        # We happen to know in advance that each row in the CSV has 100 ints
        'data': Stream([100], np.int64)
    }

    ff = AsdfFile(tree)
    # open the output file handle
    with open('new_file.asdf', 'wb') as fd:
        ff.write_to(fd)
        # open the CSV file to be converted
        with open('large_file.csv', 'r') as cfd:
            # read each line of the CSV file
            reader = csv.reader(cfd)
            for row in reader:
                # convert each row to a numpy array
                array = np.array([int(x) for x in row], np.int64)
                # write the array to the output file handle
                fd.write(array.tobytes())

Compression
===========

Individual blocks in an ASDF file may be compressed.

`zlib <http://www.zlib.net/>`__ and `bzip2 <http://www.bzip.org>`__
are included in every asdf install. Passing one of these 4 character
codes as ``all_array_compression`` to `asdf.AsdfFile.write_to` will
compress all blocks with the corresponding algorithm.:

.. runcode::

   from asdf import AsdfFile
   import numpy as np

   tree = {
       'a': np.random.rand(32, 32),
       'b': np.random.rand(64, 64)
   }

   target = AsdfFile(tree)
   target.write_to('target.asdf', all_array_compression='zlib')
   target.write_to('target.asdf', all_array_compression='bzp2')

.. asdf:: target.asdf

The `lz4 <https://en.wikipedia.org/wiki/LZ_4>`__ compression algorithm is also
supported, but requires the optional
`lz4 <https://python-lz4.readthedocs.io/>`__ package in order to work.

Similarly, `asdf.config` can be used to configure compression of all
blocks by setting `asdf.config.AsdfConfig.all_array_compression`.

`asdf.AsdfFile.set_array_compression` can be used to set the compression
for a specific block. Similarly `asdf.AsdfFile.get_array_compression` can
be used to get the compression for a specific block.

.. code:: python

   import asdf
   import numpy as np

   af = asdf.AsdfFile({"arr": np.arange(42)})
   af.set_array_compression(af["arr"], "lz4")
   assert af.get_array_compression(af["arr"]) == "lz4"

When reading a file with compressed blocks, the blocks will be automatically
decompressed when accessed. If a file with compressed blocks is read and then
written out again, by default the new file will use the same compression as the
original file. This behavior can be overridden by explicitly providing a
different compression algorithm when writing the file out again.

.. code::

    import asdf

    # Open a file with some compression
    af = asdf.open('compressed.asdf')

    # Use the same compression when writing out a new file
    af.write_to('same.asdf')

    # Or specify the (possibly different) algorithm to use when writing out
    af.write_to('different.asdf', all_array_compression='lz4')

.. _memory_mapping:

Memory mapping
==============

When enabled, array data can be memory mapped using `numpy.memmap`. This
allows for the efficient use of memory even when reading files with very large
arrays. When memory mapping is enabled array data access must occur while
the corresponding file is open. This is most easily done using a ``with``
context.

.. code::

    import asdf

    with asdf.open('my_data.asdf', memmap=True) as af:
        # array data can be accessed since the with above
        # will keep my_data.asdf open
        print(af["my_array"][0])

Attempting to access memory mapped array data after the corresponding
file has been closed will result in an error.

.. warning::

   If a file is opened with memory mapping and write access
   any changes to the array data will change the corresponding file.
