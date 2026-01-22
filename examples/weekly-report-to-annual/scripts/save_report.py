#!/usr/bin/env python3
"""
Save annual report to local file.

Saves the generated annual report content to a specified path.
"""

import json
import sys
from datetime import datetime
from pathlib import Path


def main():
    """Main entry point."""
    stdin_content = sys.stdin.read().strip()

    try:
        input_data = json.loads(stdin_content)
        content = input_data.get("content", "")
        output_path = input_data.get("output_path", "")
        filename = input_data.get("filename", "")
    except json.JSONDecodeError:
        # If not JSON, treat as plain text content
        content = stdin_content
        output_path = ""
        filename = ""

    if not content:
        print(json.dumps({
            "error": "No content provided",
            "hint": "Please provide 'content' in the input JSON"
        }, ensure_ascii=False))
        return

    # Generate default filename if not provided
    if not filename:
        year = datetime.now().year
        filename = f"annual-report-{year}.md"

    # Determine output path
    if output_path:
        output_dir = Path(output_path).expanduser()
    else:
        # Default to current directory or user's Documents
        output_dir = Path.cwd()

    # Ensure directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Full file path
    file_path = output_dir / filename

    try:
        # Write content to file
        file_path.write_text(content, encoding='utf-8')

        result = {
            "status": "success",
            "message": "Annual report saved successfully",
            "file_path": str(file_path.absolute()),
            "filename": filename,
            "size_bytes": len(content.encode('utf-8')),
            "size_chars": len(content),
            "timestamp": datetime.now().isoformat(),
        }

        print(json.dumps(result, ensure_ascii=False, indent=2))

    except PermissionError:
        print(json.dumps({
            "error": f"Permission denied: Cannot write to {file_path}",
            "hint": "Try a different output path"
        }, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
