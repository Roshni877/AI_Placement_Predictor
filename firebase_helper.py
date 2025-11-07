# firebase_helper.py
import os
import logging
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore, auth, storage

# ---------------------------------------------------------------------
# 📂 Setup paths and constants
# ---------------------------------------------------------------------
UPLOADS_DIR = "uploads"
if not os.path.exists(UPLOADS_DIR):
    os.makedirs(UPLOADS_DIR)

_db = None

# ---------------------------------------------------------------------
# ⚙️ Initialize Firebase
# ---------------------------------------------------------------------
def setup_firebase():
    """
    Initializes Firebase Admin SDK using the local serviceAccountKey.json file.
    Automatically called at import.
    """
    global _db

    if _db is not None:
        return _db  # already initialized

    try:
        # ✅ Correct local path handling
        service_path = os.path.join(os.path.dirname(__file__), "serviceAccountKey.json")

        if not os.path.exists(service_path):
            logging.error(f"❌ Firebase service account file not found at: {service_path}")
            return None

        # Initialize app only once
        if not firebase_admin._apps:
            cred = credentials.Certificate(service_path)
            firebase_admin.initialize_app(cred)
            logging.info("✅ Firebase initialized successfully.")

        _db = firestore.client()
        return _db

    except Exception as e:
        logging.exception(f"Firebase setup failed: {e}")
        return None

# Auto-initialize on import
setup_firebase()

# ---------------------------------------------------------------------
# 👤 Student Management
# ---------------------------------------------------------------------
def create_student(email: str, password: str, name: str, year: str) -> bool:
    """Create new student with year and subjects"""
    if _db is None:
        setup_firebase()
        if _db is None:
            logging.error("Firebase not initialized.")
            return False

    try:
        display_name = name.strip() if name.strip() else "Student User"
        user = auth.create_user(email=email, password=password, display_name=display_name)

        # Define subjects based on year
        year_subjects = {
            "1st Year": ["Python for Beginners", "C Programming", "Electronics Basics", "Electrical Engg", "Nanotech", "Intro to DSA", "Simple Java"],
            "2nd Year": ["Operating System", "DSA", "Java OOPs", "AI", "ADA", "DBMS", "MongoDB"],
            "3rd Year": ["SEPM", "EDA", "Python Advanced", "Java Complex", "Computer Networks"],
            "4th Year": ["Blockchain", "Cybersecurity", "Data Privacy", "Data Visualization", "DBMS"]
        }

        subjects = year_subjects.get(year, [])
        data = {
            "email": email,
            "name": display_name,
            "year": year,
            "subjects": subjects,
            "role": "Student",
            "created_at": datetime.utcnow().isoformat()
        }
        _db.collection("students").document(email).set(data)
        logging.info(f"✅ Student {email} registered successfully.")
        return True

    except Exception as e:
        logging.exception(f"create_student failed: {e}")
        return False

def save_student_data(email: str, data: dict) -> bool:
    """Update or create student profile"""
    try:
        if _db is None:
            setup_firebase()
        _db.collection("students").document(email).set(data, merge=True)
        return True
    except Exception as e:
        logging.exception(f"save_student_data failed: {e}")
        return False

def fetch_all_students():
    """Fetch all students"""
    try:
        if _db is None:
            setup_firebase()
        docs = _db.collection("students").stream()
        return [d.to_dict() for d in docs]
    except Exception as e:
        logging.exception(f"fetch_all_students failed: {e}")
        return []

def get_student(email: str):
    """Fetch a single student's data"""
    try:
        if _db is None:
            setup_firebase()
        doc = _db.collection("students").document(email).get()
        return doc.to_dict() if doc.exists else None
    except Exception as e:
        logging.exception(f"get_student failed: {e}")
        return None

