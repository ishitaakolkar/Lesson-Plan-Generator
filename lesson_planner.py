import os
import streamlit as st
import base64
import google.generativeai as genai
import re
from fpdf import FPDF
from docx import Document
from io import BytesIO

# --- CONFIGURATION & API SETUP ---
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    st.error("Error: GOOGLE_API_KEY not found in environment variables.")
    st.stop()

try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
except Exception as e:
    st.error(f"Error configuring the API: {e}")
    st.stop()

# --- DATA ---

# Full subject lists mapped by board, grade, and (for grade 11+) streams where applicable

LESSON_DATA = {
    "CBSE": {
        "Primary (1-5)": {
            "Mathematics": [],
            "English": [],
            "Hindi": [],
            "Environmental Science (EVS)": [],
            "Sanskrit": [],
            "Urdu": [],
            "Tamil": [],
            "Kannada": [],
            # Add regional languages as needed
        },
        "Middle (6-8)": {
            "Mathematics": [],
            "English": [],
            "Hindi": [],
            "Science": [],
            "Social Science": [],
            "Sanskrit": [],
            "Tamil": [],
            # Add more if applicable
        },
        "Secondary (9-10)": {
            "Mathematics": [],
            "English": [],
            "Hindi": [],
            "Science": [],
            "Social Science": [],
            "Computer Applications": [],
            "Sanskrit": [],
            "Tamil": [],
            # More subjects possible
        },
        "Senior Secondary": {
            "Science": {
                "Physics": [],
                "Chemistry": [],
                "Biology": [],
                "Mathematics": [],
                "Computer Science": [],
                "Informatics Practices": [],
            },
            "Commerce": {
                "Business Studies": [],
                "Accountancy": [],
                "Economics": [],
                "Mathematics": [],
                "Entrepreneurship": [],
            },
            "Arts": {
                "Political Science": [],
                "Geography": [],
                "History": [],
                "Psychology": [],
                "Sociology": [],
                "Economics": [],
                "English": [],
                "Hindi": [],
                "Physical Education": [],
                "Fine Arts": [],
            }
        }
    },
    "GSEB": {
        "Primary (1-5)": {
            "ગણિત (Mathematics)": [],
            "ગુજરાતી (Gujarati)": [],
            "અંગ્રેજી (English)": [],
            "વિજ્ઞાન (Science/EVS)": [],
            "સામાજિક વિજ્ઞાન (Social Science)": [],
            # Add more Gujarati medium subjects as needed
        },
        "Middle (6-8)": {
            "ગણિત (Mathematics)": [],
            "ગુજરાતી (Gujarati)": [],
            "અંગ્રેજી (English)": [],
            "વિજ્ઞાન (Science)": [],
            "સામાજિક વિજ્ઞાન (Social Science)": [],
            # More as applicable
        },
        "Secondary (9-10)": {
            "ગણિત (Mathematics)": [],
            "ગુજરાતી (Gujarati)": [],
            "અંગ્રેજી (English)": [],
            "વિજ્ઞાન (Science)": [],
            "સામાજિક વિજ્ઞાન (Social Science)": [],
            "કમ્પ્યુટર (Computer)": [],
            # Add more if needed
        },
        "Senior Secondary": {
            "Science": {
                "ભૌતિક વિજ્ઞાન (Physics)": [],
                "રાસાયણિક વિજ્ઞાન (Chemistry)": [],
                "જીવ વિજ્ઞાન (Biology)": [],
                "ગણિત (Mathematics)": [],
            },
            "Commerce": {
                "વાણિજ્ય અભ્યાસ (Business Studies)": [],
                "લેખાપાલન (Accountancy)": [],
                "અર્થશાસ્ત્ર (Economics)": [],
                "ગણિત (Mathematics)": [],
            },
            "Arts": {
                "રાજકારણ શાસ્ત્ર (Political Science)": [],
                "ભૂગોળ (Geography)": [],
                "ઇતિહાસ (History)": [],
                "મનોઃશાસ્ત્ર (Psychology)": [],
                "સામાજિક શાસ્ત્ર (Sociology)": [],
                "અંગ્રેજી (English)": [],
                "ગુજરાતી (Gujarati)": [],
                # Add other humanities subjects
            }
        }
    }
}

