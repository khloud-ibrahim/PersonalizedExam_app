import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import random

# =============================
# Page Configuration & Styling
# =============================
st.set_page_config(
    page_title="Personalized Exam System",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="📚"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    /* Main background and text colors */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* Metric cards styling */
    [data-testid="stMetricValue"] {
        font-size: 2.5rem;
        color: #667eea;
        font-weight: bold;
    }
    
    /* Headers */
    h1 {
        color: #667eea;
        font-weight: 800;
        padding: 1rem 0;
    }
    
    h2, h3 {
        color: #764ba2;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-weight: bold;
        border: none;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Info boxes */
    .stAlert {
        border-radius: 15px;
        border-left: 5px solid #667eea;
    }
    
    /* DataFrames */
    [data-testid="stDataFrame"] {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Cards effect */
    div[data-testid="column"] {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.07);
    }
    
    /* Radio buttons */
    .stRadio > label {
        background: white;
        padding: 0.5rem 1rem;
        border-radius: 10px;
        margin: 0.3rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# =============================
# Load Data
# =============================
df = pd.read_csv("processed_data.csv")
rules = pd.read_csv("fp_growth_rules.csv")

# =============================
# Sidebar Setup
# =============================
st.sidebar.markdown("### 🔐 Student Login")
st.sidebar.markdown("---")

student_id = st.sidebar.text_input("🎓 Enter Student ID", placeholder="e.g., S12")

if not student_id:
    st.markdown("""
        <div style='text-align: center; padding: 3rem;'>
            <h1 style='font-size: 3rem;'>📚 Welcome to Personalized Exam System</h1>
            <p style='font-size: 1.3rem; color: #666;'>Please enter your Student ID in the sidebar to continue</p>
        </div>
    """, unsafe_allow_html=True)
    st.stop()

if student_id not in df["student_id"].values:
    st.error("❌ Invalid Student ID. Please try again!")
    st.stop()

current_student = student_id

st.sidebar.success(f"✅ Logged in as: **{student_id}**")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "🧭 Navigation",
    ["📊 Dashboard", "📈 Analytics", "📝 Take Exam", "🤖 AI Recommendations"],
    label_visibility="collapsed"
)

# =============================
# Helper Function: Recommendations
# =============================
def get_recommendations(student_id, df, rules):
    weak_topics = (
        df[(df["student_id"] == student_id) & (df["is_correct"] == 0)]
        ["topic"].unique()
    )

    recommendations = set()
    for topic in weak_topics:
        matched_rules = rules[rules["antecedents"].str.contains(f"Topic_{topic}")]
        for _, rule in matched_rules.iterrows():
            recommendations.add(topic)

    return list(recommendations)

# =============================
# Dashboard Page
# =============================
if page == "📊 Dashboard":
    st.markdown("<h1 style='text-align: center;'>📊 Student Performance Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("---")

    student_df = df[df["student_id"] == current_student]

    total_score = student_df["score"].sum()
    accuracy = student_df["is_correct"].mean() * 100
    total_attempts = len(student_df)
    avg_time = student_df["time_spent"].mean()

    # Metrics in colorful cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("### 🎯 Total Score")
        st.metric("", total_score)
    
    with col2:
        st.markdown("### 📈 Accuracy")
        st.metric("", f"{accuracy:.1f}%")
    
    with col3:
        st.markdown("### 📝 Attempts")
        st.metric("", total_attempts)
    
    with col4:
        st.markdown("### ⏱️ Avg Time")
        st.metric("", f"{avg_time:.0f}s")

    st.markdown("---")
    
    # Performance by topic
    st.markdown("### 📚 Performance by Topic")
    topic_performance = student_df.groupby("topic")["is_correct"].agg(['mean', 'count'])
    topic_performance.columns = ['Accuracy', 'Questions']
    topic_performance['Accuracy'] = (topic_performance['Accuracy'] * 100).round(1)
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.dataframe(topic_performance, use_container_width=True)
    with col2:
        st.info("💡 **Tip:** Focus on topics with lower accuracy rates")

    st.markdown("---")
    st.markdown("### 📋 Recent Attempts")
    st.dataframe(
        student_df[["question_id", "topic", "difficulty", "is_correct", "score", "time_spent"]]
        .tail(10).sort_index(ascending=False),
        use_container_width=True
    )

# =============================
# Analytics Page
# =============================
elif page == "📈 Analytics":
    st.markdown("<h1 style='text-align: center;'>📈 Learning Analytics</h1>", unsafe_allow_html=True)
    st.markdown("---")

    # Configure matplotlib style
    plt.style.use('seaborn-v0_8-pastel')
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Error Rate by Topic")
        topic_error = 1 - df.groupby("topic")["is_correct"].mean()
        
        fig1, ax1 = plt.subplots(figsize=(10, 6))
        colors = plt.cm.RdYlGn_r(topic_error.values)
        topic_error.plot(kind="bar", ax=ax1, color=colors)
        ax1.set_ylabel("Error Rate", fontsize=12, fontweight='bold')
        ax1.set_xlabel("Topic", fontsize=12, fontweight='bold')
        ax1.set_title("Error Rate per Topic", fontsize=14, fontweight='bold', pad=20)
        ax1.grid(axis='y', alpha=0.3)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(fig1)

    with col2:
        st.markdown("### ⏱️ Time Spent vs Difficulty")
        fig2, ax2 = plt.subplots(figsize=(10, 6))
        df.boxplot(column="time_spent", by="difficulty", ax=ax2, 
                   patch_artist=True, 
                   boxprops=dict(facecolor='#667eea', alpha=0.5))
        ax2.set_ylabel("Time Spent (seconds)", fontsize=12, fontweight='bold')
        ax2.set_xlabel("Difficulty Level", fontsize=12, fontweight='bold')
        ax2.set_title("Time Spent vs Difficulty", fontsize=14, fontweight='bold', pad=20)
        plt.suptitle("")
        ax2.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig2)

    # Additional insights
    st.markdown("---")
    st.markdown("### 💡 Quick Insights")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        most_difficult = df.groupby("topic")["is_correct"].mean().idxmin()
        st.info(f"🔴 **Most Challenging Topic:**\n\n{most_difficult}")
    
    with col2:
        best_topic = df.groupby("topic")["is_correct"].mean().idxmax()
        st.success(f"🟢 **Best Performance:**\n\n{best_topic}")
    
    with col3:
        avg_accuracy = df["is_correct"].mean() * 100
        st.warning(f"📊 **Overall Accuracy:**\n\n{avg_accuracy:.1f}%")

# =============================
# Take Exam Page
# =============================
elif page == "📝 Take Exam":
    st.markdown("<h1 style='text-align: center;'>📝 Personalized Exam</h1>", unsafe_allow_html=True)
    st.markdown("---")

    recs = get_recommendations(current_student, df, rules)
    if not recs:
        recs = df["topic"].unique()

    st.info(f"🎯 **Exam Type:** {'Focused on weak areas' if recs else 'General assessment'}")
    
    exam_questions = df[df["topic"].isin(recs)].sample(min(5, len(df)))

    if "answers" not in st.session_state:
        st.session_state.answers = {}

    st.markdown("### 📋 Questions")

    for i, (idx, row) in enumerate(exam_questions.iterrows(), 1):
        with st.container():
            st.markdown(f"""
                <div style='background: white; padding: 1.5rem; border-radius: 15px; 
                            margin: 1rem 0; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
                    <h3 style='color: #667eea;'>Question {i}</h3>
                    <p><strong>📚 Topic:</strong> {row['topic']} | 
                       <strong>⚡ Difficulty:</strong> {row['difficulty']} |
                       <strong>🔢 ID:</strong> {row['question_id']}</p>
                </div>
            """, unsafe_allow_html=True)
            
            q_key = f"Q_{idx}"
            answer = st.radio(
                "Select your answer:",
                ["Option A", "Option B", "Option C", row["correct_answer"]],
                key=q_key,
                horizontal=False
            )
            st.session_state.answers[idx] = answer
            st.markdown("---")

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("✅ Submit Exam", use_container_width=True):
            new_rows = []
            correct_count = 0
            
            for idx, row in exam_questions.iterrows():
                user_answer = st.session_state.answers[idx]
                correct = user_answer == row["correct_answer"]
                if correct:
                    correct_count += 1

                new_rows.append({
                    "student_id": current_student,
                    "question_id": row["question_id"],
                    "topic": row["topic"],
                    "difficulty": row["difficulty"],
                    "question_type": row["question_type"],
                    "student_answer": user_answer,
                    "correct_answer": row["correct_answer"],
                    "is_correct": int(correct),
                    "score": int(correct),
                    "time_spent": random.randint(15, 60)
                })

            df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
            df.to_csv("processed_data.csv", index=False)

            exam_score = (correct_count / len(exam_questions)) * 100
            
            st.balloons()
            st.success(f"✅ **Exam Submitted Successfully!**")
            st.info(f"📊 **Your Score:** {correct_count}/{len(exam_questions)} ({exam_score:.1f}%)")
            st.markdown("---")
            st.markdown("Navigate to **🤖 AI Recommendations** to see updated suggestions!")

# =============================
# Recommendations Page
# =============================
elif page == "🤖 AI Recommendations":
    st.markdown("<h1 style='text-align: center;'>🤖 AI-Powered Study Recommendations</h1>", unsafe_allow_html=True)
    st.markdown("---")

    recs = get_recommendations(current_student, df, rules)

    if not recs:
        st.success("🎉 **Excellent Performance!**")
        st.markdown("""
            <div style='text-align: center; padding: 2rem;'>
                <h2>🌟 You're doing great!</h2>
                <p style='font-size: 1.2rem;'>Keep up the excellent work and continue practicing.</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("📌 **Areas for Improvement Detected**")
        st.markdown("### 🎯 Recommended Focus Topics:")
        
        for i, topic in enumerate(recs, 1):
            student_topic_df = df[(df["student_id"] == current_student) & (df["topic"] == topic)]
            accuracy = student_topic_df["is_correct"].mean() * 100 if len(student_topic_df) > 0 else 0
            
            st.markdown(f"""
                <div style='background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
                            padding: 1.5rem; border-radius: 15px; margin: 1rem 0;
                            border-left: 5px solid #667eea;'>
                    <h3 style='color: #667eea; margin: 0;'>{i}. {topic}</h3>
                    <p style='margin: 0.5rem 0;'>📊 Current Accuracy: {accuracy:.1f}%</p>
                    <p style='margin: 0; color: #666;'>💡 Suggested Path: Start with Easy → Medium difficulty questions</p>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.info("💪 **Pro Tip:** Focus on one topic at a time for better retention!")

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <p>Made with ❤️ | Personalized Learning Platform</p>
    </div>
""", unsafe_allow_html=True)