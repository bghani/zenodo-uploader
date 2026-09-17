"""
Command-line interface for zenodo-uploader.
"""

import argparse
import sys
from pathlib import Path

from .uploader import ZenodoUploader
from .utils import get_api_key
from .exceptions import ZenodoError


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Upload files and directories to Zenodo via REST API.",
        epilog=(
            "API Key Setup:\n"
            "  Option 1 (recommended): export ZENODO_API_KEY='your-api-key'\n"
            "  Option 2: --api-key 'your-api-key'"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--file",
        "-f",
        required=True,
        type=str,
        help="Path to file or directory to upload",
    )

    parser.add_argument(
        "--api-key",
        "-k",
        type=str,
        default=None,
        help="Zenodo API token (alternative to ZENODO_API_KEY env var)",
    )

    parser.add_argument(
        "--record-id",
        "-r",
        type=str,
        default=None,
        help="Existing draft record ID (omit to create new)",
    )

    parser.add_argument(
        "--no-compress",
        action="store_true",
        help="Don't compress directories (will fail if directory provided)",
    )

    parser.add_argument(
        "--retries",
        type=int,
        default=5,
        help="Maximum number of retry attempts (default: 5)",
    )

    parser.add_argument(
        "--retry-delay",
        type=int,
        default=10,
        help="Delay between retries in seconds (default: 10)",
    )

    args = parser.parse_args()

    # Resolve API key
    api_key = args.api_key
    if not api_key:
        try:
            api_key = get_api_key()
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    # Validate file/dir exists
    file_or_dir = Path(args.file)
    if not file_or_dir.exists():
        print(f"Error: Path does not exist — {file_or_dir}", file=sys.stderr)
        sys.exit(1)

    # Run upload
    try:
        uploader = ZenodoUploader(
            api_token=api_key,
            max_retries=args.retries,
            retry_delay=args.retry_delay,
        )

        result = uploader.upload(
            file_or_dir=file_or_dir,
            record_id=args.record_id,
            compress_dir=not args.no_compress,
        )

        sys.exit(0)

    except ZenodoError as e:
        print(f"\n✗ Upload failed: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
