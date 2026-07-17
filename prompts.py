"""Prompt templates for the text-summarizer tool. All prompt construction
goes here — never in main.py.

History: the "medium" prompt preserves the V2 body tested on claude.ai on
Day 1 (V2 outperformed V1 consistently). The "short" and "long" variants
are new and not yet tested — log rounds in test_prompts.md before relying
on them.
"""

# Per-length task line and extra rules. Each entry keeps the structure that
# tested well: explicit task, rules list, then the "Return ONLY" instruction
# (added in the shared skeleton below).
_LENGTH_SPECS = {
    "short": {
        "task": "Write exactly 1 sentence (max 25 words) summarizing the text below.",
        "rules": [
            "Keep only the single most important idea",
            "No bullet points, no preamble",
        ],
        "example": None,
    },
    "medium": {
        "task": "Write a 2-3 sentence summary of the text below.",
        "rules": [
            "Keep only the main idea",
            "Remove filler, opinions, and repeated points",
            "Write in clear, simple language",
            "No bullet points, no preamble",
        ],
        # Worked example carried over verbatim from the tested V2 prompt.
        "example": (
            'Input: "The weather has been strange. It rained for three days straight.\n'
            "My basement flooded. The city says climate change is the cause. Experts\n"
            'agree. Some don\'t. Anyway it was a lot of rain."\n'
            'Output: "The city experienced severe rainfall that caused flooding.\n'
            'Officials and experts attribute the unusual weather to climate change."'
        ),
    },
    "long": {
        "task": (
            "Write a single paragraph of 5-7 sentences summarizing the text below, "
            "covering the main points, key examples, and the conclusion."
        ),
        "rules": [
            "Cover the main points, notable examples, and the conclusion",
            "Remove filler, opinions, and repeated points",
            "Write in clear, simple language",
            "No bullet points, no preamble — one flowing paragraph",
        ],
        "example": None,
    },
}


def get_summarize_prompt(text: str, length: str = "medium") -> str:
    """Build a summarization prompt sized to the requested summary length.

    Args:
        text (str): The document text to summarize. It is embedded
            directly in the returned prompt (no .format() placeholders
            remain).
        length (str): Desired summary length. One of "short" (exactly
            1 sentence, max 25 words), "medium" (2-3 sentences), or
            "long" (a 5-7 sentence paragraph covering main points,
            examples, and conclusion). Defaults to "medium".

    Returns:
        str: A complete, ready-to-send prompt containing the summarizer
            role, the length-specific task and rules, the "Return ONLY
            the summary" instruction, and the text to summarize.

    Raises:
        ValueError: If length is not "short", "medium", or "long".
    """
    spec = _LENGTH_SPECS.get(length)
    if spec is None:
        raise ValueError("length must be 'short', 'medium', or 'long'")

    rules = "\n".join(f"- {rule}" for rule in spec["rules"])
    example_block = f"\nExample:\n{spec['example']}\n" if spec["example"] else ""

    return (
        "You are a professional document summarizer.\n"
        "\n"
        f"Task: {spec['task']}\n"
        "Rules:\n"
        f"{rules}\n"
        "- Return ONLY the summary. No preamble, no labels, no markdown.\n"
        f"{example_block}"
        "\n"
        "Text to summarize:\n"
        f"{text}"
    )
