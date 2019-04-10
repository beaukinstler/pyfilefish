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
            file_properties('png', 100),
            file_properties('bmp', 100),
            file_properties('gif', 100),
            file_properties('jpg', 100),
            file_properties('jpeg', 100),


            file_properties('mp3', 100),
            file_properties('wav', 10000),
            file_properties('aif', 1000),
            file_properties('iff', 1000),
            file_properties('m3u', 1024),
            file_properties('mpa', 1000),
            file_properties('m4a', 1000),
            file_properties('wma', 1000),
            file_properties('oog', 1000),
            file_properties('flac', 1000),
            
            file_properties('mp4', 1000),
            file_properties('mov', 1000),
            file_properties('mpg', 1000),
            file_properties('rm', 1000),
            file_properties('3g2', 1000),
            file_properties('3gp', 1000),
            file_properties('asf', 1000),
            file_properties('avi', 1000),
            file_properties('flv', 1000),
            file_properties('m4v', 1000),
            file_properties('srt', 1000),
            file_properties('swf', 1000),
            file_properties('vob', 1000),
            file_properties('wmv', 1000),
            
            file_properties('m4v', 1000),

            # file_properties('iso', 100000),
            # file_properties('vhd', 500000000),
            # file_properties('vdi', 500000000),
            # file_properties('img', 500000000),
            # file_properties('deb', 500000000),
            # file_properties('msi', 500000000),
            # file_properties('pkg', 500000000),
            # file_properties('app', 500000000),

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
        