# ---------------------------------------------------------------------
# 📁 Resume Upload
# ---------------------------------------------------------------------
def upload_resume(file, filename: str) -> str:
    """Save resume locally and upload to Firebase Storage (if available)"""
    try:
        path = os.path.join(UPLOADS_DIR, filename)
        with open(path, "wb") as f:
            f.write(file.getbuffer())

        if firebase_admin._apps:
            bucket = storage.bucket()
            blob = bucket.blob(f"resumes/{filename}")
            blob.upload_from_filename(path)
            blob.make_public()
            return blob.public_url

        return path
    except Exception as e:
        logging.exception(f"upload_resume failed: {e}")
        return ""

# ---------------------------------------------------------------------
# 🧠 Quiz Management
# ---------------------------------------------------------------------
def save_quiz_question(question_doc: dict) -> bool:
    """Save generated quiz question"""
    try:
        if _db is None:
            setup_firebase()
        import uuid
        qid = uuid.uuid4().hex
        _db.collection("quiz_questions").document(qid).set(question_doc)
        return True
    except Exception as e:
        logging.exception(f"save_quiz_question failed: {e}")
        return False

def save_quiz_result(email: str, subject: str, score: int, total: int, details: dict) -> bool:
    """Save quiz result with enhanced metadata"""
    try:
        if _db is None:
            setup_firebase()
        
        payload = {
            "email": email,
            "subject": subject,
            "score": score,
            "total": total,
            "percentage": (score / total) * 100,
            "details": details,
            "timestamp": datetime.utcnow().isoformat(),
            "date": datetime.utcnow().strftime("%Y-%m-%d"),
            "week": datetime.utcnow().strftime("%Y-W%U"),
            "month": datetime.utcnow().strftime("%Y-%m")
        }
        
        _db.collection("quiz_results").add(payload)
        logging.info(f"✅ Quiz result saved for {email}: {score}/{total} in {subject}")
        return True
    except Exception as e:
        logging.exception(f"save_quiz_result failed: {e}")
        return False

def fetch_student_quiz_results(email: str):
    """Fetch quiz results for a specific student"""
    try:
        if _db is None:
            setup_firebase()
        
        docs = _db.collection("quiz_results").where("email", "==", email).stream()
        results = [d.to_dict() for d in docs]
        results.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return results
    except Exception as e:
        logging.exception(f"fetch_student_quiz_results failed: {e}")
        return []

def fetch_quiz_results():
    """Fetch all quiz results"""
    try:
        if _db is None:
            setup_firebase()
        docs = _db.collection("quiz_results").stream()
        return [d.to_dict() for d in docs]
    except Exception as e:
        logging.exception(f"fetch_quiz_results failed: {e}")
        return []

# ---------------------------------------------------------------------
# 🧾 Register & Login
# ---------------------------------------------------------------------
def register_user(email: str, password: str, role: str, name: str = "", year: str = ""):
    """Register a new user (Student or Officer)"""
    try:
        if _db is None:
            setup_firebase()

        if role.lower() == "student":
            ok = create_student(email, password, name, year)
            return (True, f"✅ Student {email} registered successfully.") if ok else (False, "❌ Failed to register student.")

        elif role.lower() in ["placement officer", "officer", "admin"]:
            display_name = name.strip() if name.strip() else "Placement Officer"
            user = auth.create_user(email=email, password=password, display_name=display_name)

            data = {
                "email": email,
                "name": display_name,
                "role": "Placement Officer",
                "created_at": datetime.utcnow().isoformat()
            }
            _db.collection("placement_officers").document(email).set(data)
            return True, "✅ Placement Officer registered successfully."

        else:
            return False, "❌ Invalid role specified."

    except Exception as e:
        logging.exception(f"register_user failed: {e}")
        return False, f"❌ Registration failed: {e}"

def login_user(email: str):
    """Login user (Student or Placement Officer)"""
    try:
        if _db is None:
            setup_firebase()

        student_ref = _db.collection("students").document(email).get()
        if student_ref.exists:
            data = student_ref.to_dict()
            data["role"] = "Student"
            return data

        officer_ref = _db.collection("placement_officers").document(email).get()
        if officer_ref.exists:
            data = officer_ref.to_dict()
            data["role"] = "Placement Officer"
            return data

        return None
    except Exception as e:
        logging.exception(f"login_user failed: {e}")
        return None