import logging
from datetime import datetime
from glob import iglob
from os import makedirs, path
from shutil import move

import piexif
from dateutil.parser import parse as dateparse

from photo_normalizer.path import PathPrototype
from photo_normalizer.constants import JPEG_EXTENSIONS

append_counter = True

logger = logging.getLogger(__name__)


class Normalizer:

    default_subdir = "Normalized"
    duplicates_subdir = "Duplicates"
    nometa_subdir = "NoMetadata"
    nojpeg_subdir = "NoJpeg"

    search_recursive = True
    dryrun = False

    def __init__(self, input_dir, output_dir):
        input_dir = path.realpath(path.expanduser(path.expandvars(input_dir)))

        if not path.isdir(input_dir):
            raise ValueError("Input directory must exist")

        self.input_dir = input_dir
        self.search_glob = path.join(self.input_dir, "**", "*")
        self.output_dir = output_dir

    def prepare_paths(self):
        self.path_default = path.join(self.output_dir, self.default_subdir, "")
        self.path_nometa = path.join(self.output_dir, self.nometa_subdir, "")
        self.path_nojpg = path.join(self.output_dir, self.nojpeg_subdir, "")
        self.path_duplicates = path.join(self.output_dir, self.duplicates_subdir, "")

    def run(self):
        self.prepare_paths()

        def is_skippable(file):
            return (
                file.startswith(self.path_nometa)
                or file.startswith(self.path_nojpg)
                or file.startswith(self.path_duplicates)
                or path.isdir(file)
            )

        [
            self.process_file(f)
            for f in iglob(self.search_glob, recursive=self.search_recursive)
            if not is_skippable(f)
        ]
        logger.info("Done.")

    def check_for_nojpeg(self, file):
        lower_ext = path.splitext(file)[1].lower()
        if lower_ext not in JPEG_EXTENSIONS:
            logger.info(f"Found non-JPEG file {file}")
            return PathPrototype(
                path.basename(file), root=self.path_nojpg, fileext=lower_ext
            )

    def check_for_exifdate(self, file):
        # Extract date from EXIF data, if not possible rename file by hash?
        exif_data = piexif.load(file)
        exif_date = exif_data["Exif"].get(piexif.ExifIFD.DateTimeOriginal)

        if exif_date:
            exif_date = datetime.strptime(
                exif_date.decode("utf-8"), "%Y:%m:%d %H:%M:%S"
            )
            return PathPrototype.from_datetime(exif_date, root=self.path_default)

    def check_for_filename_date(self, file):
        try:
            file_date = dateparse(file)
            return PathPrototype.from_datetime(file_date, root=self.path_default)
        except ValueError:
            return

    def process_file(self, file):
        try:
            logger.debug("Checking for non-JPEG data")
            target = self.check_for_nojpeg(file)

            if not target:
                logger.debug("Checking for EXIF date")
                target = self.check_for_exifdate(file)

            if not target:
                logger.debug("Checking for filename date")
                target = self.check_for_filename_date(file)

            if target:
                logger.debug("Checking for duplicate target file")
                counter = target.make_unique()
                if counter:
                    logger.info(f"Duplicate counter: {counter}")

                self.move_file(file, target)
            else:
                raise Exception("All checks failed, did nothing.")

        except Exception as exc:
            logger.error(f"Failed processing file {file}: {exc}")
            pass

    def move_file(self, file, target):
        if self.dryrun:
            logger.warning(f"[DRYRUN] Would move {file} ==> {target}")
            return
        makedirs(target.dirname, exist_ok=True)
        move(src=file, dst=str(target))
