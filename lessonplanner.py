import os
import google.generativeai as genai
from dotenv import load_dotenv # Used for loading API key from .env file

def configure_gemini_api():
    """
    Configures the Google Gemini API key.
    It first tries to load the key from a .env file (for local development),
    then falls back to environment variables.
    """
    load_dotenv() # Load environment variables from .env file

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY environment variable not set.")
        print("Please set it or create a .env file with GOOGLE_API_KEY='YOUR_API_KEY_HERE'")
        print("You can get a free API key from: https://aistudio.google.com/app/apikey")
        exit(1) # Exit if API key is not found

    genai.configure(api_key=api_key)
    print("Gemini API configured successfully.")

def get_gemini_model(model_name="gemini-pro"):
    """
    Initializes and returns the Gemini GenerativeModel.
    Uses 'gemini-pro' by default for broad accessibility and free tier usage.
    """
    try:
        model = genai.GenerativeModel(model_name)
        return model
    except Exception as e:
        print(f"Error initializing Gemini model '{model_name}': {e}")
        print("Ensure the model name is correct and you have access to it.")
        exit(1)

def generate_lesson_plan(model, topic, grade_level, learning_objective):
    """
    Generates a micro lesson plan using the Gemini model.

    Args:
        model: The initialized Gemini GenerativeModel instance.
        topic (str): The subject or theme of the lesson.
        grade_level (str): The target grade or age group for the lesson.
        learning_objective (str): The specific objective students should achieve.

    Returns:
        str: The generated lesson plan outline, or an error message.
    """
    # System prompt to define the AI agent's persona and task
    system_instruction = (
        "You are an expert curriculum designer for K-12 education. "
        "Your task is to create a concise, 15-minute lesson plan outline "
        "on a given topic for a specified grade level, focusing on clear learning objectives "
        "and a simple, engaging activity. The plan should include the following sections: "
        "Introduction (2-3 sentences), Main Activity (brief description), "
        "and Conclusion/Wrap-up (2-3 sentences). "
        "Use clear headings and bullet points where appropriate for readability."
    )

    # User prompt combining the system instruction with specific user inputs
    user_prompt = (
        f"Generate a micro lesson plan outline with the following details:\n"
        f"Topic: {topic}\n"
        f"Grade Level: {grade_level}\n"
        f"Learning Objective: {learning_objective}\n\n"
        f"Please provide the output in a clear, easy-to-read format."
    )

    try:
        # Using generate_content for a single turn conversation
        # The system instruction is passed as a separate parameter for better model guidance
        response = model.generate_content(
            contents=[
                {"role": "user", "parts": [{"text": system_instruction}]},
                {"role": "user", "parts": [{"text": user_prompt}]}
            ]
        )
        return response.text
    except genai.types.BlockedPromptException as e:
        # Handle cases where the prompt might be blocked due to safety reasons
        print(f"Error: Your prompt was blocked due to safety concerns. Details: {e}")
        return "Could not generate lesson plan due to safety policy."
    except Exception as e:
        print(f"An unexpected error occurred during content generation: {e}")
        return "Could not generate lesson plan due to an internal error."

def main():
    """
    Main function to run the lesson plan generator.
    """
    configure_gemini_api()
    model = get_gemini_model()

    print("\n--- Micro Lesson Plan Generator ---")
    print("Enter details to generate a 15-minute lesson plan outline.")

    topic = input("Enter the lesson topic (e.g., 'Photosynthesis'): ")
    grade_level = input("Enter the target grade level (e.g., '7th Grade Science'): ")
    learning_objective = input("Enter a key learning objective (e.g., 'Students will identify inputs and outputs of photosynthesis'): ")

    print("\nGenerating lesson plan...")
    lesson_plan_output = generate_lesson_plan(model, topic, grade_level, learning_objective)

    print("\n--- Generated Lesson Plan ---")
    print(lesson_plan_output)
    print("\n-----------------------------")

if __name__ == "__main__":
    main()
