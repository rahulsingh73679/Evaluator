import streamlit as st
from PyPDF2 import PdfReader
import openai
import pandas as pd

# Configure OpenAI API (replace with your API key)
openai.api_key = "YOUR_OPENAI_API_KEY"

# App Title
st.title("Personalized Learning and Exam Prep App")

# Sidebar for Navigation
st.sidebar.title("Navigation")
options = st.sidebar.radio("Go to:", ["Upload PDF", "Take Quiz", "Leaderboard"])

# In-memory storage for quizzes
if "quizzes" not in st.session_state:
    st.session_state["quizzes"] = {}
if "leaderboard" not in st.session_state:
    st.session_state["leaderboard"] = []

# Function to extract questions from PDF
def extract_questions_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    questions = []
    for page in reader.pages:
        text = page.extract_text()
        lines = text.split('\n')
        for line in lines:
            if "Question Label" in line:  # Match quiz question lines
                question = {"question": line, "options": []}
                questions.append(question)
            elif "Options :" in line or "Options :" in text:
                options = lines[lines.index(line) + 1:lines.index(line) + 5]
                question["options"] = [opt.strip() for opt in options]
    return questions

# Upload PDF Section
if options == "Upload PDF":
    st.header("Upload Your Quiz PDF")
    uploaded_file = st.file_uploader("Upload your PDF file here:", type=["pdf"])
    if uploaded_file is not None:
        with st.spinner("Processing your PDF..."):
            quiz = extract_questions_from_pdf(uploaded_file)
            if quiz:
                st.success("Quiz extracted successfully!")
                st.session_state["quizzes"] = quiz
                st.write("Preview of extracted questions:")
                for q in quiz[:3]:  # Preview first 3 questions
                    st.write(q["question"])
                    st.write(q["options"])
            else:
                st.error("No questions found in the uploaded PDF.")

# Take Quiz Section
elif options == "Take Quiz":
    if not st.session_state["quizzes"]:
        st.warning("Please upload a PDF with quiz questions first.")
    else:
        st.header("Take Quiz")
        score = 0
        total = len(st.session_state["quizzes"])
        for idx, q in enumerate(st.session_state["quizzes"]):
            st.subheader(f"Question {idx + 1}: {q['question']}")
            user_answer = st.radio(
                "Choose an option:",
                q["options"],
                key=f"q{idx}"
            )
            correct_answer = q["options"][0]  # Assuming first option is correct
            if st.button(f"Submit Answer {idx + 1}", key=f"submit_{idx}"):
                if user_answer == correct_answer:
                    st.success("Correct!")
                    score += 1
                else:
                    st.error(f"Incorrect! Correct answer: {correct_answer}")

        st.write(f"Your Score: {score}/{total}")
        st.session_state["leaderboard"].append({"user": "You", "score": score})

# Leaderboard Section
elif options == "Leaderboard":
    st.header("Leaderboard")
    if st.session_state["leaderboard"]:
        leaderboard = pd.DataFrame(st.session_state["leaderboard"])
        leaderboard = leaderboard.sort_values(by="score", ascending=False)
        st.table(leaderboard)
    else:
        st.info("No scores yet. Take a quiz to get started!")

# Advanced Capabilities (Optional AI-Generated Questions)
st.sidebar.title("Advanced Features")
if st.sidebar.checkbox("Generate AI Questions"):
    st.header("AI-Generated Questions")
    user_text = st.text_area("Paste text or upload a document for AI-generated questions:")
    if st.button("Generate Questions"):
        with st.spinner("Generating questions..."):
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=f"Generate multiple-choice questions based on this text: {user_text}",
                max_tokens=300
            )
            st.write(response.choices[0].text)

