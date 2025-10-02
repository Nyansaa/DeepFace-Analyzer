import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from deepface import DeepFace
import tempfile
import os
from PIL import Image
import numpy as np
import cv2
import time
from datetime import datetime
import json
import base64
from io import BytesIO

# Page configuration
st.set_page_config(
    page_title="DeepFace Analyzer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling with animations
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global styles */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Animated header */
    .main-header {
        font-family: 'Inter', sans-serif;
        font-size: 3.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 2rem;
        animation: fadeInUp 1s ease-out;
    }
    
    /* Gradient background */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Animated cards */
    .metric-container {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .metric-container:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
    }
    
    /* Enhanced tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255, 255, 255, 0.1);
        padding: 8px;
        border-radius: 12px;
        backdrop-filter: blur(10px);
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background: rgba(255, 255, 255, 0.2);
        border-radius: 8px;
        gap: 1px;
        padding-left: 20px;
        padding-right: 20px;
        transition: all 0.3s ease;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Upload area styling */
    .stFileUploader > div > div {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 12px;
        border: 2px dashed #667eea;
        transition: all 0.3s ease;
    }
    
    .stFileUploader > div > div:hover {
        border-color: #764ba2;
        background: rgba(255, 255, 255, 1);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Animations */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    /* Success message animation */
    .stSuccess {
        animation: pulse 0.6s ease-in-out;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    /* Chart containers */
    .js-plotly-plot {
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    }
    
    /* Loading spinner */
    .stSpinner {
        border: 3px solid rgba(102, 126, 234, 0.3);
        border-radius: 50%;
        border-top: 3px solid #667eea;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = []
if 'webcam_enabled' not in st.session_state:
    st.session_state.webcam_enabled = False
if 'processing_stats' not in st.session_state:
    st.session_state.processing_stats = {
        'total_processed': 0,
        'avg_processing_time': 0,
        'success_rate': 0
    }

def analyze_image(image_file, filename=None):
    """Analyze a single image and return results with confidence scores."""
    start_time = time.time()
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
            tmp_file.write(image_file.read())
            tmp_path = tmp_file.name
        
        # Analyze the image
        result = DeepFace.analyze(tmp_path, actions=['gender', 'race', 'age'])
        
        # Clean up temporary file
        os.unlink(tmp_path)
        
        # Extract results with confidence scores
        analysis = result[0]
        
        # Get confidence scores for race
        race_scores = analysis['race']
        dominant_race = max(race_scores, key=race_scores.get)
        race_confidence = race_scores[dominant_race]
        
        # Get confidence scores for gender
        gender_scores = analysis['gender']
        dominant_gender = max(gender_scores, key=gender_scores.get)
        gender_confidence = gender_scores[dominant_gender]
        
        processing_time = time.time() - start_time
        
        # Update processing stats
        st.session_state.processing_stats['total_processed'] += 1
        total = st.session_state.processing_stats['total_processed']
        current_avg = st.session_state.processing_stats['avg_processing_time']
        st.session_state.processing_stats['avg_processing_time'] = (current_avg * (total - 1) + processing_time) / total
        
        return {
            'filename': filename or image_file.name,
            'age': analysis['age'],
            'gender': dominant_gender,
            'gender_confidence': gender_confidence,
            'race': dominant_race,
            'race_confidence': race_confidence,
            'race_scores': race_scores,
            'gender_scores': gender_scores,
            'processing_time': processing_time,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
    except Exception as e:
        st.error(f"Error analyzing image: {str(e)}")
        return None

def analyze_webcam_frame(frame):
    """Analyze a webcam frame and return results."""
    try:
        # Convert frame to PIL Image
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(frame_rgb)
        
        # Save frame temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
            pil_image.save(tmp_file.name, 'JPEG')
            tmp_path = tmp_file.name
        
        # Analyze the frame
        result = DeepFace.analyze(tmp_path, actions=['gender', 'race', 'age'])
        
        # Clean up temporary file
        os.unlink(tmp_path)
        
        # Extract results
        analysis = result[0]
        race_scores = analysis['race']
        dominant_race = max(race_scores, key=race_scores.get)
        race_confidence = race_scores[dominant_race]
        
        gender_scores = analysis['gender']
        dominant_gender = max(gender_scores, key=gender_scores.get)
        gender_confidence = gender_scores[dominant_gender]
        
        return {
            'age': analysis['age'],
            'gender': dominant_gender,
            'gender_confidence': gender_confidence,
            'race': dominant_race,
            'race_confidence': race_confidence,
            'race_scores': race_scores,
            'gender_scores': gender_scores
        }
        
    except Exception as e:
        return None

def create_advanced_charts(df):
    """Create advanced interactive charts with more insights."""
    if df.empty:
        return None, None, None, None
    
    # Age distribution with confidence overlay
    age_fig = px.histogram(
        df, 
        x='age', 
        nbins=20,
        title="Age Distribution with Confidence",
        labels={'age': 'Age', 'count': 'Number of Images'},
        color_discrete_sequence=['#667eea'],
        opacity=0.8
    )
    age_fig.update_layout(
        xaxis_title="Age",
        yaxis_title="Number of Images",
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    # Gender distribution with confidence
    gender_df = df.groupby('gender').agg({
        'gender_confidence': 'mean',
        'filename': 'count'
    }).reset_index()
    gender_df.columns = ['Gender', 'Avg Confidence', 'Count']
    
    gender_fig = px.pie(
        values=gender_df['Count'],
        names=gender_df['Gender'],
        title="Gender Distribution",
        color_discrete_sequence=['#ff7f0e', '#2ca02c'],
        hover_data={'Avg Confidence': ':.1f'}
    )
    
    # Race distribution with confidence bars
    race_df = df.groupby('race').agg({
        'race_confidence': 'mean',
        'filename': 'count'
    }).reset_index()
    race_df.columns = ['Race', 'Avg Confidence', 'Count']
    
    race_fig = px.bar(
        race_df,
        x='Race',
        y='Count',
        color='Avg Confidence',
        title="Race/Ethnicity Distribution with Average Confidence",
        color_continuous_scale='viridis',
        hover_data={'Avg Confidence': ':.1f'}
    )
    race_fig.update_layout(
        xaxis_title="Race/Ethnicity",
        yaxis_title="Number of Images",
        showlegend=False
    )
    
    # Processing time analysis
    if 'processing_time' in df.columns:
        time_fig = px.scatter(
            df,
            x='age',
            y='processing_time',
            color='gender',
            size='gender_confidence',
            title="Processing Time vs Age (colored by gender, sized by confidence)",
            hover_data=['filename', 'race', 'race_confidence']
        )
        time_fig.update_layout(
            xaxis_title="Age",
            yaxis_title="Processing Time (seconds)"
        )
    else:
        time_fig = None
    
    return age_fig, gender_fig, race_fig, time_fig

def create_distribution_charts(df):
    """Create distribution charts for the analysis results."""
    if df.empty:
        return None, None, None
    
    # Age distribution
    age_fig = px.histogram(
        df, 
        x='age', 
        nbins=20,
        title="Age Distribution",
        labels={'age': 'Age', 'count': 'Number of Images'},
        color_discrete_sequence=['#1f77b4']
    )
    age_fig.update_layout(
        xaxis_title="Age",
        yaxis_title="Number of Images",
        showlegend=False
    )
    
    # Gender distribution
    gender_counts = df['gender'].value_counts()
    gender_fig = px.pie(
        values=gender_counts.values,
        names=gender_counts.index,
        title="Gender Distribution",
        color_discrete_sequence=['#ff7f0e', '#2ca02c']
    )
    
    # Race distribution
    race_counts = df['race'].value_counts()
    race_fig = px.bar(
        x=race_counts.index,
        y=race_counts.values,
        title="Race/Ethnicity Distribution",
        labels={'x': 'Race/Ethnicity', 'y': 'Number of Images'},
        color=race_counts.values,
        color_continuous_scale='viridis'
    )
    race_fig.update_layout(
        xaxis_title="Race/Ethnicity",
        yaxis_title="Number of Images",
        showlegend=False
    )
    
    return age_fig, gender_fig, race_fig

def main():
    # Header
    st.markdown('<h1 class="main-header">🔍 DeepFace Analyzer</h1>', unsafe_allow_html=True)
    st.markdown("Upload images to analyze facial demographics including age, gender, and race/ethnicity with confidence scores.")
    
    # Sidebar for image upload and controls
    with st.sidebar:
        st.header("📁 Upload Images")
        
        # Mode selection
        mode = st.radio(
            "Choose Analysis Mode:",
            ["📁 File Upload", "📹 Webcam Live", "📊 Analytics Dashboard"],
            help="Select how you want to analyze faces"
        )
        
        if mode == "📁 File Upload":
            uploaded_files = st.file_uploader(
                "Choose images to analyze",
                type=['jpg', 'jpeg', 'png', 'bmp'],
                accept_multiple_files=True,
                help="Upload one or more images containing faces"
            )
            
            if uploaded_files:
                st.success(f"📸 {len(uploaded_files)} image(s) uploaded")
                
                # Analyze button
                if st.button("🔍 Analyze Images", type="primary"):
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    for i, uploaded_file in enumerate(uploaded_files):
                        status_text.text(f"Processing {uploaded_file.name}...")
                        result = analyze_image(uploaded_file)
                        if result:
                            st.session_state.analysis_results.append(result)
                        progress_bar.progress((i + 1) / len(uploaded_files))
                    
                    status_text.text("Analysis complete!")
                    st.success("✅ All images processed successfully!")
        
        elif mode == "📹 Webcam Live":
            st.info("🎥 Webcam feature requires camera access")
            if st.button("📹 Start Webcam Analysis", type="primary"):
                st.session_state.webcam_enabled = True
            
            if st.button("⏹️ Stop Webcam"):
                st.session_state.webcam_enabled = False
        
        elif mode == "📊 Analytics Dashboard":
            st.markdown("### 📈 Performance Metrics")
            stats = st.session_state.processing_stats
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Processed", stats['total_processed'])
                st.metric("Avg Processing Time", f"{stats['avg_processing_time']:.2f}s")
            
            with col2:
                if stats['total_processed'] > 0:
                    success_rate = len([r for r in st.session_state.analysis_results if r]) / stats['total_processed'] * 100
                    st.metric("Success Rate", f"{success_rate:.1f}%")
                else:
                    st.metric("Success Rate", "N/A")
        
        # Clear results button
        if st.button("🗑️ Clear All Results"):
            st.session_state.analysis_results = []
            st.session_state.processing_stats = {
                'total_processed': 0,
                'avg_processing_time': 0,
                'success_rate': 0
            }
            st.rerun()
    
    # Main content area
    if not st.session_state.analysis_results:
        st.info("👆 Upload some images using the sidebar to get started!")
        
        # Show example of what the app does
        st.markdown("### What this app analyzes:")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **👤 Gender Detection**
            - Male/Female classification
            - Confidence scores
            """)
        
        with col2:
            st.markdown("""
            **🎂 Age Estimation**
            - Approximate age in years
            - Based on facial features
            """)
        
        with col3:
            st.markdown("""
            **🌍 Race/Ethnicity**
            - Multiple race categories
            - Confidence scores for each
            """)
    
    else:
        # Convert results to DataFrame
        df = pd.DataFrame(st.session_state.analysis_results)
        
        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs(["📊 Individual Results", "📈 Distribution Charts", "📋 Data Table"])
        
        with tab1:
            st.header("Individual Image Analysis")
            
            # Display results for each image
            for i, result in enumerate(st.session_state.analysis_results):
                with st.expander(f"📷 {result['filename']}", expanded=True):
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        # Display the uploaded image
                        try:
                            # Re-upload and display the image
                            st.image(uploaded_files[i], caption=result['filename'], use_column_width=True)
                        except:
                            st.info("Image preview not available")
                    
                    with col2:
                        # Display analysis results
                        st.markdown("### Analysis Results")
                        
                        # Age
                        st.metric(
                            label="🎂 Age",
                            value=f"{result['age']} years"
                        )
                        
                        # Gender with confidence
                        st.metric(
                            label="👤 Gender",
                            value=result['gender'],
                            delta=f"{result['gender_confidence']:.1f}% confidence"
                        )
                        
                        # Race with confidence
                        st.metric(
                            label="🌍 Race/Ethnicity",
                            value=result['race'],
                            delta=f"{result['race_confidence']:.1f}% confidence"
                        )
                        
                        # Detailed confidence scores
                        st.markdown("#### Detailed Confidence Scores")
                        
                        col_gender, col_race = st.columns(2)
                        
                        with col_gender:
                            st.markdown("**Gender Scores:**")
                            for gender, score in result['gender_scores'].items():
                                st.write(f"• {gender}: {score:.1f}%")
                        
                        with col_race:
                            st.markdown("**Race Scores:**")
                            for race, score in result['race_scores'].items():
                                st.write(f"• {race}: {score:.1f}%")
        
        with tab2:
            st.header("Advanced Analytics Dashboard")
            
            # Create and display advanced charts
            age_fig, gender_fig, race_fig, time_fig = create_advanced_charts(df)
            
            if age_fig:
                # Top row - Age and Gender
                col1, col2 = st.columns(2)
                
                with col1:
                    st.plotly_chart(age_fig, use_container_width=True)
                
                with col2:
                    st.plotly_chart(gender_fig, use_container_width=True)
                
                # Race distribution
                st.plotly_chart(race_fig, use_container_width=True)
                
                # Processing time analysis (if available)
                if time_fig:
                    st.plotly_chart(time_fig, use_container_width=True)
                
                # Enhanced summary statistics
                st.markdown("### 📊 Advanced Statistics")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Images", len(df))
                    st.metric("Age Range", f"{df['age'].min()}-{df['age'].max()}")
                
                with col2:
                    st.metric("Average Age", f"{df['age'].mean():.1f} years")
                    st.metric("Age Std Dev", f"{df['age'].std():.1f}")
                
                with col3:
                    most_common_gender = df['gender'].mode().iloc[0] if not df['gender'].mode().empty else "N/A"
                    avg_gender_conf = df['gender_confidence'].mean()
                    st.metric("Most Common Gender", most_common_gender)
                    st.metric("Avg Gender Confidence", f"{avg_gender_conf:.1f}%")
                
                with col4:
                    most_common_race = df['race'].mode().iloc[0] if not df['race'].mode().empty else "N/A"
                    avg_race_conf = df['race_confidence'].mean()
                    st.metric("Most Common Race", most_common_race)
                    st.metric("Avg Race Confidence", f"{avg_race_conf:.1f}%")
                
                # Performance metrics
                if 'processing_time' in df.columns:
                    st.markdown("### ⚡ Performance Metrics")
                    perf_col1, perf_col2, perf_col3 = st.columns(3)
                    
                    with perf_col1:
                        st.metric("Avg Processing Time", f"{df['processing_time'].mean():.2f}s")
                    
                    with perf_col2:
                        st.metric("Fastest Processing", f"{df['processing_time'].min():.2f}s")
                    
                    with perf_col3:
                        st.metric("Slowest Processing", f"{df['processing_time'].max():.2f}s")
        
        with tab3:
            st.header("Data Table")
            
            # Display the raw data
            display_df = df[['filename', 'age', 'gender', 'gender_confidence', 'race', 'race_confidence']].copy()
            display_df.columns = ['Filename', 'Age', 'Gender', 'Gender Confidence (%)', 'Race/Ethnicity', 'Race Confidence (%)']
            
            st.dataframe(display_df, use_container_width=True)
            
            # Download button
            csv = display_df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name="face_analysis_results.csv",
                mime="text/csv"
            )

if __name__ == "__main__":
    main()
