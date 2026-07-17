"""
Command-line text summarizer.

Usage:
    python main.py --file <file_path> [--length short|medium|long] [--json]
    python main.py --batch <directory> [--length short|medium|long]

Exits with status 0 on success and 1 on any error, so the tool can be
used safely in shell scripts and pipelines.
"""

import argparse
import json
import os
import sys

import httpx
from dotenv import load_dotenv
from google import genai
from google.genai import errors as genai_errors

from prompts import get_summarize_prompt

load_dotenv()

USAGE = "Usage: python main.py --file <file_path> [--json] | python main.py --batch <directory>"
MODEL_NAME = "gemini-flash-lite-latest"
LARGE_FILE_THRESHOLD = 50_000


class ArgParser(argparse.ArgumentParser):
    """ArgumentParser that keeps this project's error conventions: a
    clean one-line message on stderr (never a stack trace/usage dump)
    and exit status 1."""

    def error(self, message):
        print(f"❌ Error: {message}", file=sys.stderr)
        print(USAGE, file=sys.stderr)
        sys.exit(1)


def load_file(file_path, quiet=False):
    """
    Load text content from a file.

    Validates that the file exists, is readable as UTF-8 text, and is
    not empty. On any failure, prints a clear user-facing error message
    (never a stack trace) and returns None.

    Args:
        file_path (str): Path to the text file to load.
        quiet (bool): When True, suppress the stdout progress line
            (used for --json mode, where stdout must contain only the
            JSON object). Error output is unaffected.

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

    # Warning only (not an error): still proceed, but let the user know
    # before an unexpectedly slow/costly API call. Printed to stderr,
    # ungated by `quiet`, so it never lands in --json's stdout output.
    if len(text) > LARGE_FILE_THRESHOLD:
        print(
            f"⚠️  Warning: File is very large ({len(text):,} characters). "
            "Summarization may be slow or cost more than usual.",
            file=sys.stderr,
        )

    if not quiet:
        print(f"📖 Loaded file: {file_path}")
    return text


def summarize(text, length="medium"):
    """
    Summarize the given text using the Gemini API.

    Day 2 change: replaces the Day 1 stub with a real call to the
    Gemini API (model: gemini-flash-lite-latest) via the google-genai SDK, using
    a prompt built by prompts.get_summarize_prompt(). Like
    load_file(), this prints its own user-facing error message (never
    a stack trace) and returns None on failure; callers only need to
    check for None.

    Args:
        text (str): The text to summarize.
        length (str): Desired summary length, passed through to
            get_summarize_prompt(): "short", "medium", or "long".
            Defaults to "medium".

    Returns:
        str | None: The summary text, or None on failure.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print(
            "❌ Error: GEMINI_API_KEY not set. Add it to your .env file.",
            file=sys.stderr,
        )
        return None

    try:
        prompt = get_summarize_prompt(text=text, length=length)
    except ValueError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return None

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
    except genai_errors.ClientError as e:
        if e.code == 429:
            print(
                "❌ Error: Rate limit reached. Please wait a minute and try again.",
                file=sys.stderr,
            )
        else:
            print(
                f"❌ Error: Gemini API rejected the request: {e.message}",
                file=sys.stderr,
            )
        return None
    except genai_errors.ServerError as e:
        print(f"❌ Error: Gemini API server error: {e.message}", file=sys.stderr)
        return None
    except httpx.RequestError:
        print(
            "❌ Error: Could not reach the Gemini API. Check your network connection and try again.",
            file=sys.stderr,
        )
        return None

    summary = (response.text or "").strip()
    if not summary:
        print("❌ Error: Gemini API returned an empty response.", file=sys.stderr)
        return None

    return summary


def summarize_file(file_path, length="medium"):
    """Load a text file and summarize it, returning a result dict.

    Composes load_file() and summarize(). Both of those print their own
    user-facing error messages on failure, so this function stays quiet
    and just signals failure with None.

    Args:
        file_path (str): Path to the UTF-8 text file to summarize.
        length (str): Desired summary length, passed through to
            summarize(): "short", "medium", or "long". Defaults to
            "medium".

    Returns:
        dict | None: On success, a dict with the keys "summary",
            "word_count", "char_count", and "source_file". None on
            any failure (the failure has already been reported on
            stderr by load_file() or summarize()).

    Raises:
        Nothing: all failure modes are handled internally and
            reported as None.
    """
    text = load_file(file_path, quiet=True)
    if text is None:
        return None

    summary = summarize(text, length=length)
    if summary is None:
        return None

    return {
        "summary": summary,
        "word_count": len(summary.split()),
        "char_count": len(summary),
        "source_file": file_path,
    }


