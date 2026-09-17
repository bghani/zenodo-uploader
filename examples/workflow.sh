#!/bin/bash

# Example: Upload a dataset to Zenodo as part of a research workflow
# 
# Usage:
#   export ZENODO_API_KEY="your-token"
#   bash workflow.sh

set -e  # Exit on error

echo "Research Data Upload Workflow"
echo "=============================="

# Check API key
if [ -z "$ZENODO_API_KEY" ]; then
    echo "Error: Set ZENODO_API_KEY environment variable"
    exit 1
fi

# Create data directory (example)
DATA_DIR="./my-research-data"
mkdir -p "$DATA_DIR"

# Simulate some data files
echo "Creating sample data..."
echo "Sample acoustic recording metadata" > "$DATA_DIR/README.txt"
echo "species,location,date,duration" > "$DATA_DIR/recordings.csv"
echo "Parus caeruleus,Forest A,2026-01-15,120" >> "$DATA_DIR/recordings.csv"

# Upload to Zenodo
echo ""
echo "Uploading to Zenodo..."
zupload --file "$DATA_DIR"

echo ""
echo "✓ Done! Check the URL above to add metadata and publish."
