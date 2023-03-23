import io
import string

import numpy

import asdf


tree_sizes = ["small", "flat", "deep", "large"]
data_sizes = ["0", "3x3", "512x512"]


def data_function(size):
    if not size:
        return ord
    dims = [int(d) for d in size.split('x')]
    # assuming double: 2 * 512 * 512 * 26 * 26 = 338M
    return lambda k: numpy.zeros(dims) * ord(k)


def build_tree(size, value_function=None):
    if value_function is None:
        value_function = str
    if isinstance(value_function, str):
        value_function = data_function(value_function)
    if size == "small":
        return {k: value_function(k) for k in string.ascii_lowercase[:3]}
    if size == "flat":
        return {k: value_function(k) for k in string.ascii_lowercase[:26]}
    if size == "deep":
        tree = {}
        for k in string.ascii_lowercase[:26]:
            tree[k] = {'value': value_function(k)}
            tree = tree[k]
        return tree
    if size == "large":
        tree = {}
        for k in string.ascii_lowercase[:26]:
            tree[k] = {k2: value_function(k2) for k2 in string.ascii_lowercase[:26]}
        return tree
    msg = f"Unknown tree size: {size}"
    raise ValueError(msg)


def write_to_bytes(af):
    bs = io.BytesIO()
    with asdf.generic_io.get_file(bs, "w") as f:
        af.write_to(f)
    bs.seek(0)
    return bs


def build_tree_keys():
    return {f"{k}_{dk}" for k in tree_sizes for dk in data_sizes}


def build_trees():
    return {f"{k}_{dk}": build_tree(k, data_function(dk)) for k in tree_sizes for dk in data_sizes}


def build_asdf_files():
    return {k: asdf.AsdfFile(tree) for key, tree in build_trees().items()}


def build_written_asdf_files():
    return {k: write_to_bytes(af) for key, af in build_asdf_files().items()}
