"""
Utility functions for zenodo-uploader.
"""

import hashlib
import os
import shutil
import sys
import zipfile
from pathlib import Path

from tqdm import tqdm

from .exceptions import CompressionError


CHUNK_SIZE = 8 * 1024 * 1024  # 8 MB read buffer


def compute_md5(file_path: Path) -> str:
    """
    Compute MD5 checksum of a file.

    Args:
        file_path: Path to the file.

    Returns:
        MD5 hash as hex string.
    """
    h = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(CHUNK_SIZE), b""):
            h.update(chunk)
    return h.hexdigest()


def format_bytes(size_bytes: int) -> str:
    """Format bytes to human-readable string."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def compress_directory(dir_path: Path, output_path: Path = None) -> Path:
    """
    Compress a directory into a zip file.

    Args:
        dir_path: Path to the directory to compress.
        output_path: Output zip file path. Defaults to dir_name.zip in current dir.

    Returns:
        Path to the created zip file.

    Raises:
        CompressionError: If compression fails.
    """
    if not dir_path.is_dir():
        raise CompressionError(f"Not a directory: {dir_path}")

    if output_path is None:
        output_path = Path.cwd() / f"{dir_path.name}.zip"

    try:
        print(f"\nCompressing directory: {dir_path.name}")
        print(f"Output: {output_path.name}")

        # Get total size for progress bar
        total_size = sum(
            f.stat().st_size
            for f in dir_path.rglob("*")
            if f.is_file()
        )

        with tqdm(
            total=total_size,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
            desc=output_path.name,
        ) as pbar:
            with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
                for file_path in dir_path.rglob("*"):
                    if file_path.is_file():
                        arcname = file_path.relative_to(dir_path.parent)
                        zf.write(file_path, arcname)
                        pbar.update(file_path.stat().st_size)

        print(f"Compression complete: {format_bytes(output_path.stat().st_size)}")
        return output_path

    except Exception as e:
        raise CompressionError(f"Failed to compress directory: {e}")


def get_api_key() -> str:
    """
    Retrieve Zenodo API key from environment variable.

    Returns:
        The API key.

    Raises:
        ValueError: If API key is not found in environment.
    """
    api_key = os.getenv("ZENODO_API_KEY")
    if not api_key:
        raise ValueError(
            "ZENODO_API_KEY environment variable not set. "
            "Set it with: export ZENODO_API_KEY='your-api-key'\n"
            "Or pass --api-key directly to the command."
        )
    return api_key
