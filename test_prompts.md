# Prompt Testing Log

Manual prompt tests are run on claude.ai (Claude Pro chat) before a version is
committed to `prompts.py`. This file records what was tested and which version won.

## Day 1 — SUMMARIZE_PROMPT

- **Versions tested:** V1 vs V2
- **Tested on:** claude.ai (Claude Pro chat)
- **Result:** V2 outperformed V1 consistently → committed to `prompts.py` as `SUMMARIZE_PROMPT`
- **V2 structure:** role framing + explicit rules + one worked example + "Return ONLY the summary" instruction

## Template for future tests

```markdown
## Day N — PROMPT_NAME

- **Versions tested:**
- **Tested on:**
- **Test inputs:**
- **Result / winner:**
- **Notes (why it won, edge cases seen):**
```
