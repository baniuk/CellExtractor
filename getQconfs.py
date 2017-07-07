"""Provide list of QCONF files in folder."""

from os import path as p
import glob

ext = ".QCONF"


def scanFolder(folder):
    """Scan folder for QCONF files and returns list of them."""
    print("Scanning ", folder)
    if not p.isdir(folder):
        raise Exception("Not a folder")

    return glob.glob(p.join(folder, "*" + ext))
