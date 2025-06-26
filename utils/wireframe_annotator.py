import re
from bs4 import BeautifulSoup

def annotate_wireframe_with_suggestions(html: str, pm_task_output: str) -> str:
    """Annotate HTML wireframe with interactive highlights based on PM suggestions."""

    if not html or not isinstance(html, str):
        return ""

    soup = BeautifulSoup(html, "html.parser")

    # Inject interactive CSS
    interactive_css = """
    <style>
    .highlight-change {
        border: 2px solid #f39c12;
        box-shadow: 0 0 8px #f1c40f;
        position: relative;
        transition: box-shadow 0.3s ease-in-out;
    }

    .highlight-change:hover {
        box-shadow: 0 0 12px 4px #f1c40f;
        z-index: 10;
    }

    .highlight-label {
        position: absolute;
        top: -10px;
        left: -10px;
        background: #f39c12;
        color: white;
        font-size: 0.7rem;
        padding: 2px 6px;
        border-radius: 4px;
        z-index: 999;
    }

    .tooltip-box {
        display: none;
        position: absolute;
        top: -60px;
        left: 0;
        background: #333;
        color: white;
        font-size: 0.75rem;
        padding: 6px;
        border-radius: 4px;
        white-space: nowrap;
        z-index: 9999;
    }

    .highlight-change:hover .tooltip-box {
        display: block;
    }

    details.annotated-story {
        background: #fff8e1;
        padding: 0.5rem;
        border: 1px solid #f39c12;
        border-radius: 6px;
        margin-bottom: 8px;
    }
    </style>
    """

    if soup.head:
        soup.head.append(BeautifulSoup(interactive_css, "html.parser"))

    # Extract user stories
    story_blocks = re.findall(r"\d+\.\s+(As a .*?)\n", pm_task_output)
    if not story_blocks:
        story_blocks = re.findall(r"(As a .*?)\n", pm_task_output)

    matched = []

    for idx, story in enumerate(story_blocks, 1):
        match = re.search(r"I want to\s+(.*?)(?:,|\s+so that)", story)
        if not match:
            continue

        keyword = match.group(1).strip().lower()
        elements = soup.find_all(string=re.compile(re.escape(keyword), re.IGNORECASE))

        for el in elements:
            if el.parent and "highlight-change" not in el.parent.get("class", []):
                el.parent["class"] = el.parent.get("class", []) + ["highlight-change"]

                # Add badge label
                label = soup.new_tag("div", attrs={"class": "highlight-label"})
                label.string = f"#{idx}"
                el.parent.insert(0, label)

                # Tooltip preview
                tooltip = soup.new_tag("div", attrs={"class": "tooltip-box"})
                tooltip.string = story[:80] + "..." if len(story) > 80 else story
                el.parent.insert(1, tooltip)

                matched.append((idx, story))
                break

    # Add collapsible section with all stories
    if matched:
        legend = soup.new_tag("div")
        legend["style"] = "margin-top: 2rem; padding: 1rem; background: #fcf8e3; border-radius: 8px;"
        legend.append(BeautifulSoup("<h4>📝 Highlighted Changes</h4>", "html.parser"))

        for idx, story in matched:
            details = soup.new_tag("details", attrs={"class": "annotated-story"})
            summary = soup.new_tag("summary")
            summary.string = f"#{idx} – {story[:40]}..."
            details.append(summary)

            full = soup.new_tag("p")
            full.string = story
            details.append(full)

            legend.append(details)

        soup.body.append(legend)

    return str(soup)
