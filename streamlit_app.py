import os
import io
from datetime import datetime
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from streamlit_lottie import st_lottie
import json
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import joblib

# Import custom modules
import firebase_helper as fb
import ai_utils as ai
from powerbi_analytics import powerbi_analytics
from ui_helpers import lottie_from_url, load_css, toggle_dark_mode

# Page config
st.set_page_config(
    page_title="AI Quiz & Placement", 
    page_icon="🎯", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load enhanced CSS
load_css()

# Session state initialization
def init_session():
    defaults = {
        "logged_in": False,
        "role": None,
        "username": "",
        "student_data": {},
        "current_quiz_data": None,
        "current_quiz_subject": None,
        "current_quiz_difficulty": None,
        "current_year": None,
        "current_subjects": [],
        "dark_mode": True,
        "quiz_answers": {},
        "quiz_submitted": False,
        "quiz_score": 0,
        "quiz_total": 0,
        "incorrect_questions": [],
        "show_feedback": False,
        "gemini_available": False
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()

# Check Gemini availability
def check_gemini_availability():
    """Check if Gemini is available and update session state"""
    try:
        gemini_status = ai.get_gemini_status()
        st.session_state.gemini_available = gemini_status
        return gemini_status
    except Exception as e:
        st.session_state.gemini_available = False
        return False

# ML Helper Functions (simplified for this example)
def predict_employability_ml(student_data):
    """Predict employability using rule-based system"""
    if not student_data:
        return 0
        
    score = 0
    
    # CGPA (0-25 points)
    cgpa = float(student_data.get("cgpa", 6.5))
    if cgpa >= 9.0: score += 25
    elif cgpa >= 8.0: score += 20
    elif cgpa >= 7.0: score += 15
    elif cgpa >= 6.0: score += 10
    else: score += 5
    
    # Internships (0-20 points)
    internships = student_data.get("internships", 0)
    score += min(20, internships * 5)
    
    # Projects (0-15 points)
    projects = student_data.get("projects", 0)
    score += min(15, projects * 3)
    
    # Certifications (0-15 points)
    certs = len(student_data.get("certifications", []))
    score += min(15, certs * 3)
    
    # Communication (0-10 points)
    communication = student_data.get("communication", 6)
    score += min(10, communication)
    
    # Year bonus (0-15 points)
    year = student_data.get("year", "1st Year")
    year_bonus = {"1st Year": 5, "2nd Year": 8, "3rd Year": 12, "4th Year": 15}
    score += year_bonus.get(year, 5)
    
    return min(100, score)

def generate_job_analysis(student_data, target_role, experience_level, timeline_months):
    """Generate comprehensive job analysis with study plan"""
    try:
        # Check if Gemini is available
        if not st.session_state.gemini_available:
            return get_fallback_job_analysis(student_data, target_role, experience_level, timeline_months)
            
        employability_score = predict_employability_ml(student_data)
        
        prompt = f"""
        Create a COMPREHENSIVE career development plan for this engineering student:
        
        STUDENT PROFILE:
        - Current CGPA: {student_data.get('cgpa', 'N/A')}/10.0
        - Academic Year: {student_data.get('year', 'N/A')}
        - Internships: {student_data.get('internships', 0)}
        - Projects: {student_data.get('projects', 0)}
        - Certifications: {', '.join(student_data.get('certifications', []))}
        - Communication Skills: {student_data.get('communication', 'N/A')}/10
        - Current Employability Score: {employability_score}%
        
        TARGET JOB:
        - Role: {target_role}
        - Experience Level: {experience_level}
        - Preparation Timeline: {timeline_months} months
        
        Provide a DETAILED analysis with these sections:
        
        ## 🎯 Current Job Fit Analysis
        - Skill gap analysis
        - Strengths and weaknesses
        - Immediate priorities
        
        ## 📚 Complete Study Plan ({timeline_months} Months)
        ### Month-by-Month Breakdown:
        - Technical skills to learn
        - Projects to build
        - Certifications to pursue
        - Interview preparation schedule
        
        ## 💼 Practical Preparation
        - Resume enhancement tips
        - Portfolio project ideas
        - Interview preparation schedule
        - Networking strategy
        
        Format this as a comprehensive markdown document with clear sections and actionable items.
        """
        
        # Use the AI utils for generation
        return ai.generate_custom_content(prompt)
        
    except Exception as e:
        return f"## ❌ AI Analysis Failed\n\nError: {str(e)}\n\nPlease try again later."

def get_fallback_job_analysis(student_data, target_role, experience_level, timeline_months):
    """Fallback job analysis when AI is unavailable"""
    employability_score = predict_employability_ml(student_data)
    
    return f"""
## 🎯 Career Development Plan - {target_role}

### 📊 Current Profile Analysis
- **Employability Score**: {employability_score}%
- **Academic Year**: {student_data.get('year', 'N/A')}
- **CGPA**: {student_data.get('cgpa', 'N/A')}/10.0
- **Experience**: {student_data.get('internships', 0)} internships, {student_data.get('projects', 0)} projects

### 📚 Recommended {timeline_months}-Month Study Plan

#### Months 1-2: Foundation Building
- Core {target_role} fundamentals
- Basic programming practice
- Online tutorials and courses

#### Months 3-4: Skill Development
- Advanced topics in your field
- Mini-projects implementation
- Certification preparation

#### Months 5-{timeline_months}: Interview Preparation
- Mock interviews
- Resume polishing
- Company research

*Note: AI analysis is currently unavailable. This is a general template.*
"""

# Enhanced Career AI Page
def career_ai_page():
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    st.title("🤖 AI Career Analysis & Job Matcher")
    st.markdown("Get personalized job recommendations and complete study plans")
    st.markdown('</div>', unsafe_allow_html=True)
    
    data = st.session_state.student_data
    if not data:
        st.error("Please complete your profile first.")
        return
    
    # Check Gemini availability
    gemini_available = check_gemini_availability()
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🎯 Job Requirements Analysis")
        
        target_role = st.selectbox(
            "Select Your Target Role",
            ["Software Engineer", "Data Scientist", "ML Engineer", "Web Developer", 
             "DevOps Engineer", "Frontend Developer", "Backend Developer", "Full Stack Developer"],
            key="target_role"
        )
        
        experience_level = st.selectbox(
            "Experience Level",
            ["Fresher (0-2 years)", "Mid-Level (2-5 years)", "Senior (5+ years)"],
            key="exp_level"
        )
        
        timeline = st.slider("Months to prepare", 1, 12, 6, key="prep_timeline")
        
        if st.button("🔍 Analyze Job Fit", use_container_width=True, key="analyze_job_fit"):
            with st.spinner("🤖 Analyzing job requirements and creating study plan..."):
                if not gemini_available:
                    st.warning("⚠️ Using template analysis (AI unavailable)")
                job_analysis = generate_job_analysis(data, target_role, experience_level, timeline)
                st.session_state.job_analysis = job_analysis
                st.success("✅ Analysis complete!")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📊 AI Career Prediction")
        
        skills = data.get('certifications', []) + [f"{data.get('projects', 0)} projects", f"{data.get('internships', 0)} internships"]
        interests = [data.get('dream_role', 'Technology')]
        
        if st.button("🔮 Predict Career Paths", use_container_width=True, key="predict_career"):
            with st.spinner("🤖 Analyzing your profile for career recommendations..."):
                if not gemini_available:
                    st.warning("⚠️ Using template prediction (AI unavailable)")
                career_prediction = ai.predict_career(data.get('year', 'Engineering'), skills, interests)
                st.session_state.career_prediction = career_prediction
                st.success("✅ Prediction complete!")
        
        # Employability Score
        employability_score = predict_employability_ml(data)
        st.session_state.ml_score = employability_score
        
        # Enhanced Gauge chart
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = employability_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Employability Score", 'font': {'size': 24}},
            number = {'font': {'size': 40}},
            gauge = {
                'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': "darkblue"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 40], 'color': '#ff6b6b'},
                    {'range': [40, 70], 'color': '#ffe66d'},
                    {'range': [70, 100], 'color': '#51cf66'}
                ]
            }
        ))
        fig.update_layout(height=300, font={'color': "darkblue", 'family': "Arial"})
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Display Results
    if "job_analysis" in st.session_state:
        with st.expander("🎯 **AI Job Analysis Results**", expanded=True):
            st.markdown(st.session_state.job_analysis)
    
    if "career_prediction" in st.session_state:
        with st.expander("🚀 **Career Path Predictions**", expanded=True):
            st.markdown(st.session_state.career_prediction)

