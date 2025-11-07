# ui_helpers.py
import requests
import streamlit as st

def lottie_from_url(url: str):
    """
    Returns parsed JSON for a lottie animation or None.
    """
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.warning(f"Couldn't load animation: {e}")
        return None

def load_css():
    """Load enhanced CSS styles with dark/light mode"""
    st.markdown("""
    <style>
    /* Base Styles */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif;
        transition: all 0.3s ease;
    }
    
    /* Dark Mode */
    .main {
        background: linear-gradient(135deg, #0c0c0c 0%, #1a1a2e 50%, #16213e 100%);
    }
    
    .dark-mode {
        background: linear-gradient(135deg, #0c0c0c 0%, #1a1a2e 50%, #16213e 100%);
        color: #ffffff;
    }
    
    .dark-mode .card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    .dark-mode .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem;
        border-radius: 20px;
        color: white;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .dark-mode .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
    }
    
    /* Light Mode */
    .light-mode {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: #333333;
    }
    
    .light-mode .card {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    .light-mode .main-header {
        background: rgba(255, 255, 255, 0.95);
        padding: 3rem;
        border-radius: 20px;
        color: #333;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.5);
    }
    
    .light-mode .metric-card {
        background: linear-gradient(135deg, #51cf66 0%, #2f9e44 100%);
        color: white;
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 8px 25px rgba(81, 207, 102, 0.3);
    }
    
    /* Common Components */
    .card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem;
        border-radius: 20px;
        color: white;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .sidebar-header {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 1rem;
    }
    
    .auth-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 2rem;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .quiz-question {
        background: rgba(255, 255, 255, 0.05);
        border-left: 4px solid #667eea;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .success-box {
        background: linear-gradient(135deg, #51cf66 0%, #2f9e44 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        text-align: center;
    }
    
    .warning-box {
        background: linear-gradient(135deg, #ffd43b 0%, #f08c00 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        text-align: center;
    }
    
    .info-box {
        background: linear-gradient(135deg, #339af0 0%, #1c7ed6 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        text-align: center;
    }
    
    /* Progress Bar */
    .progress-container {
        width: 100%;
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .progress-bar {
        height: 30px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        text-align: center;
        line-height: 30px;
        color: white;
        font-weight: bold;
        transition: width 0.5s ease-in-out;
    }
    
    /* Buttons */
    .stButton>button {
        border-radius: 15px;
        height: 3em;
        width: 100%;
        border: none;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    
    /* Input Fields */
    .stTextInput>div>div>input {
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        background: rgba(255, 255, 255, 0.1);
        color: white;
    }
    
    .stSelectbox>div>div>select {
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        background: rgba(255, 255, 255, 0.1);
        color: white;
    }
    
    /* Neon Animations */
    @keyframes neon-glow {
        0%, 100% { 
            box-shadow: 0 0 5px #667eea, 0 0 10px #667eea, 0 0 15px #667eea; 
        }
        50% { 
            box-shadow: 0 0 10px #764ba2, 0 0 20px #764ba2, 0 0 30px #764ba2; 
        }
    }
    
    .neon-card {
        animation: neon-glow 2s ease-in-out infinite alternate;
    }
    
    /* Green Animation for Light Mode */
    @keyframes green-glow {
        0%, 100% { 
            box-shadow: 0 0 5px #51cf66, 0 0 10px #51cf66; 
        }
        50% { 
            box-shadow: 0 0 10px #2f9e44, 0 0 20px #2f9e44; 
        }
    }
    
    .green-glow {
        animation: green-glow 2s ease-in-out infinite alternate;
    }
    
    /* Modal Styles */
    .modal-backdrop {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.7);
        backdrop-filter: blur(5px);
        z-index: 999;
        display: flex;
        justify-content: center;
        align-items: center;
    }

    .modal-content {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 20px;
        padding: 2rem;
        max-width: 90%;
        max-height: 90%;
        overflow-y: auto;
        border: 2px solid #667eea;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
    }

    .modal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.5rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.2);
        padding-bottom: 1rem;
    }

    .modal-close {
        background: #ff6b6b;
        border: none;
        color: white;
        border-radius: 50%;
        width: 30px;
        height: 30px;
        cursor: pointer;
        font-weight: bold;
    }

    .analysis-section {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }

    .skill-meter {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 0.5rem;
        margin: 0.5rem 0;
    }

    .skill-fill {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        height: 10px;
        border-radius: 5px;
        transition: width 0.5s ease;
    }
    
    /* Power BI Style Cards */
    .powerbi-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    
    .powerbi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    }
    
    .powerbi-metric {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        color: white;
        margin: 0.5rem;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    /* Analytics Grid */
    .analytics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    
    /* Trend Indicators */
    .trend-up {
        color: #51cf66;
        font-weight: bold;
    }
    
    .trend-down {
        color: #ff6b6b;
        font-weight: bold;
    }
    
    /* KPI Cards */
    .kpi-card {
        background: rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        border-left: 4px solid #667eea;
    }
    
    .kpi-value {
        font-size: 2rem;
        font-weight: bold;
        color: #667eea;
        margin: 0.5rem 0;
    }
    
    .kpi-label {
        font-size: 0.9rem;
        color: rgba(255, 255, 255, 0.7);
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Scrollbar Styling */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .card {
            padding: 1rem;
            margin: 0.5rem 0;
        }
        
        .main-header {
            padding: 1.5rem;
        }
        
        .analytics-grid {
            grid-template-columns: 1fr;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def load_enhanced_css():
    """Load enhanced CSS with Power BI styling"""
    st.markdown("""
    <style>
    /* Power BI Style Enhancements */
    .powerbi-dashboard {
        background: rgba(255, 255, 255, 0.02);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
    }
    
    .powerbi-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.5rem;
        margin: 1.5rem 0;
    }
    
    .powerbi-widget {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: all 0.3s ease;
    }
    
    .powerbi-widget:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.25);
        border-color: rgba(102, 126, 234, 0.5);
    }
    
    .powerbi-chart-container {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    
    .powerbi-tooltip {
        background: rgba(26, 26, 46, 0.95);
        border: 1px solid #667eea;
        border-radius: 8px;
        padding: 0.75rem;
        color: white;
        font-size: 0.85rem;
        backdrop-filter: blur(10px);
    }
    
    /* Data Visualization Colors */
    .color-primary { color: #667eea; }
    .color-secondary { color: #764ba2; }
    .color-success { color: #51cf66; }
    .color-warning { color: #ffd43b; }
    .color-danger { color: #ff6b6b; }
    .color-info { color: #339af0; }
    
    /* Gradient Backgrounds */
    .gradient-primary {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .gradient-success {
        background: linear-gradient(135deg, #51cf66 0%, #2f9e44 100%);
    }
    
    .gradient-warning {
        background: linear-gradient(135deg, #ffd43b 0%, #f08c00 100%);
    }
    
    .gradient-danger {
        background: linear-gradient(135deg, #ff6b6b 0%, #fa5252 100%);
    }
    
    /* Loading Animations */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .loading-pulse {
        animation: pulse 2s ease-in-out infinite;
    }
    
    /* Focus States */
    .stButton>button:focus,
    .stTextInput>div>div>input:focus,
    .stSelectbox>div>div>select:focus {
        outline: 2px solid #667eea;
        outline-offset: 2px;
    }
    
    /* Custom Badges */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .badge-success {
        background: rgba(81, 207, 102, 0.2);
        color: #51cf66;
        border: 1px solid rgba(81, 207, 102, 0.3);
    }
    
    .badge-warning {
        background: rgba(255, 212, 59, 0.2);
        color: #ffd43b;
        border: 1px solid rgba(255, 212, 59, 0.3);
    }
    
    .badge-danger {
        background: rgba(255, 107, 107, 0.2);
        color: #ff6b6b;
        border: 1px solid rgba(255, 107, 107, 0.3);
    }
    
    .badge-info {
        background: rgba(51, 154, 240, 0.2);
        color: #339af0;
        border: 1px solid rgba(51, 154, 240, 0.3);
    }
    
    /* Status Indicators */
    .status-indicator {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-right: 0.5rem;
    }
    
    .status-online { background: #51cf66; }
    .status-offline { background: #ff6b6b; }
    .status-pending { background: #ffd43b; }
    .status-processing { background: #339af0; }
    
    /* Progress Indicators */
    .circular-progress {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: conic-gradient(#667eea var(--progress), rgba(255, 255, 255, 0.1) 0deg);
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
    }
    
    .circular-progress::before {
        content: attr(data-progress) '%';
        position: absolute;
        color: white;
        font-weight: bold;
        font-size: 0.8rem;
    }
    
    /* Hover Effects */
    .hover-lift {
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .hover-lift:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    }
    
    /* Glass Morphism */
    .glass-effect {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 15px;
    }
    
    /* Text Utilities */
    .text-gradient {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .text-truncate {
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    
    /* Spacing Utilities */
    .m-0 { margin: 0; }
    .m-1 { margin: 0.5rem; }
    .m-2 { margin: 1rem; }
    .m-3 { margin: 1.5rem; }
    .m-4 { margin: 2rem; }
    
    .p-0 { padding: 0; }
    .p-1 { padding: 0.5rem; }
    .p-2 { padding: 1rem; }
    .p-3 { padding: 1.5rem; }
    .p-4 { padding: 2rem; }
    </style>
    """, unsafe_allow_html=True)

def toggle_dark_mode():
    """Toggle between dark and light mode"""
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = True
    
    return st.session_state.dark_mode

def apply_theme():
    """Apply the current theme to the app"""
    if st.session_state.get('dark_mode', True):
        st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(135deg, #0c0c0c 0%, #1a1a2e 50%, #16213e 100%);
            color: #ffffff;
        }
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333333;
        }
        </style>
        """, unsafe_allow_html=True)

def create_metric_card(title, value, delta=None, delta_color="normal"):
    """Create a beautiful metric card"""
    if delta is not None:
        return f"""
        <div class="metric-card hover-lift">
            <div class="kpi-label">{title}</div>
            <div class="kpi-value">{value}</div>
            <div class="{'trend-up' if delta_color == 'positive' else 'trend-down' if delta_color == 'negative' else ''}">
                {delta}
            </div>
        </div>
        """
    else:
        return f"""
        <div class="metric-card hover-lift">
            <div class="kpi-label">{title}</div>
            <div class="kpi-value">{value}</div>
        </div>
        """

def create_progress_bar(percentage, label=None):
    """Create a custom progress bar"""
    progress_html = f"""
    <div class="progress-container">
        <div class="progress-bar" style="width: {percentage}%">
            <span class="progress-text">{percentage}%</span>
        </div>
    </div>
    """
    if label:
        progress_html = f"""
        <div>
            <div style="display: flex; justify-content: between; margin-bottom: 0.5rem;">
                <span>{label}</span>
                <span>{percentage}%</span>
            </div>
            {progress_html}
        </div>
        """
    return progress_html

def create_badge(text, type="info"):
    """Create a styled badge"""
    type_class = {
        "success": "badge-success",
        "warning": "badge-warning", 
        "danger": "badge-danger",
        "info": "badge-info"
    }.get(type, "badge-info")
    
    return f'<span class="badge {type_class}">{text}</span>'

def create_status_indicator(status):
    """Create a status indicator"""
    status_class = {
        "online": "status-online",
        "offline": "status-offline",
        "pending": "status-pending",
        "processing": "status-processing"
    }.get(status, "status-offline")
    
    return f'<span class="status-indicator {status_class}"></span>'