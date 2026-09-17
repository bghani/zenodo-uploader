"""
Custom exceptions for zenodo-uploader.
"""


class ZenodoError(Exception):
    """Base exception for zenodo-uploader."""
    pass


class AuthenticationError(ZenodoError):
    """Raised when API authentication fails."""
    pass


class UploadError(ZenodoError):
    """Raised when file upload fails."""
    pass


class ChecksumMismatchError(ZenodoError):
    """Raised when MD5 checksum verification fails."""
    pass


class DraftError(ZenodoError):
    """Raised when draft record operations fail."""
    pass


class CompressionError(ZenodoError):
    """Raised when directory compression fails."""
    pass


class NetworkError(ZenodoError):
    """Raised for connection/network issues."""
    pass
