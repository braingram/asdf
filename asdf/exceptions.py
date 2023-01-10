import functools
import inspect
import warnings


class AsdfWarning(Warning):
    """
    The base warning class from which all ASDF warnings should inherit.
    """


class AsdfDeprecationWarning(AsdfWarning, DeprecationWarning):
    """
    A warning class to indicate a deprecated feature.
    """


class AsdfConversionWarning(AsdfWarning):
    """
    Warning class used for failures to convert data into custom types.
    """


class DelimiterNotFoundError(ValueError):
    """
    Indicates that a delimiter was not found when reading or
    seeking through a file.
    """


class AsdfProvisionalAPIWarning(AsdfWarning, FutureWarning):
    """
    Used for provisional features where breaking API changes might be
    introduced at any point (including minor releases). These features
    are likely to be added in a future ASDF version. However, Use of
    provisional features is highly discouraged for production code.
    """


def asdf_provisional(msg):
    """
    Mark a function as provisional.

    Parameters
    ----------
    msg: str
        The warning message to display. If not provided, a default
    """

    if isinstance(msg, (bytes, str)):

        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                warnings.warn(msg, AsdfProvisionalAPIWarning)
                return func(*args, **kwargs)

            return wrapper

        return decorator

    elif inspect.isclass(msg) or inspect.isfunction(msg):
        func = msg
        msg = f"{func.__name__} has a Provisional API and is subject to change"

        if inspect.isclass(func):
            msg = f"Class: {msg}"
        else:
            msg = f"Function: {msg}"

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            warnings.warn(msg, AsdfProvisionalAPIWarning)
            return func(*args, **kwargs)

        return wrapper

    raise TypeError(f"{type(msg)!r} is not a valid type for msg.")
