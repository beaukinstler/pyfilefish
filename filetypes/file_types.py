from collections import namedtuple


class FileProperySet(object):
    """
    A list of file types and their min size for relevance
    in searching and storing.  
    Intended to be used for potentially deciding on 
    whether a file is needed based on the type, and the 
    size that is relevant for that type

    output: a list of named tuples with 'extention' and 'min_size'

    use 
        x = FilePropertySet()
        x.list_all() -- shows all predefined types
        x.add('extension', <min_size>) -- create a new one
        x.clear() -- delete all predefined types
    """


    def __init__(self): #, file_type_properties=[PNG, ISO, JPG]):
        self.ft_list = []
        self.file_properties = namedtuple('file_type_properties', 'extension, min_size')
        
        # add defaults
        file_properties = self.file_properties
        self.add([
            file_properties('png', 500000),
            file_properties('iso', 50000000),
            file_properties('bmp', 500000),
            file_properties('gif', 500000),
            file_properties('jpg', 500000),
            file_properties('jpeg', 500000),
            file_properties('mp3', 500000),
            file_properties('wav', 5000000),
            file_properties('mp4', 5000000),
            file_properties('vhd', 50000000),
            file_properties('vdi', 50000000),
            file_properties('img', 50000000),
            file_properties('deb', 50000000),
            file_properties('msi', 50000000),
            file_properties('pkg', 50000000),
            file_properties('app', 50000000),
        ])
    
    def get_all(self):
        return self.ft_list

    def list_all(self):
        for f in self.ft_list:
            print(f"extention: {f.extension}, minsize: {f.min_size}")
    
    def clear(self):
        self.ft_list = []

    def add(self, properties):
        """
        """
        if type(properties).__name__ == 'list':
            for _ in properties:
                self.ft_list.append(_)
        else:
            self.ft_list.append(properties)
        