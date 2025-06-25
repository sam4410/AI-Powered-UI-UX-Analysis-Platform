import re

def extract_html_from_task_result(task_result) -> str:
    """
    Extract valid HTML string from a CrewAI task result.
    Handles:
    - Raw string result
    - Dict result with 'raw', 'final_output', etc.
    - Markdown-wrapped code blocks
    """
    if not task_result:
        return ""

    # Handle dict-like structure
    if isinstance(task_result, dict):
        raw_html = task_result.get("raw") or task_result.get("final_output") or ""
    else:
        raw_html = str(task_result)

    # Remove markdown code fences (```html ... ```)
    raw_html = raw_html.strip()
    if raw_html.startswith("```html"):
        raw_html = raw_html[len("```html"):].strip()
    if raw_html.endswith("```"):
        raw_html = raw_html[:-3].strip()

    # Sanity check
    if "<html" not in raw_html and "<!DOCTYPE html>" not in raw_html:
        return ""

    return raw_html
