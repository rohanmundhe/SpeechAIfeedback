import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
import numpy as np
import pandas as pd

def create_visualizations(speech_metrics):
    """Create interactive visualizations for speech analysis results"""
    
    # Volume stability over time
    st.subheader("🔊 Volume Analysis Over Time")
    create_volume_timeline(speech_metrics['rms_values'], speech_metrics['duration'])
    
    # Speaking metrics radar chart
    st.subheader("📊 Speaking Performance Radar")
    create_performance_radar(speech_metrics)
    
    # Comparison with benchmarks
    st.subheader("🎯 Performance vs. Benchmarks")
    create_benchmark_comparison(speech_metrics)

def create_volume_timeline(rms_values, duration):
    """Create volume stability timeline visualization"""
    if rms_values is None or len(rms_values) == 0:
        st.warning("No volume data available for visualization")
        return
    
    # Create time axis
    time_points = np.linspace(0, duration, len(rms_values))
    
    # Ensure rms_values is a list or array we can iterate over
    if isinstance(rms_values, np.ndarray):
        rms_list = rms_values.tolist()
    else:
        rms_list = list(rms_values)
    
    # Convert RMS to dB for better visualization
    rms_db = [20 * np.log10(max(rms, 1e-10)) for rms in rms_list]
    
    # Create the plot
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=time_points,
        y=rms_db,
        mode='lines+markers',
        name='Volume Level',
        line=dict(color='#1f77b4', width=2),
        marker=dict(size=4),
        hovertemplate='Time: %{x:.1f}s<br>Volume: %{y:.1f} dB<extra></extra>'
    ))
    
    # Add average line
    avg_volume = np.mean(rms_db)
    fig.add_hline(
        y=avg_volume,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Average: {avg_volume:.1f} dB"
    )
    
    fig.update_layout(
        title="Volume Stability Over Time",
        xaxis_title="Time (seconds)",
        yaxis_title="Volume (dB)",
        height=400,
        showlegend=True,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_performance_radar(speech_metrics):
    """Create radar chart for overall performance metrics"""
    
    # Define metrics and their values (normalized to 0-10 scale)
    categories = [
        'Speaking Pace',
        'Confidence Score', 
        'Volume Stability',
        'Clarity Score',
        'Fluency Score'
    ]
    
    # Normalize speaking pace to 0-10 scale (120-180 WPM is optimal)
    wpm = speech_metrics['words_per_minute']
    if 140 <= wpm <= 180:
        pace_score = 10
    elif wpm < 140:
        pace_score = max(1, 10 - (140 - wpm) / 10)
    else:
        pace_score = max(1, 10 - (wpm - 180) / 20)
    
    # Calculate clarity score based on filler percentage
    clarity_score = max(1, 10 - speech_metrics['filler_percentage'] / 2)
    
    # Calculate fluency score (inverse of filler percentage + pace)
    fluency_score = max(1, min(10, (pace_score + clarity_score) / 2))
    
    values = [
        pace_score,
        speech_metrics['confidence_score'],
        speech_metrics['volume_stability'],
        clarity_score,
        fluency_score
    ]
    
    # Create radar chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],  # Close the polygon
        theta=categories + [categories[0]],
        fill='toself',
        name='Your Performance',
        fillcolor='rgba(31, 119, 180, 0.3)',
        line_color='rgba(31, 119, 180, 1)',
        line_width=2
    ))
    
    # Add benchmark line (ideal performance)
    ideal_values = [8, 8, 8, 8, 8]  # Good benchmark scores
    fig.add_trace(go.Scatterpolar(
        r=ideal_values + [ideal_values[0]],
        theta=categories + [categories[0]],
        fill='tonext',
        name='Target Performance',
        fillcolor='rgba(50, 205, 50, 0.2)',
        line_color='rgba(50, 205, 50, 1)',
        line_dash='dash',
        line_width=2
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10],
                tickmode='linear',
                tick0=0,
                dtick=2
            )
        ),
        title="Speech Performance Overview",
        height=500,
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_benchmark_comparison(speech_metrics):
    """Create comparison chart with industry benchmarks"""
    
    # Define benchmarks
    benchmarks = {
        'Speaking Pace (WPM)': {
            'your_value': speech_metrics['words_per_minute'],
            'benchmark_min': 140,
            'benchmark_max': 180,
            'optimal': 160
        },
        'Filler Words (%)': {
            'your_value': speech_metrics['filler_percentage'],
            'benchmark_min': 0,
            'benchmark_max': 3,
            'optimal': 1.5
        },
        'Volume Stability': {
            'your_value': speech_metrics['volume_stability'],
            'benchmark_min': 7,
            'benchmark_max': 10,
            'optimal': 8.5
        },
        'Confidence Score': {
            'your_value': speech_metrics['confidence_score'],
            'benchmark_min': 7,
            'benchmark_max': 10,
            'optimal': 8.5
        }
    }
    
    # Create subplot data
    metrics = []
    your_values = []
    optimal_values = []
    colors = []
    
    for metric, data in benchmarks.items():
        metrics.append(metric)
        your_values.append(data['your_value'])
        optimal_values.append(data['optimal'])
        
        # Determine color based on performance
        if metric == 'Filler Words (%)':  # Lower is better
            if data['your_value'] <= data['optimal']:
                colors.append('green')
            elif data['your_value'] <= data['benchmark_max']:
                colors.append('orange')
            else:
                colors.append('red')
        else:  # Higher is better
            if data['your_value'] >= data['optimal']:
                colors.append('green')
            elif data['your_value'] >= data['benchmark_min']:
                colors.append('orange')
            else:
                colors.append('red')
    
    # Create comparison chart
    fig = go.Figure()
    
    # Your performance bars
    fig.add_trace(go.Bar(
        name='Your Performance',
        x=metrics,
        y=your_values,
        marker_color=colors,
        text=[f'{val:.1f}' for val in your_values],
        textposition='auto',
    ))
    
    # Optimal performance bars
    fig.add_trace(go.Bar(
        name='Optimal Performance',
        x=metrics,
        y=optimal_values,
        marker_color='rgba(50, 205, 50, 0.6)',
        text=[f'{val:.1f}' for val in optimal_values],
        textposition='auto',
    ))
    
    fig.update_layout(
        title="Performance vs. Optimal Benchmarks",
        xaxis_title="Metrics",
        yaxis_title="Score/Value",
        barmode='group',
        height=400,
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Add performance interpretation
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**🟢 Excellent:** Meeting or exceeding optimal performance")
    with col2:
        st.markdown("**🟡 Good:** Within acceptable range, room for improvement")
    with col3:
        st.markdown("**🔴 Needs Work:** Below recommended benchmarks")
