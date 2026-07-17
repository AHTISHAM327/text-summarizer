# Text Summarizer CLI

> AI-powered summarization for documents and folders. Runs locally — no data leaves your machine except the text you send to the API.

## What It Does

Takes any `.txt` file (or a folder of `.txt` files) and returns a clean, concise summary using Google Gemini. Supports three output lengths and structured JSON output for pipeline integration.

**Built for:**

- Summarizing research papers, reports, and meeting notes
- Batch-processing folders of articles, customer feedback, or support tickets
- Integrating into existing scripts and pipelines via `--json` and clean exit codes

## Features

| Feature          | Description                                                                                                    |
| ---------------- | -------------------------------------------------------------------------------------------------------------- |
| Single file mode | `--file path/to/doc.txt`                                                                                       |
| Batch mode       | `--batch path/to/folder/` — processes every top-level `.txt` file                                              |
| Length control   | `--length short / medium / long`                                                                               |
| JSON output      | `--json` returns a structured object with `word_count`, `char_count`                                           |
| Error-safe       | Clean one-line messages for missing files, empty inputs, API errors — never a stack trace                      |
| Exit codes       | `0` on success, `1` on any failure (pipeline-friendly)                                                         |
| Tested prompts   | The summarization prompt was iterated version-against-version and the winner committed (see `test_prompts.md`) |

## Setup

**Requirements:** Python 3.9+, a free [Google AI Studio API key](https://aistudio.google.com/apikey)

```bash
git clone https://github.com/YOUR_USERNAME/text-summarizer.git
cd text-summarizer
python3 -m pip install -r requirements.txt
```

Create a `.env` file in the project root and add your key:

```
GEMINI_API_KEY=your_key_here
```

Then try it immediately with the bundled sample:

```bash
python3 main.py --file sample.txt
```

## Usage

**Single file:**

```bash
python3 main.py --file path/to/document.txt
python3 main.py --file report.txt --length short
python3 main.py --file report.txt --json
```

**Batch mode (entire folder):**

```bash
python3 main.py --batch ./documents/
python3 main.py --batch ./documents/ --length short
```

Batch mode always prints a JSON array to stdout (one entry per file, in alphabetical order) with progress lines on stderr, so the output stays machine-readable.

**Flags:**

| Flag       | Values                    | Default  | Description                                                      |
| ---------- | ------------------------- | -------- | ---------------------------------------------------------------- |
| `--file`   | file path                 | —        | Single file to summarize                                         |
| `--batch`  | directory path            | —        | Process all top-level `.txt` files in a folder                   |
| `--length` | `short`, `medium`, `long` | `medium` | Summary length                                                   |
| `--json`   | —                         | off      | Single-file mode: output a JSON object instead of formatted text |

`--file` and `--batch` are mutually exclusive; exactly one is required.

## Example Output

**Input** (`article.txt`):

> The city council met on Tuesday to discuss the proposed downtown redevelopment plan. The plan includes new bike lanes, expanded green space, and mixed-use housing. Several residents voiced concerns about parking availability and construction noise. A final vote is scheduled for next month.

**`python3 main.py --file article.txt`:**

```
📖 Loaded file: article.txt

✅ Summary:
The city council reviewed a downtown redevelopment plan featuring bike lanes,
green space, and mixed-use housing, while addressing resident concerns about
parking and noise. A final vote is scheduled for next month.
```

**`python3 main.py --file article.txt --json`:**

```json
{
  "summary": "The city council reviewed a downtown redevelopment plan featuring bike lanes, green space, and mixed-use housing, while addressing resident concerns about parking and noise. A final vote is scheduled for next month.",
  "word_count": 33,
  "char_count": 216,
  "source_file": "article.txt"
}
```

In JSON mode the progress and success lines are suppressed so stdout stays valid JSON; warnings and errors still go to stderr.

## Error Handling

Built for scripts and pipelines, so failures are predictable:

- **Clean messages, no stack traces.** Every failure prints a single `❌`-prefixed line to stderr and exits with status `1`.
- **File problems are caught explicitly** — missing file, directory instead of a file, no read permission, binary/non-UTF-8 content, and empty files each get their own clear message.
- **API problems are handled gracefully** — a missing `GEMINI_API_KEY`, rate limits, server errors, network failures, and empty responses all produce a plain-English message instead of a crash.
- **Large files warn but don't block** — files over ~50,000 characters print a `⚠️` warning to stderr and the run proceeds.
- **Batch keeps going** — a failed file is recorded in the results array (`"error": "failed"`) and the remaining files are still processed; the run exits `1` if any file failed.

## Tech Stack

- **LLM:** Google Gemini (`gemini-flash-lite-latest`, free tier via the `google-genai` SDK)
- **Prompt design:** Versioned, manually tested prompt templates in `prompts.py`, separated from logic — test rounds logged in `test_prompts.md`
- **Error handling:** All file and API errors caught; stack traces never reach the user

## Project Structure

```
text-summarizer/
├── main.py            # CLI entry point: argument parsing, file loading, API call, output
├── prompts.py         # All prompt templates (no logic), versioned and tested
├── test_prompts.md    # Log of prompt tests and which version won
├── sample.txt         # Bundled example input for a zero-setup demo
├── requirements.txt   # Dependencies: google-genai, python-dotenv
└── README.md          # This file
```

## License

MIT
