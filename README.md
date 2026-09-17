# zenodo-uploader

Upload large files and directories to Zenodo via REST API, with built-in retry logic, progress tracking, and intelligent error diagnostics.

**Perfect for researchers managing datasets > 5GB** — avoids browser-based connection reset issues.

## Features

**Large file support** — Upload files > 5GB reliably  
**Directory compression** — Automatically zip directories before upload  
**Progress tracking** — Real-time progress bar with speed and ETA  
**Retry logic** — Automatic retries on connection failures  
**MD5 verification** — Ensure data integrity after upload  
**Rich error messages** — Clear feedback on what went wrong and how to fix it  
**Flexible auth** — Environment variable or command-line API key  

## Installation

### Via pip (recommended)

```bash
pip install zupload
```

### From source

**Option 1: Using `uv` (fastest)**

```bash
git clone https://github.com/bghani/zenodo-uploader.git
cd zenodo-uploader
uv sync
source .venv/bin/activate  # on Windows: .venv\Scripts\activate
```

**Option 2: Using `pip`**

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

### 2. Set up your API key (one-time)

```bash
export ZENODO_API_KEY="your-api-key-here"
```

Or pass it each time with `--api-key`.


## Usage
 
### Command Line (CLI) — Two workflows: Choose what works for you
 
#### Workflow 1: Upload first, add metadata later (recommended for beginners)
 
```bash
# 1. Upload your file/directory 
zupload --file dataset.zip
zupload --file dataset # if a directory is passed, automatically compresses it to .zip before upload
zupload --file dataset.csv
 
# Output: Record ID: 1234567
# A new draft is automatically created on Zenodo
 
# 2. Visit https://zenodo.org/deposit/1234567
# 3. Add title, authors, description, keywords
# 4. Click "Publish"
```
 
This is the simplest way. The tool creates a draft for you automatically.
 
#### Workflow 2: Create draft first, then upload files to it
 
```bash
# 1. Go to https://zenodo.org and create a new draft (optional)
# 2. Note the Record ID from the URL
# 3. Upload to that draft
zupload --file part1.zip --record-id 1234567
zupload --file part2.zip --record-id 1234567
 
# 4. Visit https://zenodo.org/deposit/1234567
# 5. Click "Publish"
```
 
Use this if you want to add multiple files or have already created a draft on Zenodo.
 
---
 
#### Common commands
 
```bash
# Basic upload (creates new draft automatically)
zupload --file dataset.zip
 
# Upload directory (automatically compresses to .zip)
zupload --file ./my-data/
 
# Upload to existing draft (add more files)
zupload --file another-file.zip --record-id 1234567
 
# Customize retries for unstable networks
zupload --file large.zip --retries 10 --retry-delay 20
 
# Get help
zupload --help
```
 
See [FAQ](#faq) below for explanations of what each option does.
 
### Python API 
 
You can also use `zupload` as a Python library in your own code:
 
```python
from zupload import ZenodoUploader
 
# Create uploader instance
uploader = ZenodoUploader(api_token="your-token")
 
# Upload a file
result = uploader.upload("dataset.zip")
print(f"Record ID: {result['record_id']}")
print(f"URL: {result['url']}")
 
# Upload directory (auto-compressed)
uploader.upload("./my-data/", compress_dir=True)
 
# Add file to existing draft
uploader.upload("part2.zip", record_id="1234567")
```
 
**For detailed examples, error handling, and advanced usage, see [DEVELOPMENT.md](DEVELOPMENT.md).**

## Error Messages & Solutions

If something goes wrong, `zupload` tells you what happened. Here are the most common ones:

| Error | Cause | Solution |
|-------|-------|----------|
| `API key issue` | Invalid or missing token | Set `ZENODO_API_KEY` or use `--api-key` (see Setup section) |
| `Connection problem` | Network timeout | Check internet; retry with `--retry-delay 30 --retries 10` |
| `Checksum mismatch` | Data corrupted during upload | Rare — try the upload again |
| `Cannot access draft` | Bad Record ID or no access | Check the Record ID; visit Zenodo to verify |
| `Failed to zip directory` | Compression error | Ensure directory is readable; free up disk space |

**Don't see your error?** Read the full error message carefully — it's written to help you fix it.

See [FAQ](#faq) above for more details on common options and problems.

## Next Steps After Upload

Once you run `zupload`, you get a Zenodo URL. Visit it to complete your deposit:

```bash
zupload --file dataset.zip
# Output: https://zenodo.org/deposit/1234567

# Visit that URL and:
# 1. Add title (required)
# 2. Add author(s) (required)
# 3. Add description (recommended)
# 4. Add keywords (recommended)
# 5. Click "Publish"

# Your dataset now has a DOI and is public!
```

**Need to add more files before publishing?**

```bash
# Keep the same Record ID and upload more
zupload --file part2.zip --record-id 1234567
zupload --file part3.zip --record-id 1234567

# Then visit the URL and publish when ready
```

See [Usage](#usage) above for both workflows.

## FAQ

### Understanding the basics

**Q: What is a "draft"?**  
A: A draft is a temporary workspace on Zenodo where you can upload files and add metadata before publishing. It's private until you hit "Publish". The draft gets a Record ID (like `1234567`) that you use to manage it.

**Q: Do I have to create a draft first on Zenodo?**  
A: No! Use **Workflow 1** above — `zupload` creates one automatically. You only need to create one manually (Workflow 2) if you want to add files to an existing draft or prefer starting on Zenodo's website.

**Q: What's the difference between the two workflows?**  
A: 
- **Workflow 1 (recommended):** Upload → get Record ID → add metadata on Zenodo → Publish
- **Workflow 2:** Create draft on Zenodo → get Record ID → upload files with `zupload` → add metadata → Publish

Both end the same place; Workflow 1 is fewer steps.

### File and directory options

**Q: What does `--file dataset.zip` do?**  
A: Uploads the file `dataset.zip` to Zenodo. File must exist. See `zupload --help` for more options.

**Q: What happens when I use `--file ./my-data/` (a directory)?**  
A: The directory is automatically compressed into a `.zip` file, then uploaded. The original directory stays on your computer. This is called "automatic compression" — see below.

**Q: What is "automatic compression"?**  
A: When you give `zupload` a folder instead of a file, it automatically zips it up before uploading. This is convenient because Zenodo only accepts files, not folders. You can disable this with `--no-compress` (but then you must give it a file).

**Q: Can I upload multiple files at once?**  
A: Not in a single command. But you can upload multiple files to the same draft:
```bash
zupload --file file1.zip --record-id 1234567
zupload --file file2.zip --record-id 1234567
```
They all go into the same record.

### Draft management

**Q: What is `--record-id`?**  
A: The ID of an existing draft on Zenodo. Use this to add more files to a draft. Format: a number like `1234567`. Found in the URL: `https://zenodo.org/deposit/1234567`.

**Q: When do I use `--record-id`?**  
A: When you want to add more files to an existing draft (Workflow 2), or if you already created a draft on Zenodo's website and want to upload files to it.

**Q: How do I find my Record ID?**  
A: 
- After first upload: `zupload` shows it in the output
- Or go to https://zenodo.org/account/deposits and look at the URL of your draft

### Network and retry options

**Q: What do `--retries` and `--retry-delay` do?**  
A: 
- `--retries`: How many times to try uploading if it fails (default: 5)
- `--retry-delay`: How many seconds to wait between tries (default: 10)

**Q: When should I increase retries?**  
A: If your internet is unstable or you're uploading a very large file. Example:
```bash
zupload --file huge.zip --retries 10 --retry-delay 30
```

**Q: What if my upload is interrupted?**  
A: Zenodo keeps what was uploaded. Re-run the same command and it should resume (or use the same `--record-id` and try again).

### Large files

**Q: Can I upload files larger than 5GB?**  
A: Yes! That's the whole point of this tool.

**Q: How long does a 10GB upload take?**  
A: Depends on your internet speed. At 10 Mbps: ~2-3 hours. The progress bar shows real-time speed and ETA.

### Other common questions

**Q: Does `zupload` delete my files after uploading?**  
A: No. It uploads a copy to Zenodo; your local files stay on your computer.

**Q: Does it delete the original directory after compressing it?**  
A: No. It creates a new `.zip` file; the original folder remains.

**Q: What does `--api-key` do?**  
A: Passes your Zenodo API key directly instead of using the `ZENODO_API_KEY` environment variable:
```bash
zupload --file data.zip --api-key "your-token-here"
```
Usually you set the env var once instead (less typing, safer).

**Q: What if I see an error message?**  
A: See the "Error Messages & Solutions" table above. Error messages are designed to tell you what's wrong.

**Q: Can I use this with other repositories (GitHub, Figshare, OSF)?**  
A: Currently Zenodo only. Contributions to support other repos are welcome!

**Q: Is my data private?**  
A: While it's in a draft, yes — only you can see it. Once you click "Publish", it's public and gets a DOI (unless you specify otherwise on Zenodo).

## Limits

Zenodo has some hard limits to be aware of:

- **File size:** Single file up to ~2TB (but Zenodo quota may be lower)
- **Zip file:** Compressed files cannot exceed 50GB
- **Rate limits:** ~100 API requests/hour per account
- **Quota:** Check your account at https://zenodo.org/account/settings/

If you hit these, you'll get a clear error message.

## Support

- **Questions?** Check the [FAQ](#faq) above — most common questions are answered there
- **Error?** Read the error message carefully; they're designed to help you fix it
- **Still stuck?** Open an issue on GitHub
- **Python API?** See [DEVELOPMENT.md](DEVELOPMENT.md)

## Credits

Adapted from a basic version of a code by Pranav Durai  
(Published on https://github.com/zenodo/zenodo/issues/2514 in July 2026)

**Adaptations in this version:**
- Enhanced error handling and diagnostics
- Directory compression with progress tracking
- Python package + PyPI distribution
- Flexible authentication (env var + CLI argument)
- Better user feedback and progress indicators

## License

MIT License — see [LICENSE](https://github.com/bghani/zenodo-uploader/blob/main/LICENSE) file for details.

---

**Happy uploading!**