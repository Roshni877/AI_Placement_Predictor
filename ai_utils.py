# ai_utils.py
import logging
from typing import List, Dict, Any
import google.generativeai as genai
import json
import time

# Configure Gemini API with your working key
GEMINI_API_KEY = "AIzaSyAJmr-qKnkXHMG907pxpVKMkp_wKWZsUlw"

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Global variables
_gemini_configured = False
_available_models = []
_current_model = None

def setup_gemini():
    """Setup Gemini API with proper error handling"""
    global _gemini_configured, _available_models, _current_model
    
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        logging.info("✅ Gemini API configured successfully")
        
        # List models to verify connection
        _available_models = [model.name for model in genai.list_models()]
        logging.info(f"📋 Available Gemini models: {_available_models}")
        
        # Try to initialize a model
        _current_model = get_best_model()
        _gemini_configured = _current_model is not None
        
        return _gemini_configured
        
    except Exception as e:
        logging.error(f"❌ Gemini configuration failed: {e}")
        _gemini_configured = False
        _current_model = None
        return False

# Auto-setup on import
setup_gemini()

def get_gemini_status() -> bool:
    """Check if Gemini AI is working"""
    global _gemini_configured, _current_model
    
    if not _gemini_configured:
        return setup_gemini()
    
    try:
        # Quick test with a simple generation
        if _current_model:
            test_response = safe_generate_content(_current_model, "Say 'OK' in one word.")
            return test_response is not None and len(test_response.strip()) > 0
        return False
    except Exception as e:
        logging.error(f"Gemini status check failed: {e}")
        _gemini_configured = False
        _current_model = None
        return False

def get_best_model():
    """Get the best available Gemini model with fallbacks"""
    global _available_models
    
    if not _available_models:
        try:
            _available_models = [model.name for model in genai.list_models()]
        except Exception as e:
            logging.error(f"Failed to fetch available models: {e}")
            return None
    
    try:
        # Updated model priority with Gemini 2.5 Flash
        model_priority = [
            'models/gemini-2.5-flash-exp',  # Latest experimental
            'models/gemini-2.5-flash',
            'models/gemini-1.5-flash',
            'models/gemini-1.5-pro',
            'models/gemini-1.0-pro'
        ]
        
        for model_name in model_priority:
            full_model_name = model_name if model_name.startswith('models/') else f"models/{model_name}"
            if full_model_name in _available_models:
                try:
                    model = genai.GenerativeModel(full_model_name)
                    # Test the model with a simple request
                    test_response = model.generate_content("Test")
                    if test_response.text:
                        logging.info(f"✅ Successfully loaded model: {full_model_name}")
                        return model
                except Exception as e:
                    logging.warning(f"Failed to load model {full_model_name}: {e}")
                    continue
        
        # If no specific model works, try any available model
        for model_name in _available_models:
            if 'gemini' in model_name.lower() and 'generateContent' in str(genai.get_model(model_name).supported_generation_methods):
                try:
                    model = genai.GenerativeModel(model_name)
                    test_response = model.generate_content("Test")
                    if test_response.text:
                        logging.info(f"🔄 Using fallback model: {model_name}")
                        return model
                except Exception as e:
                    continue
        
        logging.error("❌ No working Gemini models available")
        return None
        
    except Exception as e:
        logging.error(f"❌ Model selection failed: {e}")
        return None

