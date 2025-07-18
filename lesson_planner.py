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

# --- Data for Dynamic Dropdowns ---
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

    Generate the output in simple Markdown. Use these exact headings for each section: '### 📝 Introduction', '### 🎯 Main Activity', and '### ✨ Conclusion'.
    Under each heading, provide a clear, concise, and actionable plan.
    """
    try:
        response = model.generate_content(prompt, request_options={'timeout': 60})
        return response.text
    except Exception as e:
        return f"An error occurred: {e}"

# --- UPDATED: PDF & DOCX Generation Functions ---
def create_pdf(text_content):
    pdf = FPDF()
    pdf.add_page()
    # Add the Unicode font (assuming DejaVuSans.ttf is in the same directory)
    try:
        pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
        pdf.set_font('DejaVu', size=12)
    except RuntimeError:
        # Fallback to Arial if font file is not found
        pdf.set_font("Arial", size=12)
        st.warning("Font 'DejaVuSans.ttf' not found. PDF will not render emojis correctly. Please download it as instructed.", icon="⚠️")
        
    # Clean up the text for PDF
    text_for_pdf = re.sub(r'### (.*?)\n', r'\1\n\n', text_content) # Make headings bold
    text_for_pdf = text_for_pdf.replace('**', '') # Remove bold markdown
    
    pdf.multi_cell(0, 10, text_for_pdf)
    return pdf.output(dest='S').encode('latin-1')

def create_docx(text_content):
    doc = Document()
    # Clean up the text for DOCX
    text_for_docx = re.sub(r'### (.*?)\n', r'\1\n\n', text_content)
    text_for_docx = text_for_docx.replace('**', '')
    doc.add_paragraph(text_for_docx)
    bio = BytesIO()
    doc.save(bio)
    return bio.getvalue()

# --- STREAMLIT UI ---
st.set_page_config(layout="wide", page_title="Smart Lesson Planner", page_icon="🧑‍🏫")

# --- NEW: Custom CSS for visual appeal ---
st.markdown("""
    <style>
    .stDeployButton {
        visibility: hidden;
    }
    .stExpander {
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("Smart Lesson Planner")

with st.container(border=True):
    st.subheader("1. Select Your Class Details")
    col1, col2, col3 = st.columns(3)
    with col1:
        board = st.selectbox("Educational Board", list(SUBJECTS_DATA.keys()))
    with col2:
        grade = st.selectbox("Grade", list(GRADES_MAPPING.keys()))
    with col3:
        grade_category = GRADES_MAPPING[grade]
        subject_list = SUBJECTS_DATA[board][grade_category]
        subject = st.selectbox("Subject", subject_list)

    st.subheader("2. Define Your Lesson")
    topic = st.text_input("Lesson Topic", placeholder="e.g., 'The Water Cycle'")
    objective = st.text_area("Learning Objective", placeholder="e.g., 'describe the stages of evaporation and condensation'")

    if st.button("🚀 Generate Lesson Plan", type="primary", use_container_width=True):
        if all([board, grade, subject, topic, objective]):
            with st.spinner("🧠 The AI is thinking... this may take a moment."):
                lesson_plan = generate_lesson_plan(board, grade, subject, topic, objective)
                st.session_state.lesson_plan = lesson_plan
        else:
            st.warning("Please fill in all fields to generate a lesson plan.", icon="⚠️")

# --- NEW: Redesigned Output Display ---
if 'lesson_plan' in st.session_state and st.session_state.lesson_plan:
    st.markdown("---")
    st.subheader("3. Your AI-Generated Lesson Plan")
    plan_text = st.session_state.lesson_plan
    
    if plan_text.startswith("An error occurred:"):
        st.error(plan_text)
    else:
        try:
            # Use regex to find content under each heading
            intro_match = re.search(r'### 📝 Introduction\n(.*?)(?=\n###|$)', plan_text, re.S)
            activity_match = re.search(r'### 🎯 Main Activity\n(.*?)(?=\n###|$)', plan_text, re.S)
            conclusion_match = re.search(r'### ✨ Conclusion\n(.*?)(?=\n###|$)', plan_text, re.S)

            intro = intro_match.group(1).strip() if intro_match else "Not generated."
            activity = activity_match.group(1).strip() if activity_match else "Not generated."
            conclusion = conclusion_match.group(1).strip() if conclusion_match else "Not generated."

            m1, m2, m3 = st.columns(3)
            m1.metric(label="Introduction", value="3 Mins")
            m2.metric(label="Main Activity", value="9 Mins")
            m3.metric(label="Conclusion", value="3 Mins")
            
            with st.expander("📝 **Introduction**", expanded=True):
                st.markdown(intro)
            
            with st.expander("🎯 **Main Activity**", expanded=True):
                st.markdown(activity)

            with st.expander("✨ **Conclusion**", expanded=True):
                st.markdown(conclusion)

            st.markdown("---")
            
            st.write("Copy the full lesson plan text below:")
            st.code(plan_text, language='markdown')

            st.write("Or download the file:")
            dl_col1, dl_col2 = st.columns(2)
            with dl_col1:
                pdf_data = create_pdf(plan_text)
                st.download_button(label="⬇️ Download as PDF", data=pdf_data, file_name=f"{topic}_lesson_plan.pdf", mime="application/pdf", use_container_width=True)
            with dl_col2:
                docx_data = create_docx(plan_text)
                st.download_button(label="⬇️ Download as Word (DOCX)", data=docx_data, file_name=f"{topic}_lesson_plan.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)

        except Exception as e:
            st.error(f"An error occurred while displaying the plan: {e}")
            st.write("Raw AI Output:")
            st.code(plan_text)