from collections import namedtuple
from pathlib import Path


class FilePropertySet(object):
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

    def __init__(self, default_divisor='b'):
        KB = 1024.0
        MB = KB * 1024.0
        DEFAULT_MEASURE_OPTIONS = {'kb': KB, 'mb': KB * 1024}
        self.ft_list = []
        self.file_properties = namedtuple(
            "file_type_properties", "extension, min_size"
        )
        self.divisor = DEFAULT_MEASURE_OPTIONS.get(default_divisor.lower())
        # add defaults
        file_properties = self.file_properties
        self.add(
            [
                file_properties("png", MB/10),
                file_properties("bmp", MB/10),
                file_properties("gif", MB/10),
                file_properties("jpg", MB/10),
                file_properties("jpeg", MB/10),
                file_properties("pdf", MB/10),
                file_properties("mp3", MB/2),
                file_properties("wav", MB),
                file_properties("aif", MB),
                file_properties("iff", MB),
                file_properties("m3u", 1024),
                file_properties("mpa", MB),
                file_properties("wma", MB),
                file_properties("oog", MB),
                file_properties("flac", MB),
                file_properties("mp4", MB),
                file_properties("mov", 2 * MB),
                file_properties("mpg", 2 * MB),
                file_properties("rm", 2 * MB),
                file_properties("3g2", 2 * MB),
                file_properties("3gp", 2 * MB),
                file_properties("asf", 2 * MB),
                file_properties("avi", 2 * MB),
                file_properties("flv", 2 * MB),
                file_properties("m4v", 2 * MB),
                file_properties("srt", 2 * MB),
                file_properties("swf", 2 * MB),
                file_properties("vob", 2 * MB),
                file_properties("wmv", 2 * MB),
                file_properties("m4v", 2 * MB),
                # file_properties('iso', 100000),
                file_properties('vhd', 1000 * MB),
                # file_properties('vdi', 500000000),
                # file_properties('img', 500000000),
                # file_properties('deb', 500000000),
                # file_properties('msi', 500000000),
                # file_properties('pkg', 500000000),
                # file_properties('app', 500000000),
            ]
        )

    def get_all(self):
        return self.ft_list

    def list_all(self):
        for f in self.ft_list:
            print(f"extension: {f.extension}, minsize: {f.min_size}")

    def clear(self):
        self.ft_list = []

    def add(self, properties):
        """
        """
        if type(properties).__name__ == "list":
            for _ in properties:
                self.ft_list.append(_)
        else:
            self.ft_list.append(properties)

    def add_from_details(self, type_name, type_size=0):
        """add file types from simple input values.  Takes the values
        used in the FilePropertySet.file_properties named tuple, creates
        the 'file_properties' tuple, and passes to the primary 'add' function

        Arguments:
            type_name {string} -- the extension the filetype will need to be
                                  in order for the scanner to find it

        Keyword Arguments:
            type_size {int} -- size in MB that the scan should use as the 
                               minimum. (default: 0)
        """
        if type_name is not None:
            properties = self.file_properties(type_name, type_size)
            self.add(properties)

    def find_extension(self, ext: str):
        """input an extension, or a filename with an extention, and return
        the file type in the property set, with it's min size, if it exists.

        Arguments:
            ext {string} -- a file name 'test.mp3' or an ext 'mp3'

        Returns:
            file_properties {named_tuple} -- a named tuple (extension, min_size)
        """

        result = [
            file_prop
            for file_prop in self.get_all()
            if file_prop.extension == ext.lower().split(".")[-1]
        ]

        # alter the result if there is a divisor present
        if self.divisor:
            if result:
                divided_result = self.file_properties(
                        result[0].extension, result[0].min_size / self.divisor
                        )
                result = [divided_result]
        # should only need the first one in the list, since there should
        # be only one file type in the set
        return (
            result[0] if result else result
        )


    @classmethod
    def check_approved(cls, p :Path):
        """Return true if the path passed is a file with
        and extension in the list, and a size greater 
        or equal to the min size defined in the class
        
        Arguments:
            p {Path} -- A stat-able file path object
        
        Returns:
            [bool] -- true if the file is big enough and matches 
                      an extension
        """
        pstat = p.stat()
        fps = cls()
        fp = fps.find_extension(p.suffix)
        return True if fp and pstat.st_size >= fp.min_size else False
