# Text Summarizer

A command-line tool that turns long text files into clear 2–3 sentence summaries.

## What problem does it solve?

Reading long documents takes time. Whether it's a report, an article, or meeting notes, most of us just want the key points — fast. This tool takes any plain text file and produces a short, accurate summary, so you can understand a document in seconds instead of minutes. No copy-pasting into a chat window, no manual skimming.

## Why this tool?

- **A prompt that was actually tested, not guessed.** The summarization prompt was iterated and compared version-against-version before being committed — see [How it works](#how-it-works) and `test_prompts.md`.
- **Built for pipelines.** A `--json` mode emits clean, machine-readable output on stdout, and a predictable exit code on every path — drop it straight into a shell script.
- **Fails gracefully, never crashes.** Every error is a clear one-line message, never a stack trace. See [Error handling](#error-handling).
- **Zero-friction demo.** A `sample.txt` ships with the project, so you can run a real summary the moment you clone it.

## Quick start

```bash
pip install -r requirements.txt        # install dependencies
echo "GEMINI_API_KEY=your-key" > .env  # add your Gemini API key
python main.py sample.txt              # summarize the bundled sample
```

## Installation

```bash
pip install -r requirements.txt
```

Requires Python 3.8 or newer, and a `GEMINI_API_KEY` in a `.env` file in the project root. See [Requirements](#requirements) for the full list.

## Usage

```bash
python main.py filename.txt
```

Point it at any plain text file and it prints a summary to the terminal. Try it right away with the bundled sample:

```bash
python main.py sample.txt
```

Add `--json` to get a single JSON object on stdout instead (summary, word count, char count, source file) for piping into other tools:

```bash
python main.py filename.txt --json
```

## Example

**Input** (`article.txt`):

> The city council met on Tuesday to discuss the proposed downtown redevelopment plan. The plan includes new bike lanes, expanded green space, and mixed-use housing. Several residents voiced concerns about parking availability and construction noise. The council responded that a parking study is already underway and construction would be limited to daytime hours. A final vote is scheduled for next month, and if approved, construction would begin in early spring.

**Output:**

```
📖 Loaded file: article.txt

✅ Summary:
The city council reviewed a downtown redevelopment plan featuring bike lanes,
green space, and mixed-use housing, while addressing resident concerns about
parking and noise. A final vote is scheduled for next month, with construction
potentially starting in early spring.
```

The summary above is real output from the Gemini API using the tested prompt.

### JSON output

With `--json`, the same run prints a single JSON object on stdout — and nothing else, so it's safe to pipe into `jq` or another tool:

```bash
python main.py article.txt --json
```

```json
{
  "summary": "The city council reviewed a downtown redevelopment plan featuring bike lanes, green space, and mixed-use housing, while addressing resident concerns about parking and noise. A final vote is scheduled for next month, with construction potentially starting in early spring.",
  "word_count": 39,
  "char_count": 268,
  "source_file": "article.txt"
}
```

In JSON mode the progress and success lines are suppressed so stdout stays valid JSON; any warnings or errors still go to stderr.

## Error handling

The tool is built for use in scripts and pipelines, so failures are predictable:

- **Clean messages, no stack traces.** Every failure prints a single `❌`-prefixed line to stderr and exits with status `1`, so a successful run is unambiguous.
- **File problems are caught explicitly** — missing file, a directory instead of a file, no read permission, binary/non-UTF-8 content, and empty (or whitespace-only) files each get their own clear message.
- **API problems are handled gracefully** — a missing `GEMINI_API_KEY`, rate limits, Gemini server errors, network failures, and empty API responses all produce a plain-English message instead of a crash.
- **Large files warn but don't block** — files over ~50,000 characters print a `⚠️` warning to stderr (the run still proceeds), so an unexpectedly slow or costly call doesn't catch you off guard.

Because errors and warnings go to stderr and never to stdout, `--json` output stays clean even when something goes wrong.

### Exit codes

| Code | Meaning |
|------|---------|
| `0`  | Success — a summary was produced |
| `1`  | Any failure — bad arguments, an unreadable/empty file, or an API error |

This makes the tool safe to chain in scripts: `python main.py doc.txt && echo "done"` only runs the next step on success.

## How it works

1. **Load & validate** — the input file is read as UTF-8 and checked for the failure cases above before anything else happens.
2. **Prompt** — the text is dropped into `SUMMARIZE_PROMPT`, a template using role framing, explicit rules, and one worked example. This prompt was iterated version-against-version on claude.ai and the winner committed; the process is logged in `test_prompts.md`.
3. **Summarize** — the prompt is sent to the Gemini API (`gemini-flash-latest`) via the `google-genai` SDK.
4. **Output** — the result prints as a formatted summary, or as a JSON object with `--json`.

## Project structure

```
text-summarizer/
├── main.py            # CLI: argument parsing, file loading, API call, output
├── prompts.py         # Versioned, manually tested prompt templates
├── test_prompts.md    # Log of prompt tests and which version won
├── sample.txt         # Bundled example input for a zero-setup demo
├── requirements.txt   # Dependencies: google-genai, python-dotenv
└── README.md          # This file
```

## Requirements

- Python 3.8+
- A Gemini API key in a `.env` file (`GEMINI_API_KEY=...`)
- Dependencies (`pip install -r requirements.txt`): `google-genai`, `python-dotenv`

## Current status

**Done**
- [x] Project structure
- [x] File loading with validation
- [x] Error handling (missing, empty, or invalid files)
- [x] Prompt engineering (tested and versioned)
- [x] API integration (Gemini API)
- [x] JSON output

**Coming**
- [ ] Batch processing (summarize multiple files at once)

## Notes

- The summarization prompt lives in `prompts.py` and has been tested manually; the winning version is committed with notes on why it won.
- API calls use the Gemini API (`google-genai` SDK) and require a `GEMINI_API_KEY` set in a `.env` file (see `python-dotenv` in `requirements.txt`).