def batch_summarize_directory(directory_path, on_progress=None, length="medium"):
    """Summarize every top-level .txt file in a directory.

    Discovers .txt files directly inside directory_path (non-recursive),
    sorts them alphabetically by filename for predictable output order,
    and runs summarize_file() on each. Files that fail are still
    included in the results so the output array always has one entry
    per discovered file. This function does not print; the caller is
    responsible for presenting results and progress.

    Args:
        directory_path (str): Path to the directory to scan for .txt
            files.
        on_progress (callable | None): Optional callback invoked before
            each file is processed, as on_progress(index, total,
            filename) with a 1-based index. Used by the CLI to report
            progress without this function printing anything itself.
        length (str): Desired summary length, passed through to
            summarize_file(): "short", "medium", or "long". Defaults
            to "medium".

    Returns:
        list[dict]: One dict per .txt file, in alphabetical filename
            order. Successful files use the summarize_file() result
            shape; failed files use {"source_file": <path>,
            "error": "failed", "summary": None}.

    Raises:
        OSError: If directory_path does not exist, is not a directory,
            or cannot be read (includes FileNotFoundError,
            NotADirectoryError, and PermissionError).
    """
    with os.scandir(directory_path) as entries:
        txt_files = sorted(
            entry.name
            for entry in entries
            if entry.is_file() and entry.name.endswith(".txt")
        )

    results = []
    for index, filename in enumerate(txt_files, start=1):
        if on_progress is not None:
            on_progress(index, len(txt_files), filename)

        file_path = os.path.join(directory_path, filename)
        result = summarize_file(file_path, length=length)
        if result is None:
            result = {"source_file": file_path, "error": "failed", "summary": None}
        results.append(result)

    return results


def run_batch(directory_path, length="medium"):
    """Run batch mode: summarize a directory and print a JSON array.

    Prints progress and status lines to stderr and the full results
    array as JSON to stdout, so stdout stays machine-readable.

    Args:
        directory_path (str): Directory containing the .txt files to
            summarize.
        length (str): Desired summary length for every file: "short",
            "medium", or "long". Defaults to "medium".

    Returns:
        int: Process exit code — 0 if every file succeeded, 1 if any
            file failed or the directory could not be read.

    Raises:
        Nothing: directory read errors are caught and reported as a
            clean stderr message per project convention.
    """

    def report_progress(index, total, filename):
        print(f"⚙️ Processing {index}/{total}: {filename}", file=sys.stderr)

    try:
        results = batch_summarize_directory(
            directory_path, on_progress=report_progress, length=length
        )
    except OSError as e:
        print(
            f"❌ Error: Could not read directory {directory_path}: {e.strerror or e}",
            file=sys.stderr,
        )
        return 1

    if not results:
        print(f"❌ Error: No .txt files found in: {directory_path}", file=sys.stderr)
        return 1

    print(json.dumps(results, indent=2))

    failures = sum(1 for r in results if r.get("error") == "failed")
    if failures:
        print(
            f"❌ Batch finished with errors: {failures}/{len(results)} files failed.",
            file=sys.stderr,
        )
        return 1

    print(
        f"✅ Batch complete: {len(results)}/{len(results)} files succeeded.",
        file=sys.stderr,
    )
    return 0


def main():
    """
    Entry point for the command-line tool.

    Accepts either --file <path> (single-file mode) or --batch
    <directory> (batch mode); the two are mutually exclusive. An
    optional --length flag picks the summary size (short, medium, or
    long; default medium). In single-file mode an optional --json flag
    switches output to a single JSON object on stdout (with all
    emoji/status lines suppressed) so the result can be piped into
    other tools. Batch mode always prints a JSON array on stdout.
    Exits with status 1 (after a usage hint) when arguments are
    missing or invalid.
    """
    parser = ArgParser(
        description="Summarize a text file using the Gemini API.",
        epilog=(
            "Examples:\n"
            "  python main.py --file article.txt --json\n"
            "  python main.py --file article.txt --length short\n"
            "  python main.py --batch ./articles"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--file",
        metavar="FILE",
        help="path to the UTF-8 text file to summarize",
    )
    input_group.add_argument(
        "--batch",
        metavar="DIRECTORY",
        help="summarize every top-level .txt file in DIRECTORY and print a JSON array",
    )
    parser.add_argument(
        "--length",
        default="medium",
        help="summary length: short, medium, or long (default: medium)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="output a single JSON object on stdout instead of formatted text",
    )
    args = parser.parse_args()

    # Validated here (not via argparse choices) so the message matches
    # the project's exact error wording.
    if args.length not in ("short", "medium", "long"):
        print("❌ Error: length must be 'short', 'medium', or 'long'", file=sys.stderr)
        sys.exit(1)

    if args.batch:
        sys.exit(run_batch(args.batch, length=args.length))

    # load_file() prints its own error message on failure, so only the
    # non-zero exit code is needed here.
    text = load_file(args.file, quiet=args.json)
    if text is None:
        sys.exit(1)

    summary = summarize(text, length=args.length)
    if summary is None:
        sys.exit(1)

    if args.json:
        output = {
            "summary": summary,
            "word_count": len(summary.split()),
            "char_count": len(summary),
            "source_file": args.file,
        }
        print(json.dumps(output, indent=2))
    else:
        print()
        print("✅ Summary:")
        print(summary)


if __name__ == "__main__":
    main()
