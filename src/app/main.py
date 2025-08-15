from __future__ import annotations
import os
import streamlit as st
from typing import List
from datetime import datetime

from core.config import APP_NAME
from core.curriculum import BOARDS, SUBJECTS, BLOOMS_LEVELS, PEDAGOGY_STYLES, DURATIONS
from core.generator import LessonRequest, generate_lesson
from core.utils import to_markdown
from core.export import to_docx, to_pdf

st.set_page_config(page_title=APP_NAME, page_icon="📚", layout="centered")

st.title("📚 PLANIT — Smart Lesson Planner")
st.caption("Aligned to boards. Built for teachers.")

with st.form("controls"):
    col1, col2 = st.columns(2)
    with col1:
        board = st.selectbox("Board", BOARDS, index=0)
        grade = st.number_input("Grade", min_value=1, max_value=12, value=5)
        subject = st.selectbox("Subject", SUBJECTS.get(board, SUBJECTS["CBSE"]))
        duration = st.selectbox("Duration", DURATIONS, index=2)
    with col2:
        topic = st.text_input("Topic", placeholder="Fractions / Photosynthesis / Nouns…")
        pedagogy = st.selectbox("Pedagogy", PEDAGOGY_STYLES, index=1)
        bloom = st.selectbox("Bloom's Level", BLOOMS_LEVELS, index=2)

    learning_objectives = st.tags_input("Learning Objectives", suggestions=["Identify", "Explain", "Apply"]) if hasattr(st, 'tags_input') else st.text_area("Learning Objectives (comma-separated)")
    constraints = st.text_area("Constraints (resources, class size, notes)")

    submitted = st.form_submit_button("Generate Lesson Plan", use_container_width=True)

if submitted:
    if isinstance(learning_objectives, str):
        los: List[str] = [x.strip() for x in learning_objectives.split(",") if x.strip()]
    else:
        los = learning_objectives

    req = LessonRequest(
        board=board,
        grade=int(grade),
        subject=subject,
        topic=topic.strip(),
        duration=duration,
        pedagogy=pedagogy,
        bloom=bloom,
        learning_objectives=los,
        constraints=[c.strip() for c in constraints.splitlines() if c.strip()],
    )

    with st.spinner("Thinking…"):
        plan = generate_lesson(req)

    st.success("Lesson plan ready.")
    md = to_markdown(plan.model_dump())
    st.markdown(md)

    colx, coly = st.columns(2)
    now = datetime.now().strftime("%Y%m%d_%H%M")
    base = f"{req.subject}_{req.topic}_{now}".replace(" ", "_")

    with colx:
        if st.button("Export DOCX", use_container_width=True):
            out = to_docx(plan.model_dump(), path=f"{base}.docx")
            with open(out, "rb") as f:
                st.download_button("Download .docx", data=f, file_name=os.path.basename(out), mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)

    with coly:
        if st.button("Export PDF", use_container_width=True):
            out = to_pdf(plan.model_dump(), path=f"{base}.pdf")
            with open(out, "rb") as f:
                st.download_button("Download .pdf", data=f, file_name=os.path.basename(out), mime="application/pdf", use_container_width=True)

st.divider()
st.caption("Made with ❤️ for teachers. SDG4: Quality Education.")