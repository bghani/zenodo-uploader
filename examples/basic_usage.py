"""
Example: Basic usage of zenodo-uploader Python API.
"""

import os
from pathlib import Path
from zupload import ZenodoUploader, NetworkError, AuthenticationError

# Get API key from environment
api_key = os.getenv("ZENODO_API_KEY")
if not api_key:
    print("Error: Set ZENODO_API_KEY environment variable")
    exit(1)

# Initialize uploader
uploader = ZenodoUploader(api_token=api_key)

# Example 1: Upload a single file
print("=" * 60)
print("Example 1: Upload a single file")
print("=" * 60)

try:
    result = uploader.upload(
        file_or_dir="my-dataset.zip",
        record_id=None,  # Creates a new draft
    )
    print(f"\nSuccess! Record ID: {result['record_id']}")
    print(f"URL: {result['url']}")
except (AuthenticationError, NetworkError) as e:
    print(f"Error: {e}")


# Example 2: Upload a directory (automatically compressed)
print("\n" + "=" * 60)
print("Example 2: Upload a directory")
print("=" * 60)

try:
    result = uploader.upload(
        file_or_dir="./my-data-folder",
        compress_dir=True,
    )
    print(f"\nSuccess! Record ID: {result['record_id']}")
    print(f"URL: {result['url']}")
except (AuthenticationError, NetworkError) as e:
    print(f"Error: {e}")


# Example 3: Add a file to an existing draft
print("\n" + "=" * 60)
print("Example 3: Add file to existing draft")
print("=" * 60)

existing_record_id = "1234567"  # Replace with actual record ID

try:
    result = uploader.upload(
        file_or_dir="additional-file.zip",
        record_id=existing_record_id,
    )
    print(f"\nFile added to draft: {existing_record_id}")
    print(f"URL: {result['url']}")
except (AuthenticationError, NetworkError) as e:
    print(f"Error: {e}")


# Example 4: Custom retry configuration
print("\n" + "=" * 60)
print("Example 4: Custom retry settings for unstable networks")
print("=" * 60)

uploader_resilient = ZenodoUploader(
    api_token=api_key,
    max_retries=10,
    retry_delay=30,  # 30 seconds between retries
)

try:
    result = uploader_resilient.upload("large-dataset.zip")
    print(f"\nSuccess! Record ID: {result['record_id']}")
except (AuthenticationError, NetworkError) as e:
    print(f"Error: {e}")
