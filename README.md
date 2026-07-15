# Text Summarizer

A command-line tool that turns long text files into clear 2–3 sentence summaries.

## What problem does it solve?

Reading long documents takes time. Whether it's a report, an article, or meeting notes, most of us just want the key points — fast. This tool takes any plain text file and produces a short, accurate summary, so you can understand a document in seconds instead of minutes. No copy-pasting into a chat window, no manual skimming.

## Installation

```bash
pip install -r requirements.txt
```

Requires Python 3.8 or newer, and a `GEMINI_API_KEY` in a `.env` file in the project root.

## Usage

```bash
python main.py filename.txt
```

Point it at any plain text file and it prints a summary to the terminal.

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

## Current status

**Done**
- [x] Project structure
- [x] File loading with validation
- [x] Error handling (missing, empty, or invalid files)
- [x] Prompt engineering (tested and versioned)
- [x] API integration (Gemini API)

**Coming**
- [ ] JSON output
- [ ] Batch processing (summarize multiple files at once)

## Notes

- The summarization prompt lives in `prompts.py` and has been tested manually; the winning version is committed with notes on why it won.
- API calls use the Gemini API (`google-genai` SDK) and require a `GEMINI_API_KEY` set in a `.env` file (see `python-dotenv` in `requirements.txt`).
