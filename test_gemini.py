# test_gemini.py
import ai_utils as ai

def test_all_functions():
    print("🔍 Testing Gemini AI Connection...")
    print("=" * 50)
    
    # Test connection
    connection_ok = ai.test_gemini_connection()
    print(f"🔗 Connection Test: {'✅ SUCCESS' if connection_ok else '❌ FAILED'}")
    
    if connection_ok:
        # Test quiz generation
        print("\n🧪 Testing Quiz Generation...")
        quiz = ai.generate_quiz_for_subject("Python", 2)
        print(f"📝 Quiz Test: {'✅ SUCCESS' if quiz and len(quiz) > 0 else '❌ FAILED'}")
        if quiz:
            print(f"   Generated {len(quiz)} questions")
        
        # Test feedback
        print("\n💬 Testing Feedback Generation...")
        feedback = ai.generate_feedback("Python", 3, 5, [])
        print(f"📊 Feedback Test: {'✅ SUCCESS' if feedback else '❌ FAILED'}")
        
        # Test study plan
        print("\n📚 Testing Study Plan Generation...")
        study_plan = ai.generate_study_plan("Mathematics", "Beginner", 7, 2)
        print(f"🎯 Study Plan Test: {'✅ SUCCESS' if study_plan else '❌ FAILED'}")
    
    print("\n" + "=" * 50)
    print(f"Overall Status: {'✅ ALL TESTS PASSED' if connection_ok else '❌ CONNECTION FAILED'}")
    
    return connection_ok

if __name__ == "__main__":
    test_all_functions()