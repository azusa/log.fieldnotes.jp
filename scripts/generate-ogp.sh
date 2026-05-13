#!/bin/bash

# Wrapper script for generate-ogp.py
# This ensures all script executions use bash for consistency

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/generate-ogp.py"

if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "Error: $PYTHON_SCRIPT not found" >&2
    exit 1
fi

python3 "$PYTHON_SCRIPT" "$@"
