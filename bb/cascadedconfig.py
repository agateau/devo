class CascadedConfig(object):
    """
    Provide a dict-like object working on a stack of dicts
    """
    def __init__(self, *args):
        self._dicts = args

    def get(self, key, default=None):
        """
        Returns value for key, trying all dicts from the stack
        """
        for dct in self._dicts:
            try:
                return dct[key]
            except KeyError:
                pass
        return default

    def flat_get(self, key, default=None):
        """
        Returns value for key from the top-most dict only
        """
        return self._dicts[0].get(key, default)
