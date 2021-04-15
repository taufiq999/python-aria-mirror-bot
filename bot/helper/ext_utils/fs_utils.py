import os
import pathlib
import shutil
import sys
import tarfile

import magic
from bot import DOWNLOAD_DIR, LOGGER, aria2

from .exceptions import NotSupportedExtractionArchive


def clean_download(path: str):
    if os.path.exists(path):
        LOGGER.info(f"Cleaning download: {path}")
        shutil.rmtree(path)


def start_cleanup():
    try:
        shutil.rmtree(DOWNLOAD_DIR)
    except FileNotFoundError:
        pass


def clean_all():
    aria2.remove_all(True)
    try:
        shutil.rmtree(DOWNLOAD_DIR)
    except FileNotFoundError:
        pass


def exit_clean_up(signal, frame):
    try:
        LOGGER.info(
            "Please wait, while we clean up the downloads and stop running downloads"
        )
        clean_all()
        sys.exit(0)
    except KeyboardInterrupt:
        LOGGER.warning("Force Exiting before the cleanup finishes!")
        sys.exit(1)


def get_path_size(path):
    if os.path.isfile(path):
        return os.path.getsize(path)
    total_size = 0
    for root, _, files in os.walk(path):
        for f in files:
            abs_path = os.path.join(root, f)
            total_size += os.path.getsize(abs_path)
    return total_size


def tar(org_path):
    tar_path = org_path + ".tar"
    path = pathlib.PurePath(org_path)
    LOGGER.info(f"Tar: orig_path: {org_path}, tar_path: {tar_path}")
    tar = tarfile.open(tar_path, "w")
    tar.add(org_path, arcname=path.name)
    tar.close()
    return tar_path


def get_base_name(orig_path: str):
    if orig_path.endswith(".tar.bz2"):
        return orig_path.replace(".tar.bz2", "")
    if orig_path.endswith(".tar.gz"):
        return orig_path.replace(".tar.gz", "")
    if orig_path.endswith(".bz2"):
        return orig_path.replace(".bz2", "")
    if orig_path.endswith(".gz"):
        return orig_path.replace(".gz", "")
    if orig_path.endswith(".tar"):
        return orig_path.replace(".tar", "")
    if orig_path.endswith(".tbz2"):
        return orig_path.replace("tbz2", "")
    if orig_path.endswith(".tgz"):
        return orig_path.replace(".tgz", "")
    if orig_path.endswith(".zip"):
        return orig_path.replace(".zip", "")
    if orig_path.endswith(".7z"):
        return orig_path.replace(".7z", "")
    if orig_path.endswith(".Z"):
        return orig_path.replace(".Z", "")
    if orig_path.endswith(".rar"):
        return orig_path.replace(".rar", "")
    if orig_path.endswith(".iso"):
        return orig_path.replace(".iso", "")
    if orig_path.endswith(".wim"):
        return orig_path.replace(".wim", "")
    if orig_path.endswith(".cab"):
        return orig_path.replace(".cab", "")
    if orig_path.endswith(".apm"):
        return orig_path.replace(".apm", "")
    if orig_path.endswith(".arj"):
        return orig_path.replace(".arj", "")
    if orig_path.endswith(".chm"):
        return orig_path.replace(".chm", "")
    if orig_path.endswith(".cpio"):
        return orig_path.replace(".cpio", "")
    if orig_path.endswith(".cramfs"):
        return orig_path.replace(".cramfs", "")
    if orig_path.endswith(".deb"):
        return orig_path.replace(".deb", "")
    if orig_path.endswith(".dmg"):
        return orig_path.replace(".dmg", "")
    if orig_path.endswith(".fat"):
        return orig_path.replace(".fat", "")
    if orig_path.endswith(".hfs"):
        return orig_path.replace(".hfs", "")
    if orig_path.endswith(".lzh"):
        return orig_path.replace(".lzh", "")
    if orig_path.endswith(".lzma"):
        return orig_path.replace(".lzma", "")
    if orig_path.endswith(".lzma2"):
        return orig_path.replace(".lzma2", "")
    if orig_path.endswith(".mbr"):
        return orig_path.replace(".mbr", "")
    if orig_path.endswith(".msi"):
        return orig_path.replace(".msi", "")
    if orig_path.endswith(".mslz"):
        return orig_path.replace(".mslz", "")
    if orig_path.endswith(".nsis"):
        return orig_path.replace(".nsis", "")
    if orig_path.endswith(".ntfs"):
        return orig_path.replace(".ntfs", "")
    if orig_path.endswith(".rpm"):
        return orig_path.replace(".rpm", "")
    if orig_path.endswith(".squashfs"):
        return orig_path.replace(".squashfs", "")
    if orig_path.endswith(".udf"):
        return orig_path.replace(".udf", "")
    if orig_path.endswith(".vhd"):
        return orig_path.replace(".vhd", "")
    if orig_path.endswith(".xar"):
        return orig_path.replace(".xar", "")
    raise NotSupportedExtractionArchive("File format not supported for extraction")


def get_mime_type(file_path):
    mime = magic.Magic(mime=True)
    mime_type = mime.from_file(file_path)
    mime_type = mime_type if mime_type else "text/plain"
    return mime_type
