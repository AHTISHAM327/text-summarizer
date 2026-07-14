"""
Prompt templates for the Text Summarizer.
Tested on claude.ai on Day 1 — V2 outperformed V1 consistently.
"""

SUMMARIZE_PROMPT = """You are a skilled text summarizer.

Task: Write a 2-3 sentence summary of the text below.
Rules:
- Keep only the main idea
- Remove filler, opinions, and repeated points
- Write in clear, simple language
- Return ONLY the summary. No preamble, no explanation.

Example:
Input: "The weather has been strange. It rained for three days straight.
My basement flooded. The city says climate change is the cause. Experts
agree. Some don't. Anyway it was a lot of rain."
Output: "The city experienced severe rainfall that caused flooding.
Officials and experts attribute the unusual weather to climate change."

Now summarize this:
{text}"""
