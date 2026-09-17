"""
zenodo-uploader: Upload files and directories to Zenodo via REST API.

Original code by Pranav Durai.
Adapted and extended with enhanced error handling, directory compression,
and Python API support.
"""

__version__ = "1.0.0"
__author__ = "Contributors"

from .uploader import ZenodoUploader
from .exceptions import (
    ZenodoError,
    AuthenticationError,
    UploadError,
    ChecksumMismatchError,
    DraftError,
    CompressionError,
    NetworkError,
)
from .utils import compute_md5, format_bytes, compress_directory

__all__ = [
    "ZenodoUploader",
    "ZenodoError",
    "AuthenticationError",
    "UploadError",
    "ChecksumMismatchError",
    "DraftError",
    "CompressionError",
    "NetworkError",
    "compute_md5",
    "format_bytes",
    "compress_directory",
]
