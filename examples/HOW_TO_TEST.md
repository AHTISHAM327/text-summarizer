# Text Summarizer — Examples & Test Guide

Run all commands from inside your `text-summarizer/` project root with your `.env` present.

---

## 1. Quick smoke test

```bash
python main.py --file examples/04_short_paragraph.txt
```

---

## 2. All three --length modes

```bash
python main.py --file examples/01_news_article.txt --length short
python main.py --file examples/01_news_article.txt --length medium
python main.py --file examples/01_news_article.txt --length long
```

---

## 3. JSON mode (stdout must be clean JSON)

```bash
python main.py --file examples/02_research_paper_abstract.txt --json
```

Pipe test:
```bash
python main.py --file examples/03_meeting_notes.txt --json | python -c "import sys,json; print(json.load(sys.stdin)['summary'])"
```

---

## 4. Different content types

```bash
python main.py --file examples/01_news_article.txt          # news article
python main.py --file examples/02_research_paper_abstract.txt  # technical academic
python main.py --file examples/03_meeting_notes.txt         # meeting notes
python main.py --file examples/04_short_paragraph.txt       # short input
python main.py --file examples/05_customer_feedback.txt     # structured feedback
python main.py --file examples/06_technical_doc.txt         # engineering doc
```

---

## 5. Batch mode

```bash
python main.py --batch examples/batch_docs/
python main.py --batch examples/batch_docs/ --length short
```

Extract just summaries from batch output:
```bash
python main.py --batch examples/batch_docs/ 2>/dev/null | python -c "
import sys, json
for r in json.load(sys.stdin):
    print(r['source_file'], '->', r['summary'][:80], '...')
"
```

---

## 6. Edge cases — error handling

```bash
# Empty file → "File is empty" error, exit 1
python main.py --file examples/edge_cases/empty_file.txt

# Whitespace-only → same as empty (tests .strip() logic)
python main.py --file examples/edge_cases/whitespace_only.txt

# Large file → ⚠️ warning printed, but still runs
python main.py --file examples/edge_cases/large_file_warning_trigger.txt --length short

# Missing file → "File not found" error, exit 1
python main.py --file examples/does_not_exist.txt

# Directory passed as --file → clean error, exit 1
python main.py --file examples/batch_docs/

# Invalid length → clean error, exit 1
python main.py --file examples/04_short_paragraph.txt --length huge

# --file and --batch together → argparse error, exit 1
python main.py --file examples/04_short_paragraph.txt --batch examples/batch_docs/
```

---

## 7. Exit code check

```bash
python main.py --file examples/04_short_paragraph.txt && echo "EXIT 0 ✅" || echo "EXIT 1 ❌"
python main.py --file examples/edge_cases/empty_file.txt && echo "EXIT 0 ✅" || echo "EXIT 1 ❌"
```
