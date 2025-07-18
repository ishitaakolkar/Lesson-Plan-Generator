import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from a .env file
load_dotenv()

# --- CONFIGURATION ---
# Configure the Google Gemini API
try:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        st.error("Error: GOOGLE_API_KEY not found in .env file.")
        st.stop()
    genai.configure(api_key=api_key)
    # Initialize the Generative Model
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
except Exception as e:
    st.error(f"Error configuring the API: {e}")
    st.stop()


# --- HELPER FUNCTION ---
# <-- UPDATED function to accept new parameters
def generate_lesson_plan(board, grade, subject, topic, objective):
    """
    Generates a lesson plan by calling the Gemini API with a specific prompt.
    """
    # <-- UPDATED prompt with more context for the AI
    prompt = f"""
    As an expert curriculum designer specializing in the Indian education system, create a concise and engaging 15-minute micro-lesson plan.

    **Educational Board:** {board}
    **Grade Level:** {grade}
    **Subject:** {subject}
    **Lesson Topic:** {topic}
    **Learning Objective:** By the end of this 15-minute lesson, students should be able to {objective}.

    Please ensure the content, examples, and complexity are appropriate for the specified board and grade level in India.
    Structure the output in Markdown format with the following three sections:
    1.  **Introduction (3 minutes):** A hook to grab student attention and introduce the objective.
    2.  **Main Activity (9 minutes):** A simple, interactive activity for the students.
    3.  **Conclusion (3 minutes):** A quick wrap-up to check for understanding and summarize the key takeaway.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"An error occurred while generating the plan: {e}"


# --- STREAMLIT UI ---
st.set_page_config(page_title="Indian Lesson Plan Generator", page_icon="📝")

# <-- UPDATED Title
st.title("📝 Indian Curriculum Lesson Plan Generator")
st.write("Fill in the details below to generate a 15-minute lesson plan outline tailored for Indian schools.")

# --- NEW: Dropdown Menus for Structured Input ---
boards = ['CBSE', 'GSEB']
grades = ['Nursery', 'LKG', 'UKG', '1st Grade', '2nd Grade', '3rd Grade', '4th Grade', '5th Grade', '6th Grade', '7th Grade', '8th Grade', '9th Grade', '10th Grade', '11th Grade', '12th Grade']
subjects = [
    'English', 'Mathematics', 'Science', 'Social Studies', 'Hindi', 'Gujarati',
    'Computer Science', 'Physics', 'Chemistry', 'Biology', 'History', 'Geography',
    'Economics', 'Accountancy', 'Business Studies'
]

board = st.selectbox("Select Educational Board", boards)
grade = st.selectbox("Select Grade", grades)
subject = st.selectbox("Select Subject", subjects)


# <-- Text inputs for remaining details ---
topic = st.text_input("Lesson Topic", placeholder="e.g., 'The Mughal Empire', 'Photosynthesis'")
objective = st.text_area("Learning Objective", placeholder="e.g., 'list the major Mughal emperors in chronological order'")

# Button to trigger the generation
if st.button("✨ Generate Lesson Plan"):
    # <-- UPDATED to check all new fields
    if board and grade and subject and topic and objective:
        with st.spinner("🤖 AI is creating your lesson plan..."):
            # <-- UPDATED to pass all new inputs to the function
            lesson_plan = generate_lesson_plan(board, grade, subject, topic, objective)
            st.markdown("---")
            st.subheader("Your AI-Generated Lesson Plan")
            st.markdown(lesson_plan)
    else:
        st.warning("Please fill in all fields above.", icon="⚠️")