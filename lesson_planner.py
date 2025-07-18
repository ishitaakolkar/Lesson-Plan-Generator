import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
import re
from fpdf import FPDF
from docx import Document
from io import BytesIO

# --- CONFIGURATION & API SETUP ---
load_dotenv()
try:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        st.error("Error: GOOGLE_API_KEY not found in .env file.")
        st.stop()
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
except Exception as e:
    st.error(f"Error configuring the API: {e}")
    st.stop()

# --- NEW: Data for Dynamic Subject Dropdowns ---
SUBJECTS_DATA = {
    'CBSE': {
        'Primary (1-5)': ['English', 'Hindi', 'Mathematics', 'Environmental Science (EVS)'],
        'Middle (6-8)': ['English', 'Hindi', 'Mathematics', 'Science', 'Social Science', 'Sanskrit'],
        'Secondary (9-10)': ['English', 'Hindi', 'Mathematics', 'Science', 'Social Science'],
        'Senior Secondary (11-12)': ['Physics', 'Chemistry', 'Mathematics', 'Biology', 'Computer Science', 'Accountancy', 'Business Studies', 'Economics', 'English', 'History', 'Political Science', 'Geography']
    },
    'GSEB': {
        'Primary (1-5)': ['Gujarati', 'English', 'Mathematics', 'Environmental Science (Paryavaran)'],
        'Middle (6-8)': ['Gujarati', 'English', 'Mathematics', 'Science (Vigyan)', 'Social Science (Samajik Vigyan)', 'Sanskrit'],
        'Secondary (9-10)': ['Gujarati', 'English', 'Mathematics', 'Science', 'Social Science'],
        'Senior Secondary (11-12)': ['Physics', 'Chemistry', 'Mathematics', 'Biology', 'Computer Science', 'Accountancy', 'Business Studies', 'Economics', 'English', 'Gujarati', 'History', 'Political Science', 'Geography']
    }
}
GRADES_MAPPING = {
    'Nursery': 'Primary (1-5)', 'LKG': 'Primary (1-5)', 'UKG': 'Primary (1-5)',
    '1st Grade': 'Primary (1-5)', '2nd Grade': 'Primary (1-5)', '3rd Grade': 'Primary (1-5)', '4th Grade': 'Primary (1-5)', '5th Grade': 'Primary (1-5)',
    '6th Grade': 'Middle (6-8)', '7th Grade': 'Middle (6-8)', '8th Grade': 'Middle (6-8)',
    '9th Grade': 'Secondary (9-10)', '10th Grade': 'Secondary (9-10)',
    '11th Grade': 'Senior Secondary (11-12)', '12th Grade': 'Senior Secondary (11-12)'
}

# --- HELPER FUNCTIONS ---
def generate_lesson_plan(board, grade, subject, topic, objective):
    prompt = f"""
    As an expert curriculum designer for the {board} board in India, create a 15-minute micro-lesson plan for {grade}, focusing on the subject of {subject}.

    **Topic:** {topic}
    **Objective:** By the end of this lesson, students should be able to {objective}.

    Generate the output in simple Markdown. Use these exact headings for each section: '### 📝 Introduction (3 Minutes)', '### 🎯 Main Activity (9 Minutes)', and '### ✨ Conclusion (3 Minutes)'.
    Under each heading, provide a clear, concise, and actionable plan.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"An error occurred: {e}"

# --- NEW: PDF & DOCX Generation Functions ---
def create_pdf(text_content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    # Replace markdown bolding with nothing for plain text in PDF
    text_content = re.sub(r'\*\*(.*?)\*\*', r'\1', text_content)
    for line in text_content.split('\n'):
        pdf.multi_cell(0, 10, line)
    return pdf.output(dest='S').encode('latin-1')

def create_docx(text_content):
    doc = Document()
    # Replace markdown bolding with nothing for plain text in docx
    text_content = re.sub(r'\*\*(.*?)\*\*', r'\1', text_content)
    doc.add_paragraph(text_content)
    bio = BytesIO()
    doc.save(bio)
    return bio.getvalue()

# --- STREAMLIT UI ---
st.set_page_config(page_title="Smart Lesson Planner", page_icon="🧑‍🏫")
st.title("🧑‍🏫 Smart Lesson Planner for Indian Schools")
st.write("Generate engaging 15-minute lesson plans tailored to your board and grade.")

# --- UPDATED: Dynamic UI Elements ---
boards = list(SUBJECTS_DATA.keys())
grades = list(GRADES_MAPPING.keys())

col1, col2 = st.columns(2)
with col1:
    board = st.selectbox("Select Educational Board", boards)
with col2:
    grade = st.selectbox("Select Grade", grades)

# Get the correct subject list based on selections
grade_category = GRADES_MAPPING[grade]
subject_list = SUBJECTS_DATA[board][grade_category]
subject = st.selectbox("Select Subject", subject_list)

topic = st.text_input("Lesson Topic", placeholder="e.g., 'The Water Cycle'")
objective = st.text_area("Learning Objective", placeholder="e.g., 'describe the stages of evaporation and condensation'")

if st.button("🚀 Generate Lesson Plan"):
    if all([board, grade, subject, topic, objective]):
        with st.spinner("🧠 The AI is thinking..."):
            lesson_plan = generate_lesson_plan(board, grade, subject, topic, objective)
            st.session_state.lesson_plan = lesson_plan # Save to session state
    else:
        st.warning("Please fill in all fields above.", icon="⚠️")

# --- NEW: Display Output, Copy, and Download Buttons ---
if 'lesson_plan' in st.session_state and st.session_state.lesson_plan:
    st.markdown("---")
    st.subheader("Your AI-Generated Lesson Plan")

    plan_text = st.session_state.lesson_plan
    
    # Visually appealing layout
    try:
        intro_match = re.search(r'### 📝 Introduction \(3 Minutes\）\n(.*?)(?=\n###|$)', plan_text, re.S)
        activity_match = re.search(r'### 🎯 Main Activity \(9 Minutes\）\n(.*?)(?=\n###|$)', plan_text, re.S)
        conclusion_match = re.search(r'### ✨ Conclusion \(3 Minutes\）\n(.*?)(?=\n###|$)', plan_text, re.S)

        intro = intro_match.group(1).strip() if intro_match else ""
        activity = activity_match.group(1).strip() if activity_match else ""
        conclusion = conclusion_match.group(1).strip() if conclusion_match else ""

        with st.container(border=True):
            st.markdown("#### 📝 Introduction (3 Mins)")
            st.write(intro)
        
        with st.container(border=True):
            st.markdown("#### 🎯 Main Activity (9 Mins)")
            st.write(activity)

        with st.container(border=True):
            st.markdown("#### ✨ Conclusion (3 Mins)")
            st.write(conclusion)
            
    except Exception as e:
        # Fallback for any parsing error
        st.markdown(plan_text)

    st.markdown("---")
    
    # Copy to clipboard
    st.write("Copy the full lesson plan text below:")
    st.code(plan_text, language='markdown')

    # Download buttons
    st.write("Or download the file:")
    col1_dl, col2_dl = st.columns(2)
    with col1_dl:
        pdf_data = create_pdf(plan_text)
        st.download_button(
            label="⬇️ Download as PDF",
            data=pdf_data,
            file_name=f"{topic}_lesson_plan.pdf",
            mime="application/pdf"
        )
    with col2_dl:
        docx_data = create_docx(plan_text)
        st.download_button(
            label="⬇️ Download as Word (DOCX)",
            data=docx_data,
            file_name=f"{topic}_lesson_plan.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )