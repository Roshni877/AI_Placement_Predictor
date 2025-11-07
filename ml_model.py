import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_absolute_error, r2_score
import shap
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

class EmployabilityPredictor:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_names = [
            'cgpa', 'internships', 'projects', 'certification_count',
            'communication_skills', 'year_encoded', 'extracurricular_score'
        ]
        self.explainer = None
    
    def generate_synthetic_data(self, n_samples=1000):
        """Generate realistic synthetic student data"""
        np.random.seed(42)
        
        data = {
            'cgpa': np.random.normal(7.5, 1.2, n_samples).clip(5.0, 10.0),
            'internships': np.random.poisson(1.2, n_samples).clip(0, 5),
            'projects': np.random.poisson(3, n_samples).clip(0, 10),
            'certification_count': np.random.poisson(2, n_samples).clip(0, 8),
            'communication_skills': np.random.randint(4, 11, n_samples),
            'year': np.random.choice(['1st Year', '2nd Year', '3rd Year', '4th Year'], n_samples),
            'extracurricular_score': np.random.randint(0, 11, n_samples)
        }
        
        df = pd.DataFrame(data)
        
        # Create realistic employability score
        df['employability_score'] = (
            df['cgpa'] * 2.5 +
            df['internships'] * 8 +
            df['projects'] * 3 +
            df['certification_count'] * 4 +
            df['communication_skills'] * 3 +
            (df['year'].map({'1st Year': 2, '2nd Year': 4, '3rd Year': 7, '4th Year': 10})) +
            df['extracurricular_score'] * 2
        )
        
        # Normalize to 0-100 scale
        df['employability_score'] = (
            (df['employability_score'] - df['employability_score'].min()) / 
            (df['employability_score'].max() - df['employability_score'].min()) * 100
        )
        
        df['employability_score'] += np.random.normal(0, 5, n_samples)
        df['employability_score'] = df['employability_score'].clip(0, 100)
        
        return df
    
    def preprocess_data(self, df):
        """Preprocess the data for training"""
        df_processed = df.copy()
        
        # Encode categorical variables
        self.label_encoders['year'] = LabelEncoder()
        df_processed['year_encoded'] = self.label_encoders['year'].fit_transform(df_processed['year'])
        
        # Select features
        X = df_processed[self.feature_names]
        y = df_processed['employability_score']
        
        return X, y
    
    def train_model(self, n_samples=1000):
        """Train the Random Forest model with SHAP explainer"""
        st.info("🔄 Generating synthetic training data...")
        df = self.generate_synthetic_data(n_samples)
        
        st.info("🔄 Preprocessing data...")
        X, y = self.preprocess_data(df)
        
        st.info("🔄 Scaling features...")
        X_scaled = self.scaler.fit_transform(X)
        
        st.info("🔄 Training Random Forest model...")
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42
        )
        
        X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
        self.model.fit(X_train, y_train)
        
        # Create SHAP explainer
        st.info("🔄 Creating SHAP explainer...")
        self.explainer = shap.TreeExplainer(self.model)
        
        # Evaluate model
        y_pred = self.model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        st.success(f"✅ Model trained successfully! MAE: {mae:.2f}, R²: {r2:.2f}")
        
        return self.model, self.scaler, self.label_encoders
    
    def predict(self, student_data):
        """Predict employability for a single student"""
        if self.model is None:
            raise ValueError("Model not trained. Call train_model() first.")
        
        features = self.extract_features_from_student(student_data)
        features_scaled = self.scaler.transform([features])
        prediction = self.model.predict(features_scaled)[0]
        
        return max(0, min(100, prediction))
    
    def extract_features_from_student(self, student_data):
        """Extract features from student data dictionary"""
        # CGPA
        cgpa = float(student_data.get('cgpa', 6.5))
        
        # Internships
        internships = student_data.get('internships', 0)
        
        # Projects
        projects = student_data.get('projects', 0)
        
        # Certification count
        certifications = student_data.get('certifications', [])
        certification_count = len(certifications)
        
        # Communication skills
        communication_skills = student_data.get('communication', 6)
        
        # Year encoded
        year = student_data.get('year', '1st Year')
        if year in self.label_encoders['year'].classes_:
            year_encoded = self.label_encoders['year'].transform([year])[0]
        else:
            year_encoded = 0
        
        # Extracurricular score
        extracurricular_score = min(10, certification_count + internships)
        
        return [
            cgpa, internships, projects, certification_count,
            communication_skills, year_encoded, extracurricular_score
        ]
    
    def explain_prediction(self, student_data):
        """Generate SHAP explanation for prediction"""
        if self.model is None or self.explainer is None:
            return None
        
        try:
            features = self.extract_features_from_student(student_data)
            features_scaled = self.scaler.transform([features])
            
            # Get SHAP values
            shap_values = self.explainer.shap_values(features_scaled)
            
            # Create visualization
            feature_names_display = [
                'CGPA', 'Internships', 'Projects', 'Certifications',
                'Communication', 'Academic Year', 'Extracurricular'
            ]
            
            # Create bar chart for feature importance
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                y=feature_names_display,
                x=np.abs(shap_values[0]),
                orientation='h',
                marker_color='#667eea',
                text=[f"{val:.2f}" for val in np.abs(shap_values[0])],
                textposition='auto'
            ))
            
            fig.update_layout(
                title="SHAP Feature Impact on Prediction",
                xaxis_title="Impact on Employability Score",
                yaxis_title="Features",
                showlegend=False,
                height=400,
                margin=dict(l=50, r=50, t=50, b=50)
            )
            
            return fig
            
        except Exception as e:
            st.error(f"SHAP explanation failed: {e}")
            return None
    
    def generate_confidence_analysis(self, student_data):
        """Generate confidence analysis for the prediction"""
        prediction = self.predict(student_data)
        
        confidence_factors = {
            "Data Completeness": min(100, len([v for v in student_data.values() if v]) * 15),
            "Academic Performance": min(100, (student_data.get('cgpa', 0) / 10.0) * 100),
            "Practical Experience": min(100, (student_data.get('internships', 0) + student_data.get('projects', 0)) * 10),
            "Skill Diversity": min(100, len(student_data.get('certifications', [])) * 20)
        }
        
        overall_confidence = np.mean(list(confidence_factors.values()))
        
        return {
            "prediction": prediction,
            "confidence_score": overall_confidence,
            "confidence_factors": confidence_factors
        }
    
    def save_model(self, filepath='employability_model.joblib'):
        """Save trained model and preprocessors"""
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'label_encoders': self.label_encoders,
            'feature_names': self.feature_names,
            'explainer': self.explainer
        }
        joblib.dump(model_data, filepath)
        st.success(f"✅ Model saved to {filepath}")
    
    def load_model(self, filepath='employability_model.joblib'):
        """Load trained model and preprocessors"""
        try:
            model_data = joblib.load(filepath)
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.label_encoders = model_data['label_encoders']
            self.feature_names = model_data['feature_names']
            self.explainer = model_data.get('explainer')
            st.success(f"✅ Model loaded from {filepath}")
            return True
        except:
            st.warning("❌ Failed to load model, will train new one")
            return False

# Global model instance
_predictor = None

def get_predictor():
    global _predictor
    if _predictor is None:
        _predictor = EmployabilityPredictor()
        # Try to load existing model, else train new one
        if not _predictor.load_model():
            st.info("🔄 Training new model...")
            _predictor.train_model(800)
            _predictor.save_model()
    return _predictor

def predict_employability(student_data):
    """Main function to predict employability"""
    predictor = get_predictor()
    return predictor.predict(student_data)

def explain_employability(student_data):
    """Explain the employability prediction using SHAP"""
    predictor = get_predictor()
    return predictor.explain_prediction(student_data)

def get_confidence_analysis(student_data):
    """Get confidence analysis for prediction"""
    predictor = get_predictor()
    return predictor.generate_confidence_analysis(student_data)

if __name__ == "__main__":
    # Test the model
    predictor = get_predictor()
    
    # Test prediction
    test_student = {
        'cgpa': 8.5,
        'internships': 2,
        'projects': 5,
        'certifications': ['Python', 'Machine Learning', 'SQL'],
        'communication': 8,
        'year': '3rd Year'
    }
    
    score = predict_employability(test_student)
    print(f"🎯 Predicted Employability Score: {score:.1f}%")