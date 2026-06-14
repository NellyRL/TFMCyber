"""
AUTOR: David Martín Castro
This script contains the functions that are used to create, delete or modify files.
"""

#---------------------------- LIBRARIES IMPORT ---------------------------

import os
import shutil
import struct
from src.common.colours import *
from src.common import paths

#---------------------------- FILE FUNCTIONS -----------------------------

def remove_report() -> None:

    """
    This function tries to remove previous versions of report.json file.
    """

    try:
        os.remove(paths.get_report_path())
        print(f"{greenColour}[+]{endColour}{grayColour} Report file removed{endColour}")
    except:
        print(f"{redColour}[!]{endColour}{grayColour} Previous report file not exist{endColour}")

    try:
        os.remove(paths.get_report_without_extension_path())
    except:
        pass


def remove_user_data() -> None:

    """
    This function tries to remove previous versions of user data directory.
    """

    try:
        shutil.rmtree(paths.get_user_data_path())
        print(f"{greenColour}[+]{endColour}{grayColour} User data directory removed{endColour}")
    except:
        print(f"{redColour}[!]{endColour}{grayColour} Previous user data directory not exist{endColour}")

def decompress_extension(extension_path, target_dir=None) -> None:

    """
    This function tries to decompress an extension file.

    target_dir lets callers unpack somewhere other than the shared automated-run
    directory (the manual session uses its own per-sample dir so the two paths do
    not collide). Defaults to get_extension_path() to keep existing callers intact.
    """
    target = target_dir or paths.get_extension_path()
    try:
        shutil.unpack_archive(extension_path, target)
        print(f"{greenColour}[+]{endColour}{grayColour} Extension decompressed{endColour}")
    except:
        print(f"{redColour}[!]{endColour}{grayColour} Extension not decompressed{endColour}")


# CREDITS: https://github.com/Poikilos/uncrx/blob/master/uncrx.py

def zip_file_name(name):
    return name + ".zip"

def decompress_crx(filename, target_dir=None):
    ret = None

    with open(filename, "rb") as crx_in:
        magic_number = crx_in.read(4)
        magic_number_s = None
        magic_number_s = magic_number.decode("utf-8")
        if magic_number_s != "Cr24":
            print("ERROR: '" + filename + "' is not a valid crx file.")
            print("  - magic number is " + magic_number_s)
            exit(1)

        version = crx_in.read(4)
        (version,) = struct.unpack(b"<I", version)

        print("  - version: " + str(version))

        public_key_length_s = crx_in.read(4)
        (public_key_length,) = struct.unpack(b"<I", public_key_length_s)
        print("  - public_key_length: " + str(public_key_length))
        zip_sig = b"\x50\x4b\x03\x04"

        if version <= 2:
            signature_key_length = crx_in.read(4)
            (signature_key_length,) = struct.unpack(b"<I", signature_key_length)
            print("  - signature_key_length: " + str(signature_key_length))
            if signature_key_length > 1024 * 4 / 8:
                print(
                    "    - WARNING: larger than normal"
                    " signature_key_length "
                    + str(signature_key_length)
                    + " ('"
                    + public_key_length_s.decode("utf-8")
                    + "')"
                )

            crx_in.seek(public_key_length + signature_key_length, os.SEEK_CUR)
        zip_name = zip_file_name(filename)
        wrote = 0
        if zip_name is None:
            print("  - can't generate zip name from " + str(filename))
        try:
            print("  - writing '%s'..." % zip_name)
            with open(zip_name, "wb") as fzip:
                buf = " "
                while buf:  # len(buf) > 0
                    buf = crx_in.read(1)
                    # print("    - '" + buf.decode('utf-8') + "'")
                    if buf:
                        ret = zip_name
                        fzip.write(buf)
                        wrote += 1
        except IOError as e:
            print("  - couldn't open or write to file (%s)." % zip_name)
        if ret is None:
            print("  - read 0 bytes from file (%s)." % filename)
        if wrote < 1:
            print("  - wrote 0 bytes to file (%s)." % zip_name)
    
    shutil.unpack_archive(ret, target_dir or paths.get_extension_path())
    print(f"{greenColour}[+]{endColour}{grayColour} Extension decompressed{endColour}")
    return zip_name
# CREDITS END

def remove_crx_zip(crx_zip) -> None:

    """
    This function tries to remove the crx.zip file.
    """

    try:
        os.remove(crx_zip)
        print(f"{greenColour}[+]{endColour}{grayColour} Crx.zip removed{endColour}")
    except:
        print(f"{redColour}[!]{endColour}{grayColour} Crx.zip not removed{endColour}")


def remove_extension() -> None:

    """
    This function tries to remove the extension directory.
    """
    try:
        print(paths.get_extension_path())
        shutil.rmtree(paths.get_extension_path())
        print(f"{greenColour}[+]{endColour}{grayColour} Extension removed{endColour}")
    except:
        print(f"{redColour}[!]{endColour}{grayColour} Extension not removed{endColour}")