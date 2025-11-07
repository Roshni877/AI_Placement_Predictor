import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np

class PowerBIAnalytics:
    def __init__(self):
        self.color_palette = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4ecdc4', '#45b7d1']
    
    def create_employability_dashboard(self, student_data, quiz_results):
        """Create Power BI style employability dashboard with proper bounds"""
        st.markdown("""
        <style>
        .powerbi-container {
            background: rgba(255, 255, 255, 0.02);
            border-radius: 15px;
            padding: 1.5rem;
            margin: 1rem 0;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Overall Metrics Row
        st.markdown('<div class="powerbi-container">', unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            employability_score = self.calculate_employability_score(student_data)
            st.metric("🎯 Employability Score", f"{employability_score}%")
        
        with col2:
            avg_quiz_score = self.calculate_avg_quiz_score(quiz_results)
            st.metric("📊 Quiz Average", f"{avg_quiz_score}%")
        
        with col3:
            skill_gap = self.calculate_skill_gap(student_data, quiz_results)
            st.metric("📚 Skill Gap", f"{skill_gap}%")
        
        with col4:
            improvement = self.calculate_improvement_rate(quiz_results)
            st.metric("📈 Improvement Rate", f"{improvement}%")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Charts Row 1
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="powerbi-container">', unsafe_allow_html=True)
            self.create_skill_radar_chart(student_data)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="powerbi-container">', unsafe_allow_html=True)
            self.create_performance_trend_chart(quiz_results)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Charts Row 2
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="powerbi-container">', unsafe_allow_html=True)
            self.create_subject_breakdown_chart(quiz_results)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="powerbi-container">', unsafe_allow_html=True)
            self.create_employability_breakdown(student_data)
            st.markdown('</div>', unsafe_allow_html=True)
    
    def calculate_employability_score(self, student_data):
        """Calculate comprehensive employability score"""
        if not student_data:
            return 0
        
        score = 0
        score += min(25, (student_data.get('cgpa', 0) / 10.0) * 25)
        score += min(20, student_data.get('internships', 0) * 5)
        score += min(15, student_data.get('projects', 0) * 3)
        score += min(15, len(student_data.get('certifications', [])) * 3)
        score += min(10, student_data.get('communication', 0))
        score += min(15, {'1st Year': 5, '2nd Year': 8, '3rd Year': 12, '4th Year': 15}.get(student_data.get('year', '1st Year'), 5))
        
        return min(100, int(score))
    
    def calculate_avg_quiz_score(self, quiz_results):
        """Calculate average quiz score"""
        if not quiz_results:
            return 0
        
        total_percentage = sum((r.get('score', 0) / r.get('total', 1)) * 100 for r in quiz_results)
        return round(total_percentage / len(quiz_results), 1)
    
    def calculate_skill_gap(self, student_data, quiz_results):
        """Calculate skill gap based on quiz performance"""
        target_score = 80
        current_score = self.calculate_employability_score(student_data)
        return max(0, target_score - current_score)
    
    def calculate_improvement_rate(self, quiz_results):
        """Calculate improvement rate over time"""
        if len(quiz_results) < 2:
            return 0
        
        try:
            # Sort by timestamp and calculate improvement
            sorted_results = sorted(quiz_results, key=lambda x: x.get('timestamp', ''))
            if len(sorted_results) >= 2:
                recent_avg = np.mean([(r['score']/r['total'])*100 for r in sorted_results[-3:]])
                older_avg = np.mean([(r['score']/r['total'])*100 for r in sorted_results[:3]])
                return round(recent_avg - older_avg, 1)
        except:
            pass
        return 0
    
    def create_skill_radar_chart(self, student_data):
        """Create radar chart for skills assessment with proper bounds and tooltips"""
        categories = ['Academic', 'Technical', 'Experience', 'Communication', 'Projects']
        
        values = [
            min(100, (student_data.get('cgpa', 0) / 10.0) * 100),
            min(100, len(student_data.get('certifications', [])) * 20),
            min(100, student_data.get('internships', 0) * 25),
            min(100, student_data.get('communication', 0) * 10),
            min(100, student_data.get('projects', 0) * 20)
        ]
        
        # Create detailed hover text
        hover_text = []
        for i, (category, value) in enumerate(zip(categories, values)):
            details = ""
            if category == 'Academic':
                details = f"CGPA: {student_data.get('cgpa', 0)}"
            elif category == 'Technical':
                details = f"Certifications: {len(student_data.get('certifications', []))}"
            elif category == 'Experience':
                details = f"Internships: {student_data.get('internships', 0)}"
            elif category == 'Communication':
                details = f"Rating: {student_data.get('communication', 0)}/10"
            elif category == 'Projects':
                details = f"Projects: {student_data.get('projects', 0)}"
            
            hover_text.append(f"<b>{category}</b><br>Score: {value:.1f}%<br>{details}")
        
        # Add first point at the end to close the radar
        hover_text.append(hover_text[0])
        values_with_closure = values + [values[0]]
        categories_with_closure = categories + [categories[0]]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values_with_closure,
            theta=categories_with_closure,
            fill='toself',
            fillcolor='rgba(102, 126, 234, 0.3)',
            line=dict(color='#667eea', width=2),
            name='Current Skills',
            hoverinfo='text',
            hovertext=hover_text,
            hovertemplate='%{hovertext}<extra></extra>'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    tickvals=[0, 25, 50, 75, 100],
                    ticktext=['0', '25', '50', '75', '100'],
                    tickangle=0
                ),
                angularaxis=dict(
                    rotation=90,
                    direction="clockwise"
                )
            ),
            showlegend=False,
            title="Skills Radar Chart",
            height=400,
            margin=dict(l=50, r=50, t=50, b=50),
            hoverlabel=dict(
                bgcolor="white",
                font_size=12,
                font_family="Arial",
                bordercolor="black"
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def create_performance_trend_chart(self, quiz_results):
        """Create performance trend chart with proper bounds and enhanced tooltips"""
        if not quiz_results:
            st.info("No quiz data available for trend analysis")
            return
        
        try:
            # Create DataFrame and ensure proper formatting
            df = pd.DataFrame(quiz_results)
            
            # Handle timestamp conversion safely
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
                df = df.dropna(subset=['timestamp'])
            
            if len(df) == 0:
                st.info("No valid timestamp data available")
                return
                
            df['percentage'] = (df['score'] / df['total']) * 100
            df = df.sort_values('timestamp')
            
            # Create detailed hover text
            df['hover_text'] = df.apply(
                lambda row: f"<b>Date:</b> {row['timestamp'].strftime('%Y-%m-%d')}<br>"
                           f"<b>Subject:</b> {row.get('subject', 'N/A')}<br>"
                           f"<b>Score:</b> {row['score']}/{row['total']}<br>"
                           f"<b>Percentage:</b> {row['percentage']:.1f}%",
                axis=1
            )
            
            fig = px.line(df, x='timestamp', y='percentage',
                         title="Performance Trend Over Time",
                         markers=True)
            
            fig.update_traces(
                line=dict(color='#667eea', width=4),
                marker=dict(size=8, color='#764ba2'),
                hovertemplate='%{customdata}<extra></extra>',
                customdata=df['hover_text']
            )
            
            # Add trend line if enough data points
            if len(df) > 1:
                x_numeric = np.arange(len(df))
                y_values = df['percentage'].values
                z = np.polyfit(x_numeric, y_values, 1)
                trend_line = np.poly1d(z)(x_numeric)
                
                fig.add_trace(go.Scatter(
                    x=df['timestamp'],
                    y=trend_line,
                    mode='lines',
                    line=dict(dash='dash', color='#ff6b6b', width=2),
                    name='Trend Line',
                    hovertemplate='Trend: %{y:.1f}%<extra></extra>'
                ))
            
            fig.update_layout(
                height=400,
                xaxis_title="Date",
                yaxis_title="Score (%)",
                yaxis_range=[0, 100],
                margin=dict(l=50, r=50, t=50, b=50),
                showlegend=len(df) > 1,
                hovermode='x unified',
                hoverlabel=dict(
                    bgcolor="white",
                    font_size=12,
                    font_family="Arial",
                    bordercolor="black"
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.info("Could not generate trend chart")
    
    def create_subject_breakdown_chart(self, quiz_results):
        """Create subject-wise performance breakdown with enhanced tooltips"""
        if not quiz_results:
            st.info("No quiz data available for subject analysis")
            return
        
        try:
            df = pd.DataFrame(quiz_results)
            
            # Calculate average scores per subject
            subject_stats = []
            for subject in df['subject'].unique():
                subject_data = df[df['subject'] == subject]
                total_quizzes = len(subject_data)
                avg_score = (subject_data['score'].sum() / subject_data['total'].sum()) * 100
                best_score = (subject_data['score'].max() / subject_data['total'].max()) * 100
                
                subject_stats.append({
                    'subject': subject,
                    'average_score': round(avg_score, 1),
                    'quiz_count': total_quizzes,
                    'best_score': round(best_score, 1),
                    'hover_text': f"<b>Subject:</b> {subject}<br>"
                                 f"<b>Average Score:</b> {round(avg_score, 1)}%<br>"
                                 f"<b>Best Score:</b> {round(best_score, 1)}%<br>"
                                 f"<b>Quizzes Taken:</b> {total_quizzes}"
                })
            
            subject_df = pd.DataFrame(subject_stats)
            
            if len(subject_df) > 0:
                fig = px.bar(subject_df, x='subject', y='average_score',
                            color='average_score',
                            color_continuous_scale='Viridis',
                            title="Performance by Subject",
                            text='average_score')
                
                fig.update_traces(
                    texttemplate='%{text}%',
                    textposition='outside',
                    hovertemplate='%{customdata}<extra></extra>',
                    customdata=subject_df['hover_text']
                )
                
                fig.update_layout(
                    height=400,
                    xaxis_title="Subject",
                    yaxis_title="Average Score (%)",
                    yaxis_range=[0, 100],
                    margin=dict(l=50, r=50, t=50, b=50),
                    showlegend=False,
                    hoverlabel=dict(
                        bgcolor="white",
                        font_size=12,
                        font_family="Arial",
                        bordercolor="black"
                    )
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No subject data available")
                
        except Exception as e:
            st.info("Could not generate subject breakdown")
    
    def create_employability_breakdown(self, student_data):
        """Create employability factor breakdown with enhanced tooltips"""
        if not student_data:
            st.info("No student data available")
            return
        
        factors = ['CGPA', 'Internships', 'Projects', 'Certifications', 'Communication', 'Year']
        values = [
            (student_data.get('cgpa', 0) / 10.0) * 25,
            min(20, student_data.get('internships', 0) * 5),
            min(15, student_data.get('projects', 0) * 3),
            min(15, len(student_data.get('certifications', [])) * 3),
            min(10, student_data.get('communication', 0)),
            {'1st Year': 5, '2nd Year': 8, '3rd Year': 12, '4th Year': 15}.get(student_data.get('year', '1st Year'), 5)
        ]
        
        max_values = [25, 20, 15, 15, 10, 15]
        percentages = [(v/max_v)*100 for v, max_v in zip(values, max_values)]
        
        # Create detailed hover text
        hover_texts = []
        details_map = {
            'CGPA': f"Current CGPA: {student_data.get('cgpa', 0)}",
            'Internships': f"Internships Completed: {student_data.get('internships', 0)}",
            'Projects': f"Projects Done: {student_data.get('projects', 0)}",
            'Certifications': f"Certifications: {len(student_data.get('certifications', []))}",
            'Communication': f"Communication Rating: {student_data.get('communication', 0)}/10",
            'Year': f"Academic Year: {student_data.get('year', '1st Year')}"
        }
        
        for factor, percentage, value, max_val in zip(factors, percentages, values, max_values):
            hover_texts.append(
                f"<b>{factor}</b><br>"
                f"Score: {value:.1f}/{max_val}<br>"
                f"Contribution: {percentage:.1f}%<br>"
                f"{details_map[factor]}"
            )
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            y=factors,
            x=percentages,
            orientation='h',
            marker_color='#4ecdc4',
            text=[f"{v:.1f}%" for v in percentages],
            textposition='outside',
            hovertemplate='%{customdata}<extra></extra>',
            customdata=hover_texts
        ))
        
        fig.update_layout(
            title="Employability Factors Breakdown",
            xaxis_title="Contribution (%)",
            xaxis_range=[0, 100],
            height=400,
            margin=dict(l=50, r=50, t=50, b=50),
            showlegend=False,
            hoverlabel=dict(
                bgcolor="white",
                font_size=12,
                font_family="Arial",
                bordercolor="black"
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)

# Global instance
powerbi_analytics = PowerBIAnalytics()