# Map grades to categories used above
GRADES_MAPPING = {
    # Nursery, LKG, UKG mapped to Primary
    'Nursery': 'Primary (1-5)', 'LKG': 'Primary (1-5)', 'UKG': 'Primary (1-5)',
    # Grades 1-5 Primary
    '1st Grade': 'Primary (1-5)', '2nd Grade': 'Primary (1-5)', '3rd Grade': 'Primary (1-5)',
    '4th Grade': 'Primary (1-5)', '5th Grade': 'Primary (1-5)',
    # Grades 6-8 Middle
    '6th Grade': 'Middle (6-8)', '7th Grade': 'Middle (6-8)', '8th Grade': 'Middle (6-8)',
    # Grades 9-10 Secondary
    '9th Grade': 'Secondary (9-10)', '10th Grade': 'Secondary (9-10)',
    # Grades 11-12 Senior Secondary (streams)
    '11th Grade': 'Senior Secondary', '12th Grade': 'Senior Secondary'
}

# For grades 11 and 12, user must select stream:
STREAMS = {
    "Science": None,  # Use LESSON_DATA[board]["Senior Secondary"]["Science"]
    "Commerce": None, # Use LESSON_DATA[board]["Senior Secondary"]["Commerce"]
    "Arts": None      # Use LESSON_DATA[board]["Senior Secondary"]["Arts"]
}

# --- HELPER FUNCTIONS ---

@st.cache_data
def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

def generate_lesson_plan(board, grade, subject, topic, objective):
    prompt = f"""
As an expert curriculum designer for the {board} board in India, create a 15-minute micro-lesson plan for {grade}, focusing on the subject {subject}.
**Topic:** {topic}
**Objective:** By the end of this lesson, students should be able to {objective}.
Generate the output in simple Markdown. Use these exact headings for each section: '### 📝 Introduction', '### 🎯 Main Activity', and '### ✨ Conclusion'.
Under each heading, provide a clear, concise, and actionable plan.

Also, generate a short 5-question multiple-choice quiz (with answers) related to the lesson at the end under '### 📝 Quiz'.
"""
    try:
        response = model.generate_content(prompt, request_options={'timeout': 60})
        return response.text
    except Exception as e:
        return f"An error occurred: {e}"

def create_pdf(text_content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    cleaned_text = text_content.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 10, cleaned_text)
    return bytes(pdf.output(dest='S').encode('latin-1'))

def create_docx(text_content):
    doc = Document()
    cleaned_text = text_content.encode('ascii', 'ignore').decode('ascii')
    doc.add_paragraph(cleaned_text)
    bio = BytesIO()
    doc.save(bio)
    return bio.getvalue()

def translate_text(text, target_lang='hi'):
    # Placeholder for translation API integration, returns original text for now
    return text

# --- STREAMLIT UI ---

st.set_page_config(layout="wide", page_title="Smart Lesson Planner", page_icon="🧑‍🏫")

try:
    img = get_img_as_base64("background.jpg")
    page_bg_img = f"""
    <style>
    [data-testid="stAppViewContainer"] > .main {{
    background-image: url("data:image/jpeg;base64,{img}");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
    }}
    [data-testid="stHeader"] {{
    background: rgba(0,0,0,0);
    }}
    </style>
    """
    st.markdown(page_bg_img, unsafe_allow_html=True)
except FileNotFoundError:
    st.warning("background.jpg not found. Please add it to the root folder.", icon="⚠️")

st.title("Planit: Smart Lesson Planner")

