from __future__ import annotations
from typing import Dict, Any, List
import google.generativeai as genai
from pydantic import BaseModel, Field
from .config import GEMINI_API_KEY, DEFAULT_MODEL

class LessonRequest(BaseModel):
    board: str
    grade: int
    subject: str
    topic: str
    duration: str
    pedagogy: str
    bloom: str
    learning_objectives: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)

class LessonPlan(BaseModel):
    title: str
    sections: Dict[str, Any]

PROMPT = """
You are an expert teacher. Create a concise, actionable lesson plan.
Return JSON with fields: title (string), sections (object) containing keys
Unit Overview, Learning Outcomes, Prerequisites, Materials, Lesson Flow, Differentiation, Assessment, Homework/Extensions, References.
Keep lists as arrays of bullet points where appropriate. Avoid overlong prose.
Context:
- Board: {board}
- Grade: {grade}
- Subject: {subject}
- Topic: {topic}
- Duration: {duration}
- Pedagogy: {pedagogy}
- Bloom: {bloom}
- Learning Objectives: {objectives}
- Constraints: {constraints}
Ensure age-appropriate language and alignment to the board.
"""

def _client():
    genai.configure(api_key=GEMINI_API_KEY)
    return genai.GenerativeModel(DEFAULT_MODEL)


def generate_lesson(data: LessonRequest) -> LessonPlan:
    model = _client()
    prompt = PROMPT.format(
        board=data.board,
        grade=data.grade,
        subject=data.subject,
        topic=data.topic,
        duration=data.duration,
        pedagogy=data.pedagogy,
        bloom=data.bloom,
        objectives=", ".join(data.learning_objectives) or "-",
        constraints=", ".join(data.constraints) or "-",
    )
    resp = model.generate_content(prompt)
    text = resp.text or "{}"

    # Model sometimes wraps JSON in code fences
    import json, re
    cleaned = re.sub(r"^```(json)?|```$", "", text.strip(), flags=re.MULTILINE)
    payload = json.loads(cleaned)

    return LessonPlan(**payload)