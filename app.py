import streamlit as st
import time
import matplotlib.pyplot as plt
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# --- Quiz Data (Updated Questions) ---
quiz_data = [
    {"question": "Which planet is known as the Red Planet?", "options": ["Earth", "Mars", "Jupiter", "Venus"], "answer": "Mars"},
    {"question": "Which programming language is used for web development primarily?", "options": ["Python", "JavaScript", "C++", "Java"], "answer": "JavaScript"},
    {"question": "What is the largest mammal on Earth?", "options": ["Elephant", "Blue Whale", "Giraffe", "Hippopotamus"], "answer": "Blue Whale"},
    {"question": "Which HTML tag is used to insert an image?", "options": ["<img>", "<image>", "<src>", "<picture>"], "answer": "<img>"},
    {"question": "Which library is commonly used for data manipulation in Python?", "options": ["NumPy", "Pandas", "Matplotlib", "Scikit-learn"], "answer": "Pandas"}
]

# ----------- Initialize session state ---------------
if "current_q" not in st.session_state:
    st.session_state.current_q = 0
if "selected_answers" not in st.session_state:
    st.session_state.selected_answers = []
if "show_result" not in st.session_state:
    st.session_state.show_result = False
if "score" not in st.session_state:
    st.session_state.score = 0
if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()
if "animation_done" not in st.session_state:
    st.session_state.animation_done = False

# --- Helper Functions ---
def next_question(selected_option):
    q = quiz_data[st.session_state.current_q]
    if selected_option == q["answer"]:
        st.session_state.score += 1
    st.session_state.selected_answers.append(selected_option)
    st.session_state.current_q += 1
    st.session_state.start_time = time.time()
    if st.session_state.current_q >= len(quiz_data):
        st.session_state.show_result = True

def restart_quiz():
    st.session_state.current_q = 0
    st.session_state.selected_answers = []
    st.session_state.show_result = False
    st.session_state.score = 0
    st.session_state.start_time = time.time()
    st.session_state.animation_done = False

# --- Header ----
st.title("🎓 Interactive Quiz App")
st.subheader("Test your knowledge with fun questions!")
st.caption("⏰ Answer each question within **10 seconds**!")

# ------------ Progress Bar --------------
total_questions = len(quiz_data)
current_q = st.session_state.current_q
progress = current_q / total_questions
st.markdown(f"Progress: **{current_q}/{total_questions}**")
st.progress(progress)

# ============== QUIZ SECTION ==============
if not st.session_state.show_result:
    q = quiz_data[current_q]
    st.subheader(q["question"])

    # Timer with color change
    elapsed = int(time.time() - st.session_state.start_time)
    time_left = max(0, 10 - elapsed)
    if time_left > 5:
        st.success(f"⏱️ Time left: {time_left} seconds")
    elif time_left > 2:
        st.warning(f"⏱️ Hurry up! {time_left} seconds left")
    else:
        st.error(f"⏱️ Last seconds! {time_left} left!")

    # When time expires
    if time_left == 0:
        st.session_state.selected_answers.append("Time's up")
        st.session_state.current_q += 1
        st.session_state.start_time = time.time()
        if st.session_state.current_q >= len(quiz_data):
            st.session_state.show_result = True
        st.rerun()

    selected_option = st.radio("Choose an answer:", q["options"], key=f"q_{current_q}")
    st.button("➡️ Next", on_click=next_question, args=(selected_option,))

# ============== RESULT SECTION ==============
else:
    score = st.session_state.score
    total = len(quiz_data)

    # Run animation only once
    if not st.session_state.animation_done:
        st.success("🎉 Outstanding! You've completed the quiz!")
        st.balloons()
        st.snow()
        st.session_state.animation_done = True

    # --- Create DataFrame for Results ---
    result_data = []
    for i, q in enumerate(quiz_data):
        user_ans = st.session_state.selected_answers[i]
        correct = q["answer"]
        result_data.append({
            "Question": q["question"],
            "Your Answer": user_ans,
            "Correct Answer": correct,
            "Result": "✅ Correct" if user_ans == correct else "❌ Wrong"
        })

    df = pd.DataFrame(result_data)
    st.subheader("📊 Detailed Results:")
    st.dataframe(df, use_container_width=True)

    # --- Pie Chart with bright colors ---
    correct_count = score
    wrong_count = total - score
    fig, ax = plt.subplots()
    ax.pie(
        [correct_count, wrong_count],
        labels=["Correct ✅", "Incorrect ❌"],
        autopct="%1.1f%%",
        colors=["#2ecc71", "#e74c3c"],
        startangle=90
    )
    ax.axis("equal")
    st.pyplot(fig)

    # --- Download CSV Button ---
    csv_data = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="💾 Download Results as CSV",
        data=csv_data,
        file_name="quiz_results.csv",
        mime="text/csv",
    )

    # --- Restart Button ---
    st.button("🔄 Restart Quiz", on_click=restart_quiz)

# Auto-refresh every second for timer
st_autorefresh(interval=1000, key="refresh_timer")
