class VolumeType(object):
    """Class to help indicated the allowed types of volumes we
    potentially use
    """
    def __init__(self, name='', description='', **kwargs):
        self.name = name
        self.description = description
        if kwargs:
            self._from_kwargs(kwargs)

    @classmethod
    def from_kwargs(cls, name='', description='', **kwargs):
        obj = cls()
        obj.name = name
        obj.description = description
        for (field, value) in kwargs.items():
            setattr(obj, field, value)
        return obj
    
    def _from_kwargs(self, kwargs):
        for (field, value) in kwargs.items():
            setattr(self, field, value)