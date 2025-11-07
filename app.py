import streamlit as st
import pandas as pd
import json
import random
from datetime import datetime
from ai_utils import setup_gemini, generate_quiz

# -----------------------------------
# 🌟 Page Configuration
# -----------------------------------
st.set_page_config(page_title="AI Quiz & Learning Assistant", page_icon="🧠", layout="wide")

st.title("🎯 AI Smart Quiz & Learning Recommender")

# -----------------------------------
# Step 1: Subject Selection
# -----------------------------------
subject = st.selectbox("Choose a Subject", ["Mathematics", "Science", "History", "Computer Science", "English"])

if st.button("🪄 Generate Quiz"):
    try:
        genai = setup_gemini()
        quiz_json = generate_quiz(genai, subject)
        quiz_data = json.loads(quiz_json)
        st.session_state.quiz_data = quiz_data
        st.session_state.subject = subject
        st.success("✅ Quiz Generated Successfully!")
    except Exception as e:
        st.error(f"Error: {e}")

# -----------------------------------
# Step 2: Take the Quiz
# -----------------------------------
if "quiz_data" in st.session_state:
    st.subheader(f"📘 {st.session_state.subject} Quiz")

    answers = {}
    for i, q in enumerate(st.session_state.quiz_data):
        st.write(f"**Q{i+1}. {q['question']}**")
        answer = st.radio("Select your answer:", q['options'], key=f"q{i}")
        answers[q['question']] = answer[0]  # First letter (A/B/C/D)

    if st.button("📊 Submit Quiz"):
        score = 0
        total = len(st.session_state.quiz_data)
        for q in st.session_state.quiz_data:
            if answers[q["question"]] == q["answer"]:
                score += 1
        st.success(f"Your Score: {score}/{total}")

        # Store results in Excel
        df = pd.DataFrame([{
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Subject": st.session_state.subject,
            "Score": score,
            "Total": total,
            "Accuracy": f"{(score/total)*100:.2f}%"
        }])

        try:
            existing = pd.read_excel("quiz_results.xlsx")
            df = pd.concat([existing, df], ignore_index=True)
        except FileNotFoundError:
            pass

        df.to_excel("quiz_results.xlsx", index=False)
        st.info("✅ Your results are saved!")

        # AI Feedback
        genai = setup_gemini()
        feedback_prompt = f"""
        A student took a {st.session_state.subject} quiz and scored {score}/{total}.
        Suggest key areas to improve and recommend 2 YouTube videos or online resources 
        for better understanding.
        Give the response in simple bullet points.
        """
        feedback_model = genai.GenerativeModel("gemini-pro")
        feedback = feedback_model.generate_content(feedback_prompt).text
        st.subheader("📈 Personalized AI Feedback & Recommendations")
        st.markdown(feedback)
