from os import path, makedirs
import piexif
from glob import iglob
from datetime import datetime
from shutil import move
from tqdm import tqdm

from photo_normalizer.utils import hash_file

filename_fmt = "%Y-%m-%d__%H-%M-%S"
pathname_fmt = "%Y"
append_counter = True
ext = ".jpg"

base_path = "/Volumes/Fotos"
path_duplicates = "Duplicates"
path_nometa = "NoMetadata"
prefix_nometa = "nometa_"
path_nojpg = "NoJpeg"
dryrun = False

nometa_count = 1
nometa_hashes = []


path_nometa_full = path.join(base_path, path_nometa, "")
path_nojpg_full = path.join(base_path, path_nojpg, "")
path_duplicates_full = path.join(base_path, path_duplicates, "")

for file in tqdm(iglob(path.join(base_path, "**", "*"), recursive=True)):

    if (
        file.startswith(path_nometa_full) is True
        or file.startswith(path_nojpg_full) is True
        or file.startswith(path_duplicates_full) is True
        or path.isdir(file) is True
    ):
        continue

    lower_ext = path.splitext(file)[1].lower()
    if lower_ext != ext:
        try:
            tqdm.write("Non Jpg: %s" % file)
            new_target = path.join(base_path, path_nojpg, hash_file(file) + lower_ext)

            if new_target != file:
                try:
                    move(src=file, dst=new_target)
                except Exception:
                    pass

            continue
        except:
            tqdm.write("Failed on non-Jpg %s" % file)
            pass

    # Extract date from EXIF data, if not possible rename file by hash?
    exif_dict = piexif.load(file)
    exif_date = exif_dict["Exif"].get(piexif.ExifIFD.DateTimeOriginal)

    if exif_date is not None:
        exif_date = datetime.strptime(exif_date.decode("utf-8"), "%Y:%m:%d %H:%M:%S")

        new_path = path.join(base_path, exif_date.strftime(pathname_fmt))
        new_name = exif_date.strftime(filename_fmt)
    else:
        tqdm.write("File with no exif date: %s" % file)

        file_hash = hash_file(file)
        if file_hash not in nometa_hashes:
            nometa_hashes.append(file_hash)

            new_path = path.join(base_path, path_nometa)
            new_name = "nometa_%i" % nometa_count
            nometa_count += 1

        else:
            tqdm.write("Also a duplicate!")

            new_path = path.join(base_path, path_duplicates)
            new_name = "nometa__" + file_hash

    # Generate new path and name
    new_prepared = path.join(new_path, new_name)
    new_target = new_prepared

    if new_target + ext == file:
        pass
        # print('Same file')
    else:

        # Check if the target file already exists: check hash and rename otherwise
        append_count = 0
        while path.isfile(new_target + ext):
            if hash_file(new_target + ext) == hash_file(file):

                new_path = path.join(base_path, path_duplicates)
                new_target = path.join(new_path, new_name)

                break

            append_count += 1
            new_target = new_prepared + "_#%i" % append_count

        # Finally move the file to its new place
        if not dryrun:
            makedirs(new_path, exist_ok=True)
            move(src=file, dst=new_target + ext)

        tqdm.write("Path: %s" % new_target + ext)

