from os import path

from photo_normalizer.constants import DEFAULT_EXTENSION, FILENAME_FMT, PATHNAME_FMT


class PathPrototype:
    path_elems = ()
    filename = ""

    def __init__(self, filename, root=".", elems=(), fileext=DEFAULT_EXTENSION):
        self.path_elems = elems
        self.filename = filename
        self.fileext = fileext
        self.path_root = root

    def __repr__(self):
        return (
            f"<PathProto ({self.path_root}"
            f"|{','.join(self.path_elems)}"
            f"|{self.filename}{self.fileext})>"
        )

    def __str__(self):
        return path.realpath(path.expandvars(self.root + self.fileext))

    @property
    def root(self):
        return self.dirname + self.filename

    @property
    def dirname(self):
        return path.expanduser(path.join(self.path_root, *self.path_elems, ""))

    @classmethod
    def from_datetime(cls, datetime, elems=(), **kwargs):
        elems += (datetime.strftime(PATHNAME_FMT),)
        filename = datetime.strftime(FILENAME_FMT)
        return cls(filename, elems=elems, **kwargs)

    @property
    def exists(self):
        return path.exists(str(self))

    @property
    def isdir(self):
        return path.isdir(str(self))

    @property
    def isfile(self):
        return path.isfile(str(self))

    def make_unique(self):
        append_count = 0
        filename_base = self.filename
        while self.exists:
            append_count += 1
            self.filename = f"{filename_base}_#{append_count}"
        if append_count > 0:
            return append_count
