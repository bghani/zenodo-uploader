# Developer Guide

For Python API usage, error handling, and advanced configurations.

## Python API

### Basic usage

```python
from zenodo_uploader import ZenodoUploader

uploader = ZenodoUploader(api_token="your-token")

# Upload a file
result = uploader.upload("dataset.zip")

print(f"Record ID: {result['record_id']}")
print(f"URL: {result['url']}")
```

### Upload a directory

```python
# Automatically compresses to .zip
result = uploader.upload(
    file_or_dir="./my-data/",
    compress_dir=True
)
```

### Add file to existing draft

```python
result = uploader.upload(
    file_or_dir="part2.zip",
    record_id="1234567"
)
```

## Error Handling

```python
from zenodo_uploader import (
    ZenodoUploader,
    AuthenticationError,
    NetworkError,
    ChecksumMismatchError,
    DraftError,
    CompressionError,
)

uploader = ZenodoUploader(api_token="token")

try:
    result = uploader.upload("dataset.zip")
except AuthenticationError as e:
    print(f"Invalid API key: {e}")
except NetworkError as e:
    print(f"Connection issue: {e}")
    # Retry logic here
except ChecksumMismatchError as e:
    print(f"Data corruption: {e}")
except DraftError as e:
    print(f"Draft error (bad record ID?): {e}")
except CompressionError as e:
    print(f"Failed to compress directory: {e}")
```

## Custom Retry Configuration

```python
uploader = ZenodoUploader(
    api_token="token",
    max_retries=10,        # More retries
    retry_delay=30         # 30 seconds between attempts
)

uploader.upload("large-dataset.zip")
```

## Utility Functions

```python
from zenodo_uploader import compute_md5, format_bytes, compress_directory
from pathlib import Path

# Compute MD5 checksum
md5_hash = compute_md5(Path("dataset.zip"))
print(f"MD5: {md5_hash}")

# Format bytes to human-readable
size_str = format_bytes(5368709120)
print(size_str)  # "5.00 GB"

# Compress a directory
zip_path = compress_directory(Path("my-data"))
print(f"Compressed to: {zip_path}")
```

## Advanced Workflow: Batch Upload

```python
from zenodo_uploader import ZenodoUploader, NetworkError
import time

uploader = ZenodoUploader(api_token="token")

# Create new draft
record_id = uploader.create_draft()
print(f"Created draft: {record_id}")

# Get bucket
bucket_url = uploader.get_bucket_url(record_id)

# Upload multiple files
files = ["part1.zip", "part2.zip", "part3.zip"]
for file in files:
    try:
        uploader.upload_file(bucket_url, file)
        print(f"✓ {file} uploaded")
    except NetworkError as e:
        print(f"✗ {file} failed: {e}")
        time.sleep(60)
        # Retry or skip

print(f"Visit: https://zenodo.org/deposit/{record_id}")
```

## API Reference

### ZenodoUploader

```python
class ZenodoUploader:
    def __init__(
        self,
        api_token: str,
        max_retries: int = 5,
        retry_delay: int = 10
    )
    """
    Initialize uploader.
    
    Args:
        api_token: Zenodo API token with deposit:write scope
        max_retries: Max retry attempts (default: 5)
        retry_delay: Delay between retries in seconds (default: 10)
    """

    def upload(
        self,
        file_or_dir: Path,
        record_id: Optional[str] = None,
        compress_dir: bool = True
    ) -> Dict
    """
    Upload file or directory to Zenodo.
    
    Args:
        file_or_dir: Path to file or directory
        record_id: Existing draft ID (optional; creates new if None)
        compress_dir: Auto-compress directories to .zip
        
    Returns:
        Dict with record_id, file, and url
    """

    def create_draft(self) -> str
    """Create a new draft deposit. Returns record ID."""

    def get_bucket_url(self, record_id: str) -> str
    """Get S3 bucket URL for a draft record."""

    def upload_file(
        self,
        bucket_url: str,
        file_path: Path
    ) -> Dict
    """Upload file to S3 bucket. Returns file metadata."""
```

### Exceptions

```python
ZenodoError              # Base exception
├── AuthenticationError  # Invalid API token
├── UploadError         # Upload failed
├── ChecksumMismatchError # MD5 verification failed
├── DraftError          # Draft operation failed
├── CompressionError    # Directory compression failed
└── NetworkError        # Connection/timeout issue
```

### Utility Functions

```python
compute_md5(file_path: Path) -> str
"""Compute MD5 checksum of a file."""

format_bytes(size_bytes: int) -> str
"""Format bytes to human-readable (B, KB, MB, GB, TB, PB)."""

compress_directory(dir_path: Path, output_path: Path = None) -> Path
"""Compress directory to .zip with progress bar."""

get_api_key() -> str
"""Retrieve API key from ZENODO_API_KEY environment variable."""
```

## Environment Variables

```bash
# Required for API authentication
export ZENODO_API_KEY="your-api-token"
```

## Configuration

### Connection timeout

Default: 30 seconds for connect, 7200 seconds (2 hours) for read.

To customize, modify the `TIMEOUT` constant in `zenodo_uploader/uploader.py`:

```python
TIMEOUT = (30, 7200)  # (connect_timeout, read_timeout)
```

### Chunk size

Default: 8 MB for streaming and MD5 computation.

Modify in `zenodo_uploader/utils.py`:

```python
CHUNK_SIZE = 8 * 1024 * 1024  # 8 MB
```

## Performance Tips

1. **Connection** — Upload from stable, wired network
2. **Pre-compression** — For very large directories, pre-compress locally
3. **Retries** — Increase for unstable networks: `--retry-delay 30 --retries 10`
4. **Disk space** — Directory compression needs ~1x free space
5. **File size** — Zenodo single-file limit is ~2TB; zip files max 50GB

## Testing

```bash
# Install dev dependencies
uv sync --extra dev

# Run tests (if available)
pytest tests/

# Run with coverage
pytest --cov=zenodo_uploader tests/
```

## Contributing

Contributions welcome! Areas for enhancement:

- Support for other repositories (Figshare, OSF, etc.)
- Resume interrupted uploads (Zenodo resumable uploads API)
- Parallel file uploads
- Web UI (Streamlit/Flask)
- Better progress reporting for network issues

## License

MIT — see LICENSE file.