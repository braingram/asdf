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


def asdf_provisional_attribute(name, alt_name=None, msg=None):
    """
    Used to mark a public attribute as provisional.

    Parameters
    ----------
    name: str
        The name of the attribute.

    alt_name: str, optional
        An alternative name for the attribute. If not provided, the default is
        will prepend an underscore to the attribute name.

    message: str, optional
        The warning message to display. If not provided, a default
        message will be used.
    """

    private_name = f"_{name}" if alt_name is None else alt_name
    msg = f"{name} is Provisional attribute, the API and is subject to change!" if msg is None else msg

    def provisional_getter(self):
        warnings.warn(f"Getting: {msg}", AsdfProvisionalAPIWarning)

        return getattr(self, private_name)

    def provisional_setter(self, value):
        warnings.warn(f"Setting: {msg}", AsdfProvisionalAPIWarning)

        setattr(self, private_name, value)

    def provisional_deleter(self):
        warnings.warn(f"Deleting: {msg}", AsdfProvisionalAPIWarning)

        delattr(self, private_name)

    return property(provisional_getter, provisional_setter, provisional_deleter)


def asdf_provisional_argument(name, msg=None):
    """
    Used to mark a public, optional argument as provisional.

    Parameters
    ----------
    name: str
        The name of the argument.

    message: str, optional
        The warning message to display. If not provided, a default
        message will be used.
    """

    msg = f"{name} is a Provisional argument, the API and is subject to change!" if msg is None else msg

    def decorator(func):
        sig = inspect.signature(func)
        if name in sig.parameters:
            index = list(sig.parameters).index(name)

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                if name in kwargs or len(args) > index:
                    warnings.warn(msg, AsdfProvisionalAPIWarning)

                return func(*args, **kwargs)

            return wrapper
        else:
            raise ValueError(f"{name} is not a valid argument for {func.__name__}.")

    return decorator
