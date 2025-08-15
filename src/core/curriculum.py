from __future__ import annotations
from typing import Dict, List

BOARDS = [
    "CBSE",
    "ICSE",
    "State Board",
    "IB",
]

SUBJECTS: Dict[str, List[str]] = {
    "CBSE": ["Mathematics", "Science", "English", "Social Science", "Computer Science"],
    "ICSE": ["Mathematics", "Physics", "Chemistry", "Biology", "English", "History & Civics"],
    "State Board": ["Mathematics", "Science", "English", "Gujarati/Hindi", "Social Science"],
    "IB": ["Mathematics", "Sciences", "Language & Literature", "Individuals & Societies"],
}

BLOOMS_LEVELS = [
    "Remember",
    "Understand",
    "Apply",
    "Analyze",
    "Evaluate",
    "Create",
]

PEDAGOGY_STYLES = [
    "Direct Instruction",
    "Inquiry-Based",
    "Project-Based",
    "Flipped Classroom",
    "Experiential",
]

DURATIONS = ["30 min", "40 min", "45 min", "60 min", "90 min"]