import os
import tempfile


def is_fs_case_sensitive():
    """Return true if current system is case sensitive
    """
    #
    # Force case with the prefix
    # coppied from https://stackoverflow.com/a/36580834
    #
    with tempfile.NamedTemporaryFile(prefix="TmP") as tmp_file:
        return not os.path.exists(tmp_file.name.lower())