with st.container():
    st.subheader("1. Select Your Class Details")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        board = st.selectbox("Educational Board", list(LESSON_DATA.keys()))
    with col2:
        grade = st.selectbox("Grade", list(GRADES_MAPPING.keys()))
    grade_category = GRADES_MAPPING.get(grade, "Primary (1-5)")

    # If grade is 11 or 12, ask for stream selection
    stream = None
    if grade_category == "Senior Secondary":
        with col3:
            stream = st.selectbox("Select Stream", ["Science", "Commerce", "Arts"])
        subjects_list = list(LESSON_DATA[board][grade_category][stream].keys())
    else:
        with col3:
            subjects_list = list(LESSON_DATA.get(board, {}).get(grade_category, {}).keys())
            if subjects_list:
                subject = st.selectbox("Subject", subjects_list)
            else:
                subject = None
        stream = None

    # Show subjects depending on stream if applicable
    if grade_category == "Senior Secondary" and stream:
        subject = st.selectbox("Subject", list(LESSON_DATA[board][grade_category][stream].keys()))
    elif grade_category != "Senior Secondary":
        # Already handled above
        pass
    else:
        subject = None

    st.subheader("2. Define Your Lesson")

    if subject:
        available_topics = []  # For now keep empty, users can type
        topic = st.text_input("Lesson Topic", placeholder="Enter lesson topic here")
    else:
        topic = ""

    objective = st.text_area("Learning Objective for this Topic", placeholder="e.g., describe the stages of evaporation and condensation")

    translate = st.checkbox("Translate lesson plan to Hindi", value=False)

    if st.button("🚀 Generate Lesson Plan", type="primary", use_container_width=True):
        if all([board, grade, subject, topic, objective]):
            with st.spinner("🧠 The AI is thinking... this may take a moment."):
                lesson_plan = generate_lesson_plan(board, grade, subject, topic, objective)
                if translate:
                    lesson_plan = translate_text(lesson_plan, target_lang='hi')
                st.session_state.lesson_plan = lesson_plan
        else:
            st.warning("Please fill in all fields to generate a lesson plan.", icon="⚠️")

if 'lesson_plan' in st.session_state and st.session_state.lesson_plan:
    st.markdown("---")
    st.subheader("3. Your AI-Generated Lesson Plan")
    plan_text = st.session_state.lesson_plan

    if plan_text.startswith("An error occurred"):
        st.error(plan_text)
    else:
        intro_match = re.search(r'### 📝 Introduction.*?\n(.*?)(?=\n###|$)', plan_text, re.S)
        activity_match = re.search(r'### 🎯 Main Activity.*?\n(.*?)(?=\n###|$)', plan_text, re.S)
        conclusion_match = re.search(r'### ✨ Conclusion.*?\n(.*?)(?=\n###|$)', plan_text, re.S)
        quiz_match = re.search(r'### 📝 Quiz.*?\n(.*)', plan_text, re.S)

        intro = intro_match.group(1).strip() if intro_match else "Could not parse Introduction."
        activity = activity_match.group(1).strip() if activity_match else "Could not parse Main Activity."
        conclusion = conclusion_match.group(1).strip() if conclusion_match else "Could not parse Conclusion."
        quiz = quiz_match.group(1).strip() if quiz_match else "No quiz generated."

        m1, m2, m3, m4 = st.columns(4)
        m1.metric(label="Introduction", value="~3 Mins")
        m2.metric(label="Main Activity", value="~9 Mins")
        m3.metric(label="Conclusion", value="~3 Mins")
        m4.metric(label="Quiz", value="5 Questions")

        with st.expander("📝 **Introduction**", expanded=True):
            st.markdown(intro)
        with st.expander("🎯 **Main Activity**", expanded=True):
            st.markdown(activity)
        with st.expander("✨ **Conclusion**", expanded=True):
            st.markdown(conclusion)
        with st.expander("📝 **Quiz**", expanded=True):
            st.markdown(quiz)

        st.markdown("---")
        st.write("Copy the full lesson plan text below:")
        st.code(plan_text, language='markdown')

        st.write("Or download the file:")
        col_pdf, col_docx = st.columns(2)
        with col_pdf:
            try:
                pdf_data = create_pdf(plan_text)
                st.download_button(label="⬇️ Download as PDF", data=pdf_data, file_name=f"{topic}_lesson_plan.pdf", mime="application/pdf", use_container_width=True)
            except Exception as e:
                st.error(f"Failed to create PDF: {e}")
        with col_docx:
            try:
                docx_data = create_docx(plan_text)
                st.download_button(label="⬇️ Download as Word (DOCX)", data=docx_data, file_name=f"{topic}_lesson_plan.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)
            except Exception as e:
                st.error(f"Failed to create DOCX: {e}")
