# Text Summarizer

A command-line tool that turns long text files into clear 2–3 sentence summaries.

## What problem does it solve?

Reading long documents takes time. Whether it's a report, an article, or meeting notes, most of us just want the key points — fast. This tool takes any plain text file and produces a short, accurate summary, so you can understand a document in seconds instead of minutes. No copy-pasting into a chat window, no manual skimming.

## Installation

```bash
pip install -r requirements.txt
```

Requires Python 3.8 or newer.

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

> **Note:** The summary above shows the target output once API integration
> lands (see *Current status* below). The current build prints a placeholder
> summary while prompts are being tested in Claude Pro chat.

## Current status

**Done**
- [x] Project structure
- [x] File loading with validation
- [x] Error handling (missing, empty, or invalid files)
- [x] Prompt engineering (tested and versioned)

**Coming**
- [ ] API integration
- [ ] JSON output
- [ ] Batch processing (summarize multiple files at once)

## Notes

- **No paid API costs so far** — prompt development and testing is done through Claude Pro chat during this phase.
- The summarization prompt lives in `prompts.py` and has been tested manually; the winning version is committed with notes on why it won.
- API integration is the next milestone, at which point the SDK dependency will be added to `requirements.txt`.
