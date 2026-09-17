# zenodo-uploader

Upload large files and directories to Zenodo via REST API, with built-in retry logic, progress tracking, and intelligent error diagnostics.

**Perfect for researchers managing datasets > 5GB** — avoids browser-based connection reset issues.

## Features

 **Large file support** — Upload files > 5GB reliably  
 **Directory compression** — Automatically zip directories before upload  
 **Progress tracking** — Real-time progress bar with speed and ETA  
 **Retry logic** — Configurable retries with exponential backoff  
 **MD5 verification** — Ensure data integrity after upload  
 **Rich error messages** — Know exactly what failed and why  
 **Dual API** — Use as CLI tool or Python library  
 **Flexible auth** — Environment variable or command-line API key  

## Installation

### Via pip (recommended)

```bash
pip install zenodo-uploader
```

### From source

```bash
git clone https://github.com/bghani/zenodo-uploader.git
cd zenodo-uploader
pip install -e .
```

## Quick Start

### 1. Get your Zenodo API token

- Go to https://zenodo.org/account/settings/applications/tokens/new/
- Create a personal access token with `deposit:write` scope
- Save it somewhere safe

### 2. Set up your API key

**Option 1: Environment variable (recommended)**

```bash
export ZENODO_API_KEY="your-api-key-here"
```

**Option 2: Pass via CLI each time**

```bash
zupload --file my-dataset.zip --api-key "your-api-key-here"
```

### 3. Upload

```bash
# Upload a single file
zupload --file my-dataset.zip

# Upload a directory (automatically compressed)
zupload --file /path/to/my-data/

# Upload to an existing draft (to add more files)
zupload --file another-file.zip --record-id 1234567
```

## Usage

### CLI

```bash
# Basic upload
zupload --file dataset.zip

# Upload directory with custom retries
zupload --file ./my-data --retries 10 --retry-delay 15

# Add file to existing draft
zupload --file new-file.zip --record-id 1234567

# Don't compress directories (fails if directory provided)
zupload --file dataset.zip --no-compress

# Full help
zupload --help
```

### Python API

Use as a library in your own scripts:

```python
from zenodo_uploader import ZenodoUploader

uploader = ZenodoUploader(api_token="your-token")

# Upload a file
result = uploader.upload(
    file_or_dir="dataset.zip",
    record_id=None,  # Creates new draft if None
    compress_dir=True
)

print(f"Record: {result['record_id']}")
print(f"URL: {result['url']}")
```

### Handling errors

```python
from zenodo_uploader import ZenodoUploader, AuthenticationError, NetworkError

try:
    uploader = ZenodoUploader(api_token="token")
    result = uploader.upload("dataset.zip")
except AuthenticationError as e:
    print(f"API key issue: {e}")
except NetworkError as e:
    print(f"Connection problem: {e}")
```

## Configuration

### Retry behavior

Default: 5 retries with 10-second delays between attempts.

```bash
# More aggressive retries for unstable networks
zupload --file large.zip --retries 10 --retry-delay 20
```

### Compression control

By default, directories are automatically compressed. To disable:

```bash
zupload --file myfile.zip --no-compress
```

## Error Handling

Common errors and solutions:

| Error | Cause | Solution |
|-------|-------|----------|
| `AuthenticationError` | Invalid/missing API key | Check `ZENODO_API_KEY` env var or `--api-key` argument |
| `NetworkError` | Connection timeout/lost | Check internet connection; increase `--retry-delay` |
| `ChecksumMismatchError` | Data corruption during transfer | File may have been corrupted; retry upload |
| `CompressionError` | Failed to zip directory | Ensure directory is readable; free up disk space |
| `DraftError` | Cannot access draft record | Check record ID; ensure you have write access |

## API Reference

### `ZenodoUploader`

```python
class ZenodoUploader:
    def __init__(self, api_token: str, max_retries: int = 5, retry_delay: int = 10)
    def upload(self, file_or_dir: Path, record_id: Optional[str] = None, compress_dir: bool = True) -> Dict
    def create_draft(self) -> str
    def get_bucket_url(self, record_id: str) -> str
    def upload_file(self, bucket_url: str, file_path: Path) -> Dict
```

### Utility functions

```python
from zenodo_uploader import compute_md5, format_bytes, compress_directory

# Compute MD5 of a file
md5_hash = compute_md5(Path("dataset.zip"))

# Format bytes to human-readable
size_str = format_bytes(5368709120)  # "5.00 GB"

# Compress a directory
zip_path = compress_directory(Path("my-data"))
```

## Workflow Example

Typical research data pipeline:

```bash
# Set API key once per session
export ZENODO_API_KEY="your-token"

# Create a new draft
zupload --file part1.zip
# → Output: Record ID: 1234567

# Add more files to the same draft
zupload --file part2.zip --record-id 1234567
zupload --file part3.zip --record-id 1234567

# Visit https://zenodo.org/deposit/1234567
# → Fill in metadata (title, authors, description, etc.)
# → Click "Publish"
```

## Advanced: Custom retry strategy

```python
from zenodo_uploader import ZenodoUploader

# More aggressive for unstable networks
uploader = ZenodoUploader(
    api_token="token",
    max_retries=10,
    retry_delay=30  # 30 seconds between retries
)

uploader.upload("large-dataset.zip")
```

## Performance tips

1. **Upload from a stable network** — Use wired connection if possible
2. **Compress beforehand** — Pre-compress large directories locally if network is slow
3. **Increase timeouts for very large files** — Default 2-hour read timeout usually sufficient
4. **Monitor disk space** — Directory compression requires ~1x free space

## Limitations

- Zenodo has upload quotas; check your account at https://zenodo.org/account/settings/
- Single files are limited to ~2TB (Zenodo storage limit)
- Compressed zip files cannot exceed 50GB per file
- API rate limits apply (typically 100 requests/hour for authenticated users)

## FAQ

**Q: Can I upload files larger than 5GB?**  
A: Yes! That's the main use case. The default timeout is 2 hours for uploads.

**Q: What if the upload is interrupted?**  
A: Zenodo keeps the partial upload in your draft. Simply re-run the command with the same `--record-id` to resume or add another file.

**Q: Does zupload delete the original directory after compression?**  
A: No. Compression creates a new `.zip` file; the original directory remains.

**Q: Can I use this with other repositories (not Zenodo)?**  
A: Currently Zenodo only. The code is modular; contributing support for other repositories is welcome.

## Credits & Attribution

**Original code** by Pranav Durai  
(Published on [forum/community], 12.07.2026)

**Adaptations in this version:**
- Enhanced error handling and diagnostics
- Directory compression with progress tracking
- Python package structure and PyPI distribution
- Dual API (CLI + library)
- Flexible authentication (env var + CLI argument)
- Better user feedback and progress indicators

## License

MIT License — see LICENSE file for details.

## Contributing

Contributions welcome! Please open issues or submit PRs.

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing documentation above
- Review error messages (they're designed to be helpful)

---

**Happy uploading! 🚀**
