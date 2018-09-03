class Singleton(object):

    @classmethod
    def instance(cls, *args, **kwargs):
        try:
            return cls.__initialized
        except AttributeError:
            pass
        cls.__initialized = self = cls(*args, **kwargs)
        return self

    @classmethod
    def initialized(cls, default=None):
        try:
            return cls.__initialized
        except AttributeError:
            return default
