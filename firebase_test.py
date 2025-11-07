# firebase_test.py
import firebase_admin
from firebase_admin import credentials, firestore

def test_firebase():
    try:
        # Initialize Firebase
        cred = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(cred)
        
        # Connect to Firestore
        db = firestore.client()
        
        print("✅ Connected to Firebase successfully!")
        
        # Test collections
        collections = db.collections()
        collection_names = [c.id for c in collections]
        print("📁 Available collections:", collection_names)
        
        return True
        
    except Exception as e:
        print(f"❌ Firebase connection failed: {e}")
        return False

if __name__ == "__main__":
    test_firebase()