"""
Command-line text summarizer.

Usage:
    python main.py <file_path>

Exits with status 0 on success and 1 on any error, so the tool can be
used safely in shell scripts and pipelines.
"""

import sys

USAGE = "Usage: python main.py <file_path>"


def load_file(file_path):
    """
    Load text content from a file.

    Validates that the file exists, is readable as UTF-8 text, and is
    not empty. On any failure, prints a clear user-facing error message
    (never a stack trace) and returns None.

    Args:
        file_path (str): Path to the text file to load.

    Returns:
        str | None: The file's text content, or None on failure.
    """
    # Attempt the read directly and translate each failure into a clean
    # message. This also covers cases that pre-checks can't catch
    # reliably: permissions, binary content, or the file disappearing
    # between a check and the open.
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        print(f'❌ Error: File "{file_path}" not found.', file=sys.stderr)
        return None
    except IsADirectoryError:
        print(
            f"❌ Error: Expected a file but got a directory: {file_path}",
            file=sys.stderr,
        )
        return None
    except PermissionError:
        print(f"❌ Error: No permission to read: {file_path}", file=sys.stderr)
        return None
    except UnicodeDecodeError:
        print(
            f"❌ Error: Not a readable text file (binary or non-UTF-8 content): {file_path}",
            file=sys.stderr,
        )
        return None
    except OSError as e:
        # Catch-all for rarer I/O failures (disk errors, invalid paths, ...).
        print(
            f"❌ Error: Could not read {file_path}: {e.strerror or e}", file=sys.stderr
        )
        return None

    # .strip() so whitespace-only files count as empty, not as valid content.
    if not text.strip():
        print(f"❌ Error: File is empty: {file_path}", file=sys.stderr)
        return None

    print(f"📖 Loaded file: {file_path}")
    return text


def summarize(text):
    """
    Summarize the given text.

    Currently a stub that returns a placeholder string.
    TODO: Add API call here in Day 2

    Args:
        text (str): The text to summarize.

    Returns:
        str: The summary (placeholder for now).
    """
    # TODO: Add API call here in Day 2 (Anthropic SDK + prompts.SUMMARIZE_PROMPT).
    # `text` is unused until the real summarization logic lands.
    return "[Summary placeholder - API integration coming in Day 2]"


def main():
    """
    Entry point for the command-line tool.

    Expects exactly one argument: the path of the file to summarize.
    Loads the file, generates a summary, and prints it. Exits with
    status 1 (after a usage hint) when arguments are missing or invalid.
    """
    # sys.argv[0] is the script name itself, so the file path is argv[1].
    if len(sys.argv) < 2:
        print("❌ Error: No file path provided.", file=sys.stderr)
        print(USAGE, file=sys.stderr)
        sys.exit(1)

    # Batch processing isn't supported yet, so reject extra arguments
    # loudly instead of silently ignoring all but the first file.
    if len(sys.argv) > 2:
        print(
            f"❌ Error: Expected exactly one file path (got {len(sys.argv) - 1} arguments).",
            file=sys.stderr,
        )
        print(USAGE, file=sys.stderr)
        sys.exit(1)

    file_path = sys.argv[1]

    # load_file() prints its own error message on failure, so only the
    # non-zero exit code is needed here.
    text = load_file(file_path)
    if text is None:
        sys.exit(1)

    summary = summarize(text)

    print()
    print("✅ Summary:")
    print(summary)


if __name__ == "__main__":
    main()
