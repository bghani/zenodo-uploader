"""
Core Zenodo uploader API.

Original code by Pranav Durai taken
from: https://github.com/zenodo/zenodo/issues/2514 on 17 Sep 2026.

The code was adapted and extended with enhanced error handling, 
directory compression, and Python API support.
"""

import time
from pathlib import Path
from typing import Dict, Optional

import requests
from requests.exceptions import ConnectionError, Timeout, ChunkedEncodingError
from tqdm import tqdm

from .exceptions import (
    AuthenticationError,
    UploadError,
    ChecksumMismatchError,
    DraftError,
    NetworkError,
)
from .utils import compute_md5, format_bytes, compress_directory


class ZenodoUploader:
    """
    Upload files to Zenodo via REST API with retry logic and progress tracking.
    """

    BASE_URL = "https://zenodo.org/api"
    CHUNK_SIZE = 8 * 1024 * 1024  # 8 MB read buffer
    TIMEOUT = (30, 7200)  # (connect timeout, read timeout) in seconds
    MAX_RETRIES = 5
    RETRY_DELAY = 10  # seconds between retries

    def __init__(self, api_token: str, max_retries: int = 5, retry_delay: int = 10):
        """
        Initialize the uploader.

        Args:
            api_token: Zenodo API token with deposit:write scope.
            max_retries: Maximum number of retry attempts.
            retry_delay: Delay between retries in seconds.
        """
        if not api_token:
            raise AuthenticationError("API token is empty or None")

        self.api_token = api_token
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def _get_headers(self) -> Dict[str, str]:
        """Get authorization headers."""
        return {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }

    def _validate_token(self) -> bool:
        """
        Validate the API token by checking deposit endpoint.

        Returns:
            True if token is valid.

        Raises:
            AuthenticationError: If token is invalid.
        """
        try:
            response = requests.get(
                f"{self.BASE_URL}/deposit/depositions",
                headers=self._get_headers(),
                timeout=self.TIMEOUT,
            )
            if response.status_code == 401:
                raise AuthenticationError(
                    "Invalid API token. Check your ZENODO_API_KEY or --api-key."
                )
            response.raise_for_status()
            return True
        except (ConnectionError, Timeout) as e:
            raise NetworkError(f"Cannot reach Zenodo API: {e}")

    def create_draft(self) -> str:
        """
        Create a new empty draft deposit.

        Returns:
            The record ID of the new draft.

        Raises:
            DraftError: If draft creation fails.
        """
        try:
            print("Creating new draft record on Zenodo...")
            response = requests.post(
                f"{self.BASE_URL}/deposit/depositions",
                json={},
                headers=self._get_headers(),
                timeout=self.TIMEOUT,
            )
            response.raise_for_status()
            record_id = str(response.json()["id"])
            print(f"✓ Draft created: {record_id}")
            return record_id
        except requests.exceptions.HTTPError as e:
            raise DraftError(f"Failed to create draft: {e.response.text}")
        except (ConnectionError, Timeout) as e:
            raise NetworkError(f"Connection error creating draft: {e}")

    def get_bucket_url(self, record_id: str) -> str:
        """
        Retrieve the S3 bucket URL for a draft record.

        Args:
            record_id: The record ID.

        Returns:
            The bucket URL.

        Raises:
            DraftError: If bucket retrieval fails.
        """
        try:
            response = requests.get(
                f"{self.BASE_URL}/deposit/depositions/{record_id}",
                headers=self._get_headers(),
                timeout=self.TIMEOUT,
            )
            response.raise_for_status()
            bucket_url = response.json()["links"]["bucket"]
            print(f"✓ Bucket URL retrieved")
            return bucket_url
        except requests.exceptions.HTTPError as e:
            raise DraftError(f"Failed to retrieve bucket: {e.response.text}")
        except (ConnectionError, Timeout) as e:
            raise NetworkError(f"Connection error retrieving bucket: {e}")

    def upload_file(self, bucket_url: str, file_path: Path) -> Dict:
        """
        Upload a file to Zenodo's S3 bucket with retry logic.

        Args:
            bucket_url: The S3 bucket URL.
            file_path: Path to the file to upload.

        Returns:
            File metadata dict from Zenodo.

        Raises:
            UploadError: If upload fails after all retries.
            ChecksumMismatchError: If MD5 verification fails.
        """
        if not file_path.exists():
            raise UploadError(f"File not found: {file_path}")

        file_size = file_path.stat().st_size
        filename = file_path.name

        print(f"\nUploading: {filename} ({format_bytes(file_size)})")
        print("Computing MD5 checksum...")

        try:
            local_md5 = compute_md5(file_path)
            print(f"Local MD5: {local_md5}")
        except Exception as e:
            raise UploadError(f"Failed to compute checksum: {e}")

        upload_url = f"{bucket_url}/{filename}"

        for attempt in range(1, self.max_retries + 1):
            try:
                print(f"\nAttempt {attempt}/{self.max_retries}...", end=" ")
                
                with open(file_path, "rb") as f:
                    with tqdm(
                        total=file_size,
                        unit="B",
                        unit_scale=True,
                        unit_divisor=1024,
                        desc=filename,
                    ) as pbar:

                        class ProgressReader:
                            def __init__(self, fobj):
                                self.fobj = fobj

                            def read(self, size=-1):
                                chunk = self.fobj.read(size)
                                pbar.update(len(chunk))
                                return chunk

                        response = requests.put(
                            upload_url,
                            data=ProgressReader(f),
                            headers={
                                "Authorization": f"Bearer {self.api_token}",
                                "Content-Type": "application/octet-stream",
                                "Content-Length": str(file_size),
                            },
                            timeout=self.TIMEOUT,
                        )
                        response.raise_for_status()

                # Verify checksum
                remote_md5 = response.json().get("checksum", "").replace("md5:", "")
                if remote_md5 and remote_md5 != local_md5:
                    print(
                        f"\n✗ Checksum mismatch!\n"
                        f"  Local : {local_md5}\n"
                        f"  Remote: {remote_md5}"
                    )
                    raise ChecksumMismatchError("MD5 mismatch after upload")

                print("✓ Upload successful")
                print(f"Remote MD5: {remote_md5}")
                return response.json()

            except ChecksumMismatchError:
                raise
            except (ConnectionError, Timeout, ChunkedEncodingError) as e:
                error_type = type(e).__name__
                print(f"✗ {error_type}")
                if attempt < self.max_retries:
                    print(f"  Retrying in {self.retry_delay}s...")
                    time.sleep(self.retry_delay)
                else:
                    raise NetworkError(
                        f"Upload failed after {self.max_retries} attempts: {e}"
                    )
            except requests.exceptions.HTTPError as e:
                print(f"✗ HTTP Error {e.response.status_code}")
                if attempt < self.max_retries:
                    print(f"  Retrying in {self.retry_delay}s...")
                    time.sleep(self.retry_delay)
                else:
                    raise UploadError(f"Upload failed: {e.response.text}")

        return {}

    def upload(
        self,
        file_or_dir: Path,
        record_id: Optional[str] = None,
        compress_dir: bool = True,
    ) -> Dict:
        """
        Upload a file or directory to Zenodo.

        If a directory is provided, it is automatically compressed into a zip file.

        Args:
            file_or_dir: Path to file or directory.
            record_id: Existing draft record ID (optional; creates new if not provided).
            compress_dir: If True, compress directories before uploading.

        Returns:
            Dict with record_id and file info.

        Raises:
            UploadError: If upload fails.
        """
        file_or_dir = Path(file_or_dir)

        # Validate token first
        self._validate_token()

        # Handle directory compression
        if file_or_dir.is_dir():
            if not compress_dir:
                raise UploadError(
                    "Directory provided but compress_dir=False. "
                    "Please provide a file or set compress_dir=True."
                )
            file_to_upload = compress_directory(file_or_dir)
        else:
            file_to_upload = file_or_dir

        # Get or create draft
        if record_id:
            print(f"Using existing draft record: {record_id}")
        else:
            record_id = self.create_draft()

        # Get bucket and upload
        bucket_url = self.get_bucket_url(record_id)
        self.upload_file(bucket_url, file_to_upload)

        print("\n" + "=" * 60)
        print("✓ Upload complete!")
        print(f"Record ID : {record_id}")
        print(f"Record URL: https://zenodo.org/deposit/{record_id}")
        print("\nNext steps:")
        print("1. Visit the URL above")
        print("2. Add metadata (title, description, creators, etc.)")
        print("3. Click 'Publish' when ready")
        print("=" * 60)

        return {
            "record_id": record_id,
            "file": file_to_upload.name,
            "url": f"https://zenodo.org/deposit/{record_id}",
        }