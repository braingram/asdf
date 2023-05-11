import weakref


class UndefinedRef:
    pass


class Key:
    _next = 0

    @classmethod
    def _next_key(cls):
        key = cls._next
        cls._next += 1
        return key

    def __init__(self, obj=None, key=None):
        if key is None:
            key = Key._next_key()
        self._key = key
        self._ref = UndefinedRef
        if obj is not None:
            self.assign_object(obj)

    def is_valid(self):
        if self._ref is UndefinedRef:
            return False
        r = self._ref()
        if r is None:
            return False
        return True

    def __hash__(self):
        return self._key

    def assign_object(self, obj):
        self._ref = weakref.ref(obj)

    def matches_object(self, obj):
        if self._ref is UndefinedRef:
            return False
        r = self._ref()
        if r is None:
            return False
        return r is obj

    def __eq__(self, other):
        if not isinstance(other, Key):
            return NotImplemented
        if self._key != other._key:
            return False
        if not self.is_valid():
            return False
        return other.matches_object(self._ref())

    def __copy__(self):
        return self.__class__(self._ref(), self._key)