def safe_generate_content(model, prompt, max_retries=3):
    """Safely generate content with retries"""
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            if response.text and response.text.strip():
                return response.text.strip()
            else:
                logging.warning(f"Empty response on attempt {attempt + 1}")
        except Exception as e:
            logging.warning(f"Generation failed on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                time.sleep(1)  # Wait before retry
    return None

def generate_quiz_for_subject(subject: str, num_questions: int = 5) -> List[Dict[str, Any]]:
    """Generate quiz for a subject with robust error handling"""
    try:
        if not get_gemini_status():
            logging.warning("Gemini unavailable, using fallback questions")
            return get_fallback_questions()[:num_questions]
            
        model = get_best_model()
        if not model:
            return get_fallback_questions()[:num_questions]
        
        prompt = f"""
        Generate exactly {num_questions} multiple choice quiz questions about {subject} for engineering students.
        
        IMPORTANT: Return ONLY valid JSON format - no other text, no explanations, no markdown.
        
        Required JSON structure:
        [
            {{
                "question": "Clear and concise question text?",
                "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
                "answer": "A",
                "explanation": "Brief explanation of why this is correct"
            }}
        ]
        
        Rules:
        - Generate exactly {num_questions} questions
        - Each question must have exactly 4 options labeled A), B), C), D)
        - Answer should be the letter (A, B, C, or D)
        - Make questions practical and relevant to engineering students
        - Ensure questions are diverse and cover different aspects of {subject}
        """
        
        response_text = safe_generate_content(model, prompt)
        if not response_text:
            logging.warning("No response from Gemini, using fallback")
            return get_fallback_questions()[:num_questions]
        
        # Clean and parse response
        cleaned_text = response_text.strip()
        
        # Remove markdown code blocks if present
        if '```json' in cleaned_text:
            cleaned_text = cleaned_text.split('```json')[1].split('```')[0].strip()
        elif '```' in cleaned_text:
            cleaned_text = cleaned_text.split('```')[1].strip()
        
        # Remove any leading/trailing non-JSON text
        start_idx = cleaned_text.find('[')
        end_idx = cleaned_text.rfind(']') + 1
        if start_idx >= 0 and end_idx > start_idx:
            cleaned_text = cleaned_text[start_idx:end_idx]
        
        try:
            questions = json.loads(cleaned_text)
            
            # Validate and format questions
            validated_questions = []
            for q in questions:
                if all(key in q for key in ['question', 'options', 'answer']):
                    # Ensure answer is single letter
                    if isinstance(q['answer'], str) and len(q['answer']) > 0:
                        q['answer'] = q['answer'][0].upper()
                    validated_questions.append(q)
            
            if validated_questions:
                logging.info(f"✅ Generated {len(validated_questions)} valid questions")
                return validated_questions[:num_questions]
            else:
                logging.warning("No valid questions found in response")
                return get_fallback_questions()[:num_questions]
                
        except json.JSONDecodeError as e:
            logging.error(f"JSON parsing failed: {e}")
            logging.error(f"Raw response: {cleaned_text}")
            return get_fallback_questions()[:num_questions]
            
    except Exception as e:
        logging.error(f"Quiz generation failed: {e}")
        return get_fallback_questions()[:num_questions]

def generate_feedback(subject: str, score: int, total: int, incorrect_questions: List[Dict]) -> str:
    """Generate feedback with error handling"""
    try:
        if not get_gemini_status():
            return get_fallback_feedback(subject, score, total, incorrect_questions)
            
        model = get_best_model()
        if not model:
            return get_fallback_feedback(subject, score, total, incorrect_questions)
        
        incorrect_summary = "\n".join([
            f"- Q: {q.get('question', 'Unknown')} (Your answer: {q.get('user', 'N/A')}, Correct: {q.get('correct', 'N/A')})"
            for q in incorrect_questions
        ])
        
        prompt = f"""
        Create constructive and encouraging feedback for an engineering student.
        
        Quiz Results:
        - Subject: {subject}
        - Score: {score}/{total} ({(score/total)*100:.1f}%)
        - Incorrect Questions: {len(incorrect_questions)}
        
        Incorrect Questions Summary:
        {incorrect_summary}
        
        Please provide:
        1. **Performance Summary** - Overall assessment
        2. **Strengths** - What they did well
        3. **Areas for Improvement** - Specific topics to focus on
        4. **Study Recommendations** - Concrete action steps
        5. **Encouragement** - Motivational closing
        
        Format in clear markdown with emojis. Be supportive, specific, and helpful.
        Focus on growth mindset and practical next steps.
        """
        
        response_text = safe_generate_content(model, prompt)
        return response_text or get_fallback_feedback(subject, score, total, incorrect_questions)
        
    except Exception as e:
        logging.error(f"Feedback generation failed: {e}")
        return get_fallback_feedback(subject, score, total, incorrect_questions)

def generate_custom_content(prompt: str, context: Dict[str, Any] = None) -> str:
    """Generate custom content using Gemini AI"""
    try:
        if not get_gemini_status():
            return "🔴 AI service is currently unavailable. Please try again later."
            
        model = get_best_model()
        if not model:
            return "🔴 AI service is currently unavailable. Please try again later."
        
        full_prompt = prompt
        if context:
            context_str = "\n".join([f"{key}: {value}" for key, value in context.items()])
            full_prompt = f"Context:\n{context_str}\n\nTask:\n{prompt}"
        
        response_text = safe_generate_content(model, full_prompt)
        return response_text or "🔴 Sorry, I couldn't generate a response. Please try again."
        
    except Exception as e:
        logging.error(f"Custom content generation failed: {e}")
        return f"🔴 Error generating content: {str(e)}"

def generate_study_plan(subject: str, level: str, days_available: int, hours_per_day: int) -> str:
    """Generate study plan using Gemini AI"""
    try:
        if not get_gemini_status():
            return "🔴 AI service unavailable. Cannot generate study plan."
            
        prompt = f"""
        Create a comprehensive {days_available}-day study plan for {subject} at {level} level.
        
        Constraints:
        - Study time: {hours_per_day} hours per day
        - Total days: {days_available}
        - Target audience: Engineering students
        
        Include in the study plan:
        - **Learning Objectives**: Clear goals for each week
        - **Daily Schedule**: Hour-by-hour breakdown
        - **Topics Breakdown**: Specific concepts to cover
        - **Practice Exercises**: Hands-on activities
        - **Resources**: Recommended books, videos, websites
        - **Assessment**: Weekly checkpoints and tests
        - **Projects**: Mini-projects to apply knowledge
        
        Format in markdown with clear sections, emojis, and actionable items.
        Make it practical and achievable for a student.
        """
        
        return generate_custom_content(prompt)
        
    except Exception as e:
        logging.error(f"Study plan generation failed: {e}")
        return "🔴 Unable to generate study plan. Please try again later."

def predict_career(subject: str, skills: List[str], interests: List[str]) -> str:
    """Predict career paths using Gemini AI"""
    try:
        if not get_gemini_status():
            return "🔴 AI service unavailable. Cannot generate career prediction."
            
        prompt = f"""
        Suggest detailed career paths for an engineering student with this profile:
        
        - **Primary Subject**: {subject}
        - **Technical Skills**: {', '.join(skills) if skills else 'Basic programming'}
        - **Interests**: {', '.join(interests) if interests else 'Technology and innovation'}
        
        Provide comprehensive analysis including:
        
        1. **Career Options**: 3-5 specific job roles
        2. **Required Skills**: Technical and soft skills needed
        3. **Growth Opportunities**: Career progression paths
        4. **Salary Expectations**: Entry-level to senior ranges
        5. **Top Companies**: Recommended employers
        6. **Action Steps**: Concrete steps to prepare
        7. **Learning Resources**: Courses, certifications, projects
        
        Format in markdown with clear sections and practical advice.
        Be realistic and data-driven in your recommendations.
        """
        
        return generate_custom_content(prompt)
        
    except Exception as e:
        logging.error(f"Career prediction failed: {e}")
        return "🔴 Unable to generate career prediction. Please try again later."

def analyze_resume_with_ai(student_data: Dict[str, Any]) -> str:
    """Analyze resume and provide career suggestions"""
    try:
        if not get_gemini_status():
            return get_fallback_resume_analysis(student_data)
            
        prompt = f"""
        Conduct a comprehensive resume analysis and career guidance session for this engineering student:
        
        STUDENT PROFILE:
        {json.dumps(student_data, indent=2)}
        
        Provide detailed analysis in these sections:
        
        1. **Profile Summary**: Overall assessment
        2. **Key Strengths**: What stands out positively
        3. **Gap Analysis**: Missing skills or experiences
        4. **Career Recommendations**: Specific roles matching their profile
        5. **Skill Development**: Priority skills to acquire
        6. **Project Suggestions**: Portfolio enhancement ideas
        7. **Interview Preparation**: Areas to focus on
        8. **Timeline**: 3-6-12 month action plan
        
        Be constructive, specific, and actionable. Format in markdown with clear sections.
        """
        
        response = generate_custom_content(prompt)
        return response or get_fallback_resume_analysis(student_data)
        
    except Exception as e:
        logging.error(f"Resume analysis failed: {e}")
        return get_fallback_resume_analysis(student_data)

# Fallback functions
def get_fallback_questions() -> List[Dict[str, Any]]:
    """Provide fallback questions when Gemini fails"""
    return [
        {
            "question": "Which data structure follows LIFO (Last-In-First-Out) principle?",
            "options": ["A) Queue", "B) Stack", "C) Array", "D) Linked List"],
            "answer": "B",
            "explanation": "Stack follows LIFO principle where the last element added is the first one removed."
        },
        {
            "question": "What is the time complexity of binary search algorithm?",
            "options": ["A) O(n)", "B) O(log n)", "C) O(n²)", "D) O(1)"],
            "answer": "B",
            "explanation": "Binary search has O(log n) time complexity as it halves the search space each iteration."
        },
        {
            "question": "Which programming language is primarily used for machine learning and data science?",
            "options": ["A) Java", "B) Python", "C) C++", "D) HTML"],
            "answer": "B",
            "explanation": "Python is widely used in machine learning due to its extensive libraries like TensorFlow, PyTorch, and scikit-learn."
        },
        {
            "question": "What does SQL stand for in database management?",
            "options": ["A) Structured Query Language", "B) Simple Question Language", "C) System Query Logic", "D) Standard Question Format"],
            "answer": "A",
            "explanation": "SQL stands for Structured Query Language, used for managing and manipulating relational databases."
        },
        {
            "question": "Which protocol is used for secure web communication (HTTPS)?",
            "options": ["A) HTTP", "B) FTP", "C) HTTPS", "D) SMTP"],
            "answer": "C",
            "explanation": "HTTPS (HyperText Transfer Protocol Secure) encrypts communication between web browsers and servers."
        }
    ]

def get_fallback_feedback(subject: str, score: int, total: int, incorrect_questions: List[Dict]) -> str:
    """Provide fallback feedback when Gemini fails"""
    percentage = (score / total) * 100
    
    if percentage >= 80:
        return f"""
## 🎉 Outstanding Performance!

**Score:** {score}/{total} ({percentage:.1f}%) in {subject}

### 🌟 What You Did Well:
- Strong understanding of core concepts
- Excellent problem-solving skills
- Good time management

### 💡 Next Steps:
- Challenge yourself with advanced topics
- Consider mentoring other students
- Explore real-world applications

Keep up the excellent work! 🚀
"""
    elif percentage >= 60:
        return f"""
## 👍 Solid Performance!

**Score:** {score}/{total} ({percentage:.1f}%) in {subject}

### ✅ Strengths:
- Good grasp of fundamental concepts
- Reasonable problem-solving approach

### 📚 Areas to Improve:
- Review specific topics where you lost points
- Practice more application-based questions
- Work on time management

### 🎯 Action Plan:
1. Review incorrect questions
2. Practice similar problems
3. Focus on weak areas

You're on the right track! 💪
"""
    else:
        return f"""
## 💪 Learning Opportunity!

**Score:** {score}/{total} ({percentage:.1f}%) in {subject}

### 🔍 Focus Areas:
- Fundamental concepts need reinforcement
- Practice basic problem-solving
- Build stronger foundation

### 📖 Study Strategy:
1. Start with basic concepts
2. Practice regularly
3. Seek help when needed
4. Review and revise

### 🎯 Immediate Actions:
- Review course materials
- Practice with simple exercises
- Don't hesitate to ask questions

Every expert was once a beginner! Keep going! 🌟
"""

def get_fallback_resume_analysis(student_data: Dict[str, Any]) -> str:
    """Provide fallback resume analysis"""
    return f"""
## 📋 Basic Profile Analysis

### 📊 Current Status
- **Name**: {student_data.get('name', 'Not specified')}
- **Academic Year**: {student_data.get('year', 'Not specified')}
- **CGPA**: {student_data.get('cgpa', 'Not specified')}/10.0

### 🎯 Quick Assessment
- **Projects Completed**: {student_data.get('projects', 0)}
- **Internship Experience**: {student_data.get('internships', 0)}
- **Certifications**: {len(student_data.get('certifications', []))}
- **Communication Skills**: {student_data.get('communication', 'Not rated')}/10

### 💡 Recommended Actions

#### 🚀 Immediate (Next 2 weeks)
1. Complete all profile sections
2. Identify 2-3 target roles
3. Start basic skill certification

#### 📈 Short-term (1 month)
1. Build 1-2 technical projects
2. Practice communication skills
3. Network with professionals

#### 🎯 Medium-term (3 months)
1. Apply for internships
2. Complete advanced certifications
3. Prepare for interviews

### 🌟 Success Tips
- Focus on practical projects
- Document your learning journey
- Build a professional network
- Stay consistent with skill development

*Note: AI-powered resume analysis is currently unavailable. This is a general template to get you started.*
"""

# Test function
def test_gemini_connection():
    """Test if Gemini is working"""
    try:
        status = get_gemini_status()
        if status:
            model = get_best_model()
            if model:
                test_response = safe_generate_content(model, "Say only 'TEST_SUCCESS'")
                if test_response and "TEST_SUCCESS" in test_response.upper():
                    logging.info("✅ Gemini connection test passed!")
                    return True
        logging.warning("❌ Gemini connection test failed")
        return False
    except Exception as e:
        logging.error(f"Connection test failed: {e}")
        return False

# Initialize on module load
if __name__ == "__main__":
    print("🔍 Testing Gemini AI Integration...")
    print("=" * 50)
    
    if test_gemini_connection():
        print("✅ Gemini AI is ready to use!")
        
        # Test quiz generation
        print("\n🧪 Testing quiz generation...")
        quiz = generate_quiz_for_subject("Python Programming", 2)
        if quiz:
            print(f"✅ Generated {len(quiz)} quiz questions")
        else:
            print("❌ Quiz generation failed")
    else:
        print("❌ Gemini AI is not available")
        print("🔄 The app will use fallback content")