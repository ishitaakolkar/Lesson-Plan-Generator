from __future__ import annotations
from typing import Dict, Any

SECTION_ORDER = [
    "Unit Overview",
    "Learning Outcomes",
    "Prerequisites",
    "Materials",
    "Lesson Flow",
    "Differentiation",
    "Assessment",
    "Homework/Extensions",
    "References",
]

def to_markdown(plan: Dict[str, Any]) -> str:
    lines = [f"# {plan.get('title','Lesson Plan')}\n"]
    for section in SECTION_ORDER:
        content = plan.get("sections", {}).get(section)
        if content:
            lines.append(f"## {section}\n")
            if isinstance(content, list):
                for item in content:
                    lines.append(f"- {item}")
            else:
                lines.append(str(content))
            lines.append("")
    return "\n".join(lines).strip()