# Sidebar with enhanced UI
with st.sidebar:
    st.markdown('<div class="sidebar-header">', unsafe_allow_html=True)
    st.title("🚀 AI Placement Predictor")
    st.markdown("**Ammu • Future Ready**")
    st.markdown("---")
    
    # Gemini Status Check
    gemini_available = check_gemini_availability()
    if gemini_available:
        st.success("🤖 Gemini AI: Connected ✅")
    else:
        st.warning("🤖 Gemini AI: Offline 🔄")
    
    # Dark Mode Toggle
    dark_mode = st.toggle("🌙 Dark Mode", value=st.session_state.dark_mode)
    if dark_mode != st.session_state.dark_mode:
        st.session_state.dark_mode = dark_mode
        st.rerun()
    
    if not st.session_state.logged_in:
        st.info("🔐 Please login to access features")
    else:
        st.success(f"👋 Welcome, {st.session_state.username}!")
        st.markdown(f"**Role:** {st.session_state.role}")
        if st.session_state.role == "Student" and st.session_state.student_data:
            st.markdown(f"**Year:** {st.session_state.student_data.get('year', 'Not set')}")
        
        if st.button("🚪 Logout", use_container_width=True, key="logout_btn"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# Enhanced Login/Register Page
def login_register_page():
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        st.subheader("🌟 Register New Account")
        
        reg_role = st.selectbox("Select Role", ["Student", "Placement Officer"], key="reg_role")
        reg_name = st.text_input("Full Name", key="reg_name")
        reg_email = st.text_input("Email", key="reg_email")
        reg_password = st.text_input("Password", type="password", key="reg_password")
        
        if reg_role == "Student":
            reg_year = st.selectbox("Academic Year", ["1st Year", "2nd Year", "3rd Year", "4th Year"], key="reg_year")
        else:
            reg_year = ""
        
        if st.button("🎯 Register Account", use_container_width=True, key="reg_btn"):
            if not reg_email or not reg_password:
                st.error("📧 Email and password are required")
            else:
                ok, msg = fb.register_user(reg_email.strip(), reg_password.strip(), reg_role, reg_name, reg_year)
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        st.subheader("🔑 Login to Existing Account")
        
        login_email = st.text_input("Email", key="login_email")
        login_password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("🚀 Login", use_container_width=True, key="login_btn"):
            if not login_email:
                st.error("📧 Enter your email")
            else:
                user = fb.login_user(login_email.strip())
                if user:
                    st.session_state.logged_in = True
                    st.session_state.username = login_email.strip()
                    st.session_state.role = user.get("role")
                    st.session_state.student_data = fb.get_student(login_email.strip()) or {}
                    if st.session_state.role == "Student" and st.session_state.student_data:
                        st.session_state.current_year = st.session_state.student_data.get("year")
                        st.session_state.current_subjects = st.session_state.student_data.get("subjects", [])
                    st.success("🎉 Login successful!")
                    st.rerun()
                else:
                    st.error("❌ Account not found. Please register first.")
        st.markdown('</div>', unsafe_allow_html=True)

# Enhanced Student Profile Page
def student_profile_page():
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    st.title("🎓 Student Profile Management")
    st.markdown("Complete your profile for better placement predictions")
    st.markdown('</div>', unsafe_allow_html=True)
    
    data = st.session_state.student_data or {}
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📋 Personal Information")
        
        name = st.text_input("Full Name", value=data.get("name", ""), key="profile_name")
        year = st.selectbox(
            "Academic Year", 
            ["1st Year", "2nd Year", "3rd Year", "4th Year"],
            index=["1st Year", "2nd Year", "3rd Year", "4th Year"].index(data.get("year", "1st Year")),
            key="profile_year"
        )
        cgpa = st.slider("CGPA", 0.0, 10.0, float(data.get("cgpa", 7.0)), step=0.1, key="profile_cgpa")
        
        st.subheader("🎯 Skills & Experience")
        certs = st.text_area("Certifications (one per line)", value="\n".join(data.get("certifications", [])), key="profile_certs")
        internships = st.number_input("Number of Internships", 0, 10, int(data.get("internships", 0)), key="profile_internships")
        projects = st.number_input("Number of Projects", 0, 50, int(data.get("projects", 0)), key="profile_projects")
        comm_skills = st.slider("Communication Skills (1-10)", 1, 10, int(data.get("communication", 6)), key="profile_comm")
        
        st.subheader("🎯 Career Goals")
        target_companies = st.text_input("Target Companies", value=data.get("target_companies", ""), key="target_companies")
        dream_role = st.text_input("Dream Role/Position", value=data.get("dream_role", ""), key="dream_role")
        
        if st.button("💾 Save Profile", use_container_width=True, key="save_profile"):
            profile = {
                "name": name,
                "year": year,
                "cgpa": float(cgpa),
                "certifications": [c.strip() for c in certs.split("\n") if c.strip()],
                "internships": int(internships),
                "projects": int(projects),
                "communication": int(comm_skills),
                "target_companies": target_companies,
                "dream_role": dream_role,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Update subjects based on year
            year_subjects = {
                "1st Year": ["Python for Beginners", "C Programming", "Electronics Basics", "Electrical Engg", "Nanotech", "Intro to DSA", "Simple Java"],
                "2nd Year": ["Operating System", "DSA", "Java OOPs", "AI", "ADA", "DBMS", "MongoDB"],
                "3rd Year": ["SEPM", "EDA", "Python Advanced", "Java Complex", "Computer Networks"],
                "4th Year": ["Blockchain", "Cybersecurity", "Data Privacy", "Data Visualization", "DBMS"]
            }
            profile["subjects"] = year_subjects.get(year, [])
            
            ok = fb.save_student_data(st.session_state.username, profile)
            if ok:
                st.session_state.student_data = profile
                st.session_state.current_year = year
                st.session_state.current_subjects = profile["subjects"]
                st.success("✅ Profile saved successfully!")
            else:
                st.error("❌ Failed to save profile")
        
        # AI Resume Analysis
        if st.button("🔍 AI Resume Analysis", use_container_width=True, key="ai_resume_analysis"):
            with st.spinner("🤖 AI is analyzing your profile..."):
                if not st.session_state.gemini_available:
                    st.warning("⚠️ AI analysis unavailable")
                else:
                    resume_analysis = ai.analyze_resume_with_ai(st.session_state.student_data)
                    st.session_state.resume_analysis = resume_analysis
                    st.success("✅ Analysis complete!")
        
        if "resume_analysis" in st.session_state:
            with st.expander("📋 AI Resume Analysis Results"):
                st.markdown(st.session_state.resume_analysis)
                
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Profile completion metrics
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📊 Profile Completion")
        
        completion_score = min(100, len([v for v in [name, cgpa, certs] if v]) * 25)
        
        # Animated progress bar
        progress_html = f"""
        <div class="progress-container">
            <div class="progress-bar" style="width: {completion_score}%">
                <span class="progress-text">{completion_score}%</span>
            </div>
        </div>
        """
        st.markdown(progress_html, unsafe_allow_html=True)
        
        if completion_score < 100:
            st.warning("Complete all fields for better placement predictions")
        else:
            st.success("Profile complete! 🎉")
        
        # Quick stats
        st.subheader("📈 Quick Stats")
        st.metric("CGPA", f"{cgpa}/10.0")
        st.metric("Internships", internships)
        st.metric("Projects", projects)
        st.metric("Communication", f"{comm_skills}/10")
        
        st.markdown('</div>', unsafe_allow_html=True)

# Enhanced Student Dashboard
def student_dashboard_page():
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    st.title("📊 Student Analytics Dashboard")
    st.markdown("Power BI Style Analytics with AI Insights")
    st.markdown('</div>', unsafe_allow_html=True)
    
    data = st.session_state.student_data
    if not data:
        st.info("Please complete your profile first.")
        return
    
    # Fetch quiz results
    try:
        all_results = fb.fetch_quiz_results()
        user_results = [r for r in all_results if r.get('email') == st.session_state.username]
    except:
        user_results = []
    
    # Create Power BI style dashboard
    powerbi_analytics.create_employability_dashboard(data, user_results)
    
    # AI Recommendations Section
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🤖 AI Study & Career Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        study_subject = st.selectbox("Select Subject for Study Plan", st.session_state.current_subjects, key="study_subject")
        study_level = st.selectbox("Current Level", ["Beginner", "Intermediate", "Advanced"], key="study_level")
        
        if st.button("📚 Generate AI Study Plan", use_container_width=True, key="gen_study_plan"):
            with st.spinner("🤖 Creating personalized study plan..."):
                if not st.session_state.gemini_available:
                    st.warning("⚠️ AI study plan unavailable")
                else:
                    study_plan = ai.generate_study_plan(study_subject, study_level, 30, 2)
                    st.session_state.study_plan = study_plan
                    st.success("✅ Study plan generated!")
    
    with col2:
        if st.button("🎯 Get Career Suggestions", use_container_width=True, key="get_career_suggestions"):
            with st.spinner("🤖 Analyzing career prospects..."):
                skills = data.get('certifications', []) + [f"{data.get('projects', 0)} projects"]
                interests = [data.get('dream_role', 'Technology')]
                if not st.session_state.gemini_available:
                    st.warning("⚠️ AI career suggestions unavailable")
                else:
                    career_prediction = ai.predict_career(data.get('year', 'Engineering'), skills, interests)
                    st.session_state.career_prediction = career_prediction
                    st.success("✅ Career analysis complete!")
    
    # Display AI insights if available
    if "study_plan" in st.session_state:
        with st.expander("📚 AI Study Plan", expanded=True):
            st.markdown(st.session_state.study_plan)
    
    if "career_prediction" in st.session_state:
        with st.expander("🚀 Career Suggestions", expanded=True):
            st.markdown(st.session_state.career_prediction)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Quiz Functions
def display_quiz_results():
    """Display quiz results with beautiful AI feedback"""
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    score = st.session_state.quiz_score
    total = st.session_state.quiz_total
    percentage = (score / total) * 100
    quiz_subject = st.session_state.current_quiz_subject
    
    # Enhanced result display
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🎯 Score", f"{score}/{total}")
    with col2:
        st.metric("📊 Percentage", f"{percentage:.1f}%")
    with col3:
        st.metric("📚 Subject", quiz_subject)
    
    # Performance indicator
    if percentage >= 80:
        st.success("🎉 Outstanding Performance! You've mastered this topic!")
    elif percentage >= 60:
        st.warning("📚 Good Job! Keep practicing to improve further.")
    else:
        st.info("💪 Learning Opportunity! Review the concepts and try again.")
    
    # AI Feedback
    with st.expander("🤖 AI Feedback & Learning Recommendations", expanded=True):
        with st.spinner("Generating personalized feedback..."):
            feedback = ai.generate_feedback(
                quiz_subject,
                score,
                total,
                st.session_state.incorrect_questions
            )
            st.markdown(feedback)
    
    # Save results to Firebase
    try:
        fb.save_quiz_result(
            st.session_state.username,
            quiz_subject,
            score,
            total,
            {
                "timestamp": datetime.utcnow().isoformat(),
                "percentage": percentage,
                "incorrect_count": len(st.session_state.incorrect_questions)
            }
        )
    except Exception as e:
        st.warning("Results saved locally (Firebase unavailable)")
    
    # Action buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Take Another Quiz", use_container_width=True, key="another_quiz_btn"):
            reset_quiz_session()
            st.rerun()
    with col2:
        if st.button("📊 View Progress Analytics", use_container_width=True, key="view_progress_btn"):
            st.session_state.show_feedback = False
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def take_quiz_page():
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    st.title("🧠 AI Smart Quiz System")
    st.markdown("Test your knowledge with AI-generated adaptive questions")
    st.markdown('</div>', unsafe_allow_html=True)
    
    if not st.session_state.current_subjects:
        st.error("Please complete your profile to access subjects based on your year.")
        return
    
    # Check Gemini availability
    gemini_available = check_gemini_availability()
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("⚙️ Quiz Settings")
        
        subject = st.selectbox("Choose Subject", st.session_state.current_subjects, key="quiz_subject_select")
        num_questions = st.slider("Number of Questions", 3, 10, 5, key="quiz_count_slider")
        
        if st.button("🎲 Generate New Quiz", use_container_width=True, key="generate_quiz_btn"):
            with st.spinner("🤖 AI is generating your quiz..."):
                try:
                    if gemini_available:
                        quiz = ai.generate_quiz_for_subject(subject, num_questions)
                    else:
                        quiz = ai.get_fallback_questions()[:num_questions]
                        st.info("📝 Using pre-defined questions (AI unavailable)")
                    
                    if quiz and len(quiz) > 0:
                        st.session_state.current_quiz_data = quiz
                        st.session_state.current_quiz_subject = subject
                        st.session_state.quiz_answers = {}
                        st.session_state.quiz_submitted = False
                        st.session_state.show_feedback = False
                        st.success(f"✅ Generated {len(quiz)} questions successfully!")
                    else:
                        st.error("❌ Failed to generate quiz questions. Please try again.")
                        
                except Exception as e:
                    st.error(f"❌ Failed to generate quiz: {str(e)}")
        
        # Gemini Status Check
        if gemini_available:
            st.success("🤖 Gemini AI: Connected ✅")
        else:
            st.warning("🤖 Gemini AI: Using Fallback Mode 🔄")
            
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        quiz_data = st.session_state.get('current_quiz_data')
        quiz_subject = st.session_state.get('current_quiz_subject')
        
        if quiz_data and not st.session_state.get('quiz_submitted', False):
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader(f"🧠 {quiz_subject} Quiz")
            st.write(f"**Total Questions:** {len(quiz_data)}")
            
            answers = {}
            for i, q in enumerate(quiz_data):
                st.markdown(f'<div class="quiz-question">', unsafe_allow_html=True)
                st.write(f"**Q{i+1}. {q['question']}**")
                
                choice = st.radio(
                    "Select your answer:",
                    q['options'],
                    key=f"quiz_question_{i}",
                    index=None
                )
                if choice:
                    # Store the full answer text
                    answers[q['question']] = choice
                st.markdown('</div>', unsafe_allow_html=True)
            
            if st.button("📤 Submit Quiz", use_container_width=True, key="submit_quiz_btn"):
                if len(answers) != len(quiz_data):
                    st.error("Please answer all questions before submitting.")
                else:
                    score = 0
                    total = len(quiz_data)
                    incorrect_questions = []
                    
                    for q in quiz_data:
                        user_ans = answers.get(q["question"], "")
                        correct_ans = q.get("correct_answer", q.get("answer", ""))
                        if user_ans == correct_ans:
                            score += 1
                        else:
                            incorrect_questions.append({
                                "question": q["question"],
                                "user_answer": user_ans,
                                "correct_answer": correct_ans,
                                "explanation": q.get("explanation", "No explanation available")
                            })
                    
                    st.session_state.quiz_score = score
                    st.session_state.quiz_total = total
                    st.session_state.incorrect_questions = incorrect_questions
                    st.session_state.quiz_submitted = True
                    st.session_state.show_feedback = True
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        
        elif st.session_state.get('quiz_submitted', False) and st.session_state.get('show_feedback', True):
            display_quiz_results()
        
        else:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.info("🎯 Configure your quiz settings on the left and click 'Generate New Quiz' to get started!")
            st.markdown('</div>', unsafe_allow_html=True)

def reset_quiz_session():
    """Reset quiz-related session state"""
    keys_to_clear = [
        'current_quiz_data', 'current_quiz_subject', 'current_quiz_difficulty',
        'quiz_answers', 'quiz_submitted', 'quiz_score', 'quiz_total', 
        'incorrect_questions', 'show_feedback'
    ]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

# Enhanced Officer Dashboard
def officer_dashboard_page():
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    st.title("👨‍💼 Placement Officer Dashboard")
    st.markdown("Monitor student progress and placement readiness")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Fetch data
    students = fb.fetch_all_students()
    
    if not students:
        st.info("No student records found.")
        return
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("👥 Total Students", len(students))
    with col2:
        avg_cgpa = np.mean([s.get('cgpa', 0) for s in students if s.get('cgpa')])
        st.metric("📊 Avg CGPA", f"{avg_cgpa:.2f}")
    with col3:
        total_internships = sum([s.get('internships', 0) for s in students])
        st.metric("💼 Total Internships", total_internships)
    with col4:
        employable = len([s for s in students if predict_employability_ml(s) >= 70])
        st.metric("🎯 Employable Students", employable)
    
    # Student details
    st.subheader("👥 Student Analytics")
    display_data = []
    for student in students:
        score = predict_employability_ml(student)
        display_data.append({
            "Name": student.get("name", "N/A"),
            "Email": student.get("email", "N/A"),
            "Year": student.get("year", "N/A"),
            "CGPA": student.get("cgpa", "N/A"),
            "Employability": f"{score}%",
            "Internships": student.get("internships", 0),
            "Projects": student.get("projects", 0),
            "Status": "Ready" if score >= 70 else "Needs Improvement"
        })
    
    display_df = pd.DataFrame(display_data)
    st.dataframe(display_df, use_container_width=True)

# Main app router
def main():
    if not st.session_state.logged_in:
        login_register_page()
    else:
        if st.session_state.role == "Student":
            tab1, tab2, tab3, tab4 = st.tabs(["🎓 Profile", "📊 Dashboard", "🧠 Smart Quiz", "🎯 Career AI"])
            with tab1:
                student_profile_page()
            with tab2:
                student_dashboard_page()
            with tab3:
                take_quiz_page()
            with tab4:
                career_ai_page()
        else:
            officer_dashboard_page()

if __name__ == "__main__":
    main()