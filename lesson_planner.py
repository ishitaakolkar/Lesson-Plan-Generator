import streamlit as st
import os
import base64  # NEW: Import for encoding the image
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
LESSON_DATA = {
    'CBSE': {
        'Primary (1-5)': {
            'Mathematics': ['Shapes and Space', 'Numbers from One to Nine', 'Addition and Subtraction', 'Measurement', 'Time', 'Money'],
            'English': ['Reading Comprehension: The Little Bird', 'Grammar: Nouns', 'Vocabulary: Animal Names', 'Writing: My Family'],
            'Environmental Science (EVS)': ['Our Body', 'Plants Around Us', 'Animals Around Us', 'Water', 'Our Festivals']
        },
        'Middle (6-8)': {
            'Science': ['Food: Where Does It Come From?', 'Components of Food', 'Fibre to Fabric', 'Sorting Materials Into Groups', 'Separation of Substances'],
            'Social Science': ['What, Where, How and When?', 'On The Trail of the Earliest People', 'From Gathering to Growing Food', 'In the Earliest Cities']
        }
    },
    'GSEB': {
        'Primary (1-5)': {
            'Mathematics': ['આકારો અને જગ્યા (Shapes and Space)', 'એક થી નવ સુધીની સંખ્યાઓ (Numbers 1-9)', 'સરવાળા અને બાદબાકી (Addition/Subtraction)'],
            'Gujarati': ['વાર્તા: લાલચુ કૂતરો (Story: The Greedy Dog)', 'વ્યાકરણ: સંજ્ઞા (Grammar: Nouns)', 'કવિતા: વરસાદ (Poem: Rain)']
        },
        'Middle (6-8)': {
            'Science (Vigyan)': ['ખોરાક: ક્યાંથી મળે છે? (Food: Where does it come from?)', 'આહારના ઘટકો (Components of Food)', 'પદાર્થોનું અલગીકરણ (Separation of Substances)'],
            'Social Science (Samajik Vigyan)': ['ચાલો, ઇતિહાસ જાણીએ (Let’s Know History)', 'આપણી આસપાસ શું? (What is Around Us?)', 'સરકાર (The Government)']
        }
    }
}
GRADES_MAPPING = {
    'Nursery': 'Primary (1-5)', 'LKG': 'Primary (1-5)', 'UKG': 'Primary (1-5)',
    '1st Grade': 'Primary (1-5)', '2nd Grade': 'Primary (1-5)', '3rd Grade': 'Primary (1-5)', '4th Grade': 'Primary (1-5)', '5th Grade': 'Primary (1-5)',
    '6th Grade': 'Middle (6-8)', '7th Grade': 'Middle (6-8)', '8th Grade': 'Middle (6-8)'
}

# --- HELPER FUNCTIONS ---
@st.cache_data
def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

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

def create_pdf(text_content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    cleaned_text = text_content.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 10, cleaned_text)
    return bytes(pdf.output())

def create_docx(text_content):
    doc = Document()
    cleaned_text = text_content.encode('ascii', 'ignore').decode('ascii')
    doc.add_paragraph(cleaned_text)
    bio = BytesIO()
    doc.save(bio)
    return bio.getvalue()

# --- STREAMLIT UI ---
st.set_page_config(layout="wide", page_title="Smart Lesson Planner", page_icon="🧑‍🏫")

# --- NEW: Set Background Image ---
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

with st.container(border=True):
    st.subheader("1. Select Your Class Details")
    col1, col2, col3 = st.columns(3)
    with col1:
        board = st.selectbox("Educational Board", list(LESSON_DATA.keys()))
    with col2:
        grade = st.selectbox("Grade", list(GRADES_MAPPING.keys()))
    with col3:
        grade_category = GRADES_MAPPING.get(grade, 'Primary (1-5)') # Default gracefully
        available_subjects = list(LESSON_DATA.get(board, {}).get(grade_category, {}).keys())
        if available_subjects:
            subject = st.selectbox("Subject", available_subjects)
        else:
            subject = None
            st.warning("No subjects defined for this grade level yet.")

    st.subheader("2. Define Your Lesson")
    if subject:
        available_topics = LESSON_DATA.get(board, {}).get(grade_category, {}).get(subject, [])
        if available_topics:
            topic = st.selectbox("Lesson Topic / Chapter", available_topics)
        else:
            topic = st.text_input("Lesson Topic", placeholder="No pre-defined topics. Please enter one.")
    else:
        topic = ""

    objective = st.text_area("Learning Objective for this Topic", placeholder="e.g., 'describe the stages of evaporation and condensation'")

    if st.button("🚀 Generate Lesson Plan", type="primary", use_container_width=True):
        if all([board, grade, subject, topic, objective]):
            with st.spinner("🧠 The AI is thinking... this may take a moment."):
                lesson_plan = generate_lesson_plan(board, grade, subject, topic, objective)
                st.session_state.lesson_plan = lesson_plan
        else:
            st.warning("Please fill in all fields to generate a lesson plan.", icon="⚠️")

# --- Output Display Section ---
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

        intro = intro_match.group(1).strip() if intro_match else "Could not parse Introduction."
        activity = activity_match.group(1).strip() if activity_match else "Could not parse Main Activity."
        conclusion = conclusion_match.group(1).strip() if conclusion_match else "Could not parse Conclusion."

        m1, m2, m3 = st.columns(3)
        m1.metric(label="Introduction", value="~3 Mins")
        m2.metric(label="Main Activity", value="~9 Mins")
        m3.metric(label="Conclusion", value="~3 Mins")
        
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
            try:
                pdf_data = create_pdf(plan_text)
                st.download_button(label="⬇️ Download as PDF", data=pdf_data, file_name=f"{topic}_lesson_plan.pdf", mime="application/pdf", use_container_width=True)
            except Exception as e:
                st.error(f"Failed to create PDF: {e}")
        with dl_col2:
            try:
                docx_data = create_docx(plan_text)
                st.download_button(label="⬇️ Download as Word (DOCX)", data=docx_data, file_name=f"{topic}_lesson_plan.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)
            except Exception as e:
                st.error(f"Failed to create DOCX: {e}")