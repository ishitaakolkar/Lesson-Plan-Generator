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
def generate_lesson_plan(grade, topic, objective):
    """
    Generates a lesson plan by calling the Gemini API with a specific prompt.
    """
    # This is our "System Instruction" prompt
    prompt = f"""
    As an expert curriculum designer, create a concise and engaging 15-minute micro-lesson plan.

    **Grade Level:** {grade}
    **Lesson Topic:** {topic}
    **Learning Objective:** By the end of this 15-minute lesson, students should be able to {objective}.

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
st.set_page_config(page_title="Micro Lesson Plan Generator", page_icon="📝")

st.title("📝 Micro Lesson Plan Generator")
st.write("Fill in the details below to generate a 15-minute lesson plan outline.")

# Input fields for the user
grade = st.text_input("Grade Level", placeholder="e.g., '4th Grade'")
topic = st.text_input("Lesson Topic", placeholder="e.g., 'The Solar System'")
objective = st.text_area("Learning Objective", placeholder="e.g., 'name the planets in order from the Sun'")

# Button to trigger the generation
if st.button("✨ Generate Lesson Plan"):
    if grade and topic and objective:
        with st.spinner("🤖 AI is creating your lesson plan..."):
            lesson_plan = generate_lesson_plan(grade, topic, objective)
            st.markdown("---")
            st.subheader("Your AI-Generated Lesson Plan")
            st.markdown(lesson_plan)
    else:
        st.warning("Please fill in all fields above.", icon="⚠️")