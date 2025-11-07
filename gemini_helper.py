# gemini_helper.py
import os
import json
import logging
import google.generativeai as genai
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ---------------------------------------------------------------------
# ⚙️ Configuration - API Key
# ---------------------------------------------------------------------
GEMINI_API_KEY = "AIzaSyAJmr-qKnkXHMG907pxpVKMkp_wKWZsUlw"

# Configure Gemini with the API key
try:
    genai.configure(api_key=GEMINI_API_KEY)
    logging.info("✅ Gemini API configured successfully")
except Exception as e:
    logging.error(f"❌ Gemini configuration failed: {e}")

# ---------------------------------------------------------------------
# 🎯 Model Configuration
# ---------------------------------------------------------------------
def get_gemini_model():
    """Get the best available Gemini model"""
    try:
        # Try different models in order of preference
        model_priority = [
            'model/gemini-2.5-flash'
        ]
        
        available_models = [model.name for model in genai.list_models()]
        logging.info(f"📋 Available models: {available_models}")
        
        for model_name in model_priority:
            full_model_name = f"models/{model_name}"
            if full_model_name in available_models:
                model = genai.GenerativeModel(full_model_name)
                logging.info(f"✅ Using model: {full_model_name}")
                return model
        
        # Fallback to any available Gemini model
        for model_name in available_models:
            if 'gemini' in model_name.lower():
                model = genai.GenerativeModel(model_name)
                logging.info(f"🔄 Using fallback model: {model_name}")
                return model
        
        logging.error("❌ No Gemini models available")
        return None
        
    except Exception as e:
        logging.error(f"❌ Model selection failed: {e}")
        return None

# ---------------------------------------------------------------------
# 🧠 Generate Custom Content (Core Function)
# ---------------------------------------------------------------------
def generate_custom_content(prompt: str, context: Dict[str, Any] = None) -> str:
    """Generate custom content using Gemini AI with proper API integration"""
    try:
        # Build enhanced prompt with context
        enhanced_prompt = prompt
        if context:
            context_str = "\n".join([f"{key}: {value}" for key, value in context.items()])
            enhanced_prompt = f"CONTEXT INFORMATION:\n{context_str}\n\nMAIN TASK:\n{prompt}"
        
        # Get the model
        model = get_gemini_model()
        if not model:
            return "❌ AI service temporarily unavailable. Please try again later."
        
        # Generate response
        response = model.generate_content(enhanced_prompt)
        
        if response.text:
            logging.info("✅ Content generated successfully")
            return response.text.strip()
        else:
            logging.error("❌ Empty response from Gemini API")
            return "❌ I apologize, but I couldn't generate a response. Please try again."
            
    except Exception as e:
        logging.error(f"❌ Content generation failed: {e}")
        return f"❌ I encountered an error while generating content. Please try again later."

# ---------------------------------------------------------------------
# 📚 Study Plan Generation
# ---------------------------------------------------------------------
def generate_study_plan_content(subject: str, level: str, days_available: int, hours_per_day: int) -> str:
    """Generate comprehensive study plan"""
    prompt = f"""
    Create a detailed {days_available}-day study plan for {subject} at {level} level.
    
    SPECIFIC REQUIREMENTS:
    - Duration: {days_available} days
    - Daily study time: {hours_per_day} hours
    - Subject: {subject}
    - Level: {level}
    
    Please structure the study plan with:
    1. 🎯 Learning Objectives - Clear goals for the entire period
    2. 📅 Daily Schedule - Detailed day-by-day plan
    3. 📖 Topics Breakdown - Specific topics to cover each day
    4. 🏋️ Practice Exercises - Hands-on activities and exercises
    5. 🔄 Revision Strategy - How to review and reinforce learning
    6. 📊 Progress Tracking - Milestones and checkpoints
    7. 💡 Study Tips - Effective learning strategies for this subject
    
    Make the plan practical, achievable, and tailored to the specified time commitment.
    Include time for breaks, revision, and practice tests.
    """
    
    context = {
        "content_type": "study_plan",
        "subject": subject,
        "level": level,
        "duration_days": days_available,
        "daily_hours": hours_per_day,
        "total_study_hours": days_available * hours_per_day
    }
    
    return generate_custom_content(prompt, context)

# ---------------------------------------------------------------------
# 💼 Career Prediction
# ---------------------------------------------------------------------
def generate_career_prediction(subject: str, skills: List[str], interests: List[str]) -> str:
    """Generate career path predictions"""
    prompt = f"""
    Based on the following student profile, suggest suitable career paths:
    
    STUDENT PROFILE:
    - Primary Subject Interest: {subject}
    - Technical Skills: {', '.join(skills) if skills else 'Not specified'}
    - Personal Interests: {', '.join(interests) if interests else 'Not specified'}
    
    Please provide comprehensive career guidance including:
    
    1. 🎯 CAREER PATHS (3-5 options):
       For each career, include:
       - Job title and overview
       - Daily responsibilities
       - Industry applications
       - Future prospects
    
    2. 📚 REQUIRED QUALIFICATIONS:
       - Educational requirements
       - Certifications needed
       - Skill development path
    
    3. 🚀 GROWTH OPPORTUNITIES:
       - Entry-level to senior progression
       - Salary expectations
       - Industry demand
    
    4. 🔧 SKILL ENHANCEMENT:
       - Specific skills to develop
       - Recommended courses/tools
       - Project suggestions
    
    5. 📅 ACTION PLAN:
       - Short-term steps (next 6 months)
       - Medium-term goals (1-2 years)
       - Long-term career trajectory
    
    Provide realistic, practical advice tailored to the student's profile.
    """
    
    context = {
        "content_type": "career_prediction",
        "subject": subject,
        "skills": skills,
        "interests": interests,
        "analysis_type": "comprehensive_career_guidance"
    }
    
    return generate_custom_content(prompt, context)

# ---------------------------------------------------------------------
# 🧩 Generate Quiz Questions
# ---------------------------------------------------------------------
def generate_quiz(subject: str, num_questions: int = 5) -> List[Dict[str, Any]]:
    """Generate quiz questions with robust error handling"""
    if not subject:
        logging.warning("No subject provided, using fallback questions")
        return get_fallback_questions()[:num_questions]

    prompt = f"""
    Create {num_questions} multiple-choice questions for '{subject}' suitable for engineering students.
    
    REQUIREMENTS:
    - Exactly {num_questions} questions
    - Diverse difficulty levels
    - Practical, application-based questions
    - Clear and unambiguous options
    
    FORMAT REQUIREMENTS - Return ONLY valid JSON:
    [
        {{
            "question": "Clear question text?",
            "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
            "answer": "A",
            "explanation": "Brief explanation of why this is correct"
        }}
    ]
    
    Important: Return ONLY the JSON array, no additional text or markdown formatting.
    """

    try:
        response_text = generate_custom_content(prompt, {"type": "quiz", "subject": subject})
        
        if response_text and not response_text.startswith("❌"):
            questions = parse_quiz_response(response_text)
            if questions and len(questions) > 0:
                logging.info(f"✅ Generated {len(questions)} questions for {subject}")
                return questions[:num_questions]
        
        logging.warning("❌ Quiz generation failed, using fallback")
        return get_fallback_questions()[:num_questions]
            
    except Exception as e:
        logging.error(f"❌ Quiz generation failed: {e}")
        return get_fallback_questions()[:num_questions]

def parse_quiz_response(response_text: str) -> List[Dict[str, Any]]:
    """Parse the quiz response with multiple strategies"""
    if not response_text:
        return None
        
    cleaned_text = response_text.strip()
    
    # Strategy 1: Try to extract JSON from markdown code blocks
    if '```json' in cleaned_text:
        start_idx = cleaned_text.find('```json') + 7
        end_idx = cleaned_text.find('```', start_idx)
        if start_idx > 6 and end_idx > start_idx:
            json_str = cleaned_text[start_idx:end_idx].strip()
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass
    
    # Strategy 2: Try to find JSON array directly
    start_idx = cleaned_text.find('[')
    end_idx = cleaned_text.rfind(']') + 1
    
    if start_idx >= 0 and end_idx > start_idx:
        json_str = cleaned_text[start_idx:end_idx]
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass
    
    # Strategy 3: Try parsing entire response
    try:
        return json.loads(cleaned_text)
    except json.JSONDecodeError as e:
        logging.error(f"❌ Failed to parse JSON from response: {e}")
        return None

# ---------------------------------------------------------------------
# 🎯 Generate Feedback
# ---------------------------------------------------------------------
def generate_feedback(subject: str, score: int, total: int, incorrect_questions: List[Dict]) -> str:
    """Generate personalized feedback"""
    prompt = f"""
    Provide constructive feedback for a student who scored {score} out of {total} in {subject}.
    
    PERFORMANCE ANALYSIS:
    - Score: {score}/{total} ({(score/total)*100:.1f}%)
    - Areas needing improvement: Based on incorrect answers
    
    Please provide:
    1. 📊 Performance Summary - Overall assessment
    2. 🎯 Weak Areas - Specific topics that need attention
    3. 📚 Study Recommendations - Concrete actions to improve
    4. 💪 Encouragement - Motivational message
    5. 🚀 Next Steps - Immediate actions to take
    
    Be constructive, specific, and encouraging. Focus on growth and improvement.
    """
    
    try:
        context = {
            "type": "feedback",
            "subject": subject, 
            "score": score, 
            "total": total,
            "performance_percentage": f"{(score/total)*100:.1f}%"
        }
        
        return generate_custom_content(prompt, context)
    except Exception as e:
        logging.error(f"❌ Feedback generation failed: {e}")
        return get_fallback_feedback(subject, score, total, incorrect_questions)

# ---------------------------------------------------------------------
# 🧠 Fallback Content
# ---------------------------------------------------------------------
def get_fallback_questions() -> List[Dict[str, Any]]:
    """Reliable fallback questions"""
    return [
        {
            "question": "Which data structure follows LIFO principle?",
            "options": ["A) Queue", "B) Stack", "C) Array", "D) Linked List"],
            "answer": "B",
            "explanation": "Stack follows Last-In-First-Out (LIFO) principle"
        },
        {
            "question": "What is the time complexity of binary search?",
            "options": ["A) O(n)", "B) O(log n)", "C) O(n²)", "D) O(1)"],
            "answer": "B",
            "explanation": "Binary search has O(log n) time complexity"
        },
        {
            "question": "Which language is primarily used for machine learning?",
            "options": ["A) Java", "B) Python", "C) C++", "D) HTML"],
            "answer": "B",
            "explanation": "Python is widely used in machine learning due to its libraries"
        },
        {
            "question": "What does SQL stand for?",
            "options": ["A) Structured Query Language", "B) Simple Question Language", "C) System Query Logic", "D) Standard Question Format"],
            "answer": "A",
            "explanation": "SQL stands for Structured Query Language"
        },
        {
            "question": "Which protocol is used for secure web browsing?",
            "options": ["A) HTTP", "B) FTP", "C) HTTPS", "D) SMTP"],
            "answer": "C",
            "explanation": "HTTPS provides secure encrypted communication"
        }
    ]

def get_fallback_feedback(subject: str, score: int, total: int, incorrect_questions: List[Dict]) -> str:
    """Fallback feedback template"""
    percentage = (score/total)*100 if total > 0 else 0
    return f"""
## 📊 Quiz Results for {subject}

**Score:** {score}/{total} ({percentage:.1f}%)

### 🎯 Performance Summary:
{'✅ Excellent work! Keep it up!' if percentage >= 80 else '👍 Good effort! Some areas need improvement.' if percentage >= 60 else '📚 Keep practicing! You\'re making progress.'}

### 🔍 Areas to Improve:
- Review fundamental concepts
- Practice application-based questions
- Focus on time management

### 📚 Recommended Actions:
1. Review core topics in {subject}
2. Practice with similar questions
3. Join study groups for discussion
4. Use online resources for clarification

### 💡 Pro Tip:
"Consistent practice is key to mastery. Don't get discouraged - every mistake is a learning opportunity!"

### 🎯 Next Steps:
- Create a study schedule
- Focus on weak areas identified
- Take regular practice tests
- Seek help when needed

**Remember:** Progress takes time. Celebrate your improvements! 🎉
"""

# ---------------------------------------------------------------------
# 🔧 Test Functions
# ---------------------------------------------------------------------
def test_gemini_connection() -> bool:
    """Test if Gemini API is working"""
    try:
        model = get_gemini_model()
        if model:
            response = model.generate_content("Say 'CONNECTION_SUCCESS' in one word.")
            if response.text and "CONNECTION_SUCCESS" in response.text.upper():
                logging.info("✅ Gemini connection test passed")
                return True
        return False
    except Exception as e:
        logging.error(f"❌ Gemini connection test failed: {e}")
        return False

def test_study_plan_generation():
    """Test study plan generation"""
    print("\n🧪 Testing Study Plan Generation...")
    try:
        study_plan = generate_study_plan_content("Python Programming", "Beginner", 7, 2)
        if study_plan and not study_plan.startswith("❌"):
            print("✅ Study plan generated successfully!")
            print(f"Preview: {study_plan[:200]}...")
            return True
        else:
            print("❌ Study plan generation failed")
            return False
    except Exception as e:
        print(f"❌ Study plan test failed: {e}")
        return False

def test_career_prediction():
    """Test career prediction"""
    print("\n🧪 Testing Career Prediction...")
    try:
        career_advice = generate_career_prediction(
            "Computer Science", 
            ["Python", "Data Structures"], 
            ["AI", "Web Development"]
        )
        if career_advice and not career_advice.startswith("❌"):
            print("✅ Career prediction generated successfully!")
            print(f"Preview: {career_advice[:200]}...")
            return True
        else:
            print("❌ Career prediction failed")
            return False
    except Exception as e:
        print(f"❌ Career prediction test failed: {e}")
        return False

# Auto-test on import
if __name__ == "__main__":
    print("🔍 Testing Gemini Integration...")
    print("=" * 50)
    
    if test_gemini_connection():
        test_study_plan_generation()
        test_career_prediction()
        print("\n✅ All tests completed!")
    else:
        print("\n❌ Gemini connection failed. Please check your API key.")