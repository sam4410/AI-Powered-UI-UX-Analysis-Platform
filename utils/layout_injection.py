# --- 1. Layout Tree Serializer (after Agent 1 runs) ---
def extract_layout_tree(description_output: str) -> str:
    """Extracts a structured layout tree from Agent 1 output."""
    import re
    lines = description_output.splitlines()
    tree_lines = [line for line in lines if line.strip().startswith("- ") or line.strip().startswith("  -")]
    if not tree_lines:
        return ""
    formatted_tree = "\n".join(tree_lines)
    return formatted_tree.strip()

# --- 2. Injected Prompt Example for Mockup Agent ---
def build_mockup_prompt(hierarchy_tree: str, extra_instructions: str = "") -> str:
    return f"""
You are an expert UI wireframe generator.

Use only Tailwind CSS utility classes and plain HTML.

Strictly follow the hierarchy tree provided below when organizing layout and visual structure. Your mockup must preserve the component nesting and sequence as shown. Use grid, flexbox, spacing, and container classes where necessary.

{extra_instructions}

---
UI LAYOUT TREE (Structure):
{hierarchy_tree}
---

Return only a complete HTML file starting with <!DOCTYPE html>. Do NOT include commentary or explanation.
""".strip()
