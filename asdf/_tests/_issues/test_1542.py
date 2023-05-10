import os

import numpy as np

import asdf


def test_1542():
    """
    ASDF fails to write blocks to non-seekable file

    https://github.com/asdf-format/asdf/issues/1542
    """
    r, w = os.pipe()
    with os.fdopen(r, "rb") as rf:
        with os.fdopen(w, "wb") as wf:
            arrs = [np.zeros(1, dtype="uint8") + i for i in range(10)]
            af = asdf.AsdfFile({"arrs": arrs})
            af.write_to(wf)
        with asdf.open(rf) as raf:
            for a, ra in zip(arrs, raf["arrs"]):
                np.testing.assert_array_equal(a, ra)