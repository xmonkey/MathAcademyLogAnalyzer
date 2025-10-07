#!/usr/bin/env python3
"""
Comprehensive analysis and visualization script for course progress data
Generates multiple charts and an interactive dashboard
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import os

# Ensure output directory exists
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Set style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def load_data():
    """Load course data from JSON file"""
    with open('ella_course_data.json', 'r') as f:
        data = json.load(f)
    return data

def create_overview_charts(data):
    """Create overview analysis charts"""
    stats = data['statistics']
    activities = pd.DataFrame(data['activities'])
    
    # Convert date to datetime
    activities['Date'] = pd.to_datetime(activities['Date'])
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 3, figsize=(20, 12))
    fig.suptitle('Course Progress Analysis', fontsize=16, fontweight='bold')
    
    # 1. XP by Course
    course_xp = {course: info['xp'] for course, info in stats['course_breakdown'].items()}
    axes[0, 0].pie(course_xp.values(), labels=course_xp.keys(), autopct='%1.1f%%')
    axes[0, 0].set_title('XP Distribution by Course')
    
    # 2. Task Type Distribution
    task_counts = {task: info['count'] for task, info in stats['task_type_breakdown'].items()}
    bars = axes[0, 1].bar(task_counts.keys(), task_counts.values())
    axes[0, 1].set_title('Task Type Distribution')
    axes[0, 1].tick_params(axis='x', rotation=45)
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        axes[0, 1].text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}', ha='center', va='bottom')
    
    # 3. Daily XP Progress
    daily_data = pd.DataFrame([
        {'Date': date, 'XP': info['total_xp'], 'Tasks': info['task_count']}
        for date, info in stats['daily_breakdown'].items()
    ])
    daily_data['Date'] = pd.to_datetime(daily_data['Date'])
    daily_data = daily_data.sort_values('Date')
    
    axes[0, 2].plot(daily_data['Date'], daily_data['XP'], marker='o', linewidth=2, markersize=4)
    axes[0, 2].set_title('Daily XP Progress')
    axes[0, 2].set_xlabel('Date')
    axes[0, 2].set_ylabel('XP Earned')
    axes[0, 2].tick_params(axis='x', rotation=45)
    
    # 4. XP Performance by Task Type
    task_performance = {task: info['xp'] for task, info in stats['task_type_breakdown'].items()}
    bars = axes[1, 0].bar(task_performance.keys(), task_performance.values(), color='lightcoral')
    axes[1, 0].set_title('XP Earned by Task Type')
    axes[1, 0].tick_params(axis='x', rotation=45)
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        axes[1, 0].text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}', ha='center', va='bottom')
    
    # 5. Weekly Activity Pattern
    activities['Weekday'] = activities['Date'].dt.day_name()
    weekly_activity = activities.groupby('Weekday').size().reindex(
        ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'], fill_value=0
    )
    
    bars = axes[1, 1].bar(weekly_activity.index, weekly_activity.values, color='lightgreen')
    axes[1, 1].set_title('Activity by Day of Week')
    axes[1, 1].tick_params(axis='x', rotation=45)
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        axes[1, 1].text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}', ha='center', va='bottom')
    
    # 6. Course Progress Timeline
    for i, (course, info) in enumerate(stats['course_breakdown'].items()):
        course_activities = activities[activities['Course'] == course]
        if len(course_activities) > 0:
            cumulative_xp = course_activities.sort_values('Date')['XP Earned'].cumsum()
            axes[1, 2].plot(course_activities.sort_values('Date')['Date'], cumulative_xp, 
                           marker='o', label=course, linewidth=2, markersize=3)
    
    axes[1, 2].set_title('Cumulative XP by Course')
    axes[1, 2].set_xlabel('Date')
    axes[1, 2].set_ylabel('Cumulative XP')
    axes[1, 2].legend()
    axes[1, 2].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    output_file = os.path.join(OUTPUT_DIR, 'analysis_overview.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Overview charts saved as '{output_file}'")

def create_interactive_dashboard(data):
    """Create interactive dashboard using Plotly"""
    stats = data['statistics']
    activities = pd.DataFrame(data['activities'])
    activities['Date'] = pd.to_datetime(activities['Date'])
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Daily XP Progress', 'Course Distribution', 
                       'Task Type Analysis', 'Weekly Activity'),
        specs=[[{"secondary_y": False}, {"type": "pie"}],
               [{"secondary_y": False}, {"type": "bar"}]]
    )
    
    # 1. Daily XP Progress
    daily_data = pd.DataFrame([
        {'Date': date, 'XP': info['total_xp'], 'Tasks': info['task_count']}
        for date, info in stats['daily_breakdown'].items()
    ])
    daily_data['Date'] = pd.to_datetime(daily_data['Date'])
    daily_data = daily_data.sort_values('Date')
    
    fig.add_trace(
        go.Scatter(x=daily_data['Date'], y=daily_data['XP'],
                  mode='lines+markers', name='Daily XP',
                  line=dict(color='royalblue', width=2)),
        row=1, col=1
    )
    
    # 2. Course Distribution
    course_xp = {course: info['xp'] for course, info in stats['course_breakdown'].items()}
    fig.add_trace(
        go.Pie(labels=list(course_xp.keys()), values=list(course_xp.values()),
               name="Course XP"),
        row=1, col=2
    )
    
    # 3. Task Type Analysis
    task_data = pd.DataFrame([
        {'Task': task, 'Count': info['count'], 'XP': info['xp']}
        for task, info in stats['task_type_breakdown'].items()
    ])
    
    fig.add_trace(
        go.Bar(x=task_data['Task'], y=task_data['Count'],
               name='Task Count', marker_color='lightcoral'),
        row=2, col=1
    )
    
    # 4. Weekly Activity
    activities['Weekday'] = activities['Date'].dt.day_name()
    weekly_activity = activities.groupby('Weekday').size().reindex(
        ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'], fill_value=0
    )
    
    fig.add_trace(
        go.Bar(x=weekly_activity.index, y=weekly_activity.values,
               name='Weekly Activity', marker_color='lightgreen'),
        row=2, col=2
    )
    
    # Update layout
    fig.update_layout(
        title_text="Interactive Course Dashboard",
        showlegend=False,
        height=800
    )
    
    # Save as HTML
    output_file = os.path.join(OUTPUT_DIR, "interactive_dashboard.html")
    fig.write_html(output_file)
    print(f"Interactive dashboard saved as '{output_file}'")

def create_performance_analysis(data):
    """Create detailed performance analysis charts"""
    stats = data['statistics']
    activities = pd.DataFrame(data['activities'])
    activities['Date'] = pd.to_datetime(activities['Date'])
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    fig.suptitle('Performance Analysis', fontsize=16, fontweight='bold')
    
    # 1. XP Efficiency (XP Earned vs XP Possible)
    activities['Efficiency'] = activities['XP Earned'] / activities['XP Possible']
    
    # Group by task type
    efficiency_by_task = activities.groupby('Task')['Efficiency'].mean().sort_values(ascending=False)
    
    bars = axes[0, 0].bar(efficiency_by_task.index, efficiency_by_task.values)
    axes[0, 0].set_title('Average XP Efficiency by Task Type')
    axes[0, 0].set_ylabel('Efficiency (Earned/Possible)')
    axes[0, 0].tick_params(axis='x', rotation=45)
    axes[0, 0].axhline(y=1.0, color='red', linestyle='--', alpha=0.7, label='100% Efficiency')
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        axes[0, 0].text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.2f}', ha='center', va='bottom')
    
    # 2. Monthly Progress
    activities['Month'] = activities['Date'].dt.strftime('%Y-%m')
    monthly_stats = activities.groupby('Month').agg({
        'XP Earned': 'sum',
        'Task': 'count'
    }).reset_index()
    
    ax2 = axes[0, 1]
    ax2_twin = ax2.twinx()
    
    bars = ax2.bar(monthly_stats['Month'], monthly_stats['XP Earned'], 
                   alpha=0.7, color='skyblue', label='Total XP')
    line = ax2_twin.plot(monthly_stats['Month'], monthly_stats['Task'], 
                        'ro-', linewidth=2, markersize=6, label='Task Count')
    
    ax2.set_title('Monthly Progress')
    ax2.set_xlabel('Month')
    ax2.set_ylabel('Total XP', color='skyblue')
    ax2_twin.set_ylabel('Number of Tasks', color='red')
    ax2.tick_params(axis='x', rotation=45)
    
    # 3. Course Progression Timeline
    course_colors = {'Prealgebra': 'blue', 'Integrated Math I (Honors)': 'red', 
                    '5Th Grade Math': 'green', '4Th Grade Math': 'orange'}
    
    for course, color in course_colors.items():
        course_data = activities[activities['Course'] == course]
        if len(course_data) > 0:
            course_data_sorted = course_data.sort_values('Date')
            cumulative_xp = course_data_sorted['XP Earned'].cumsum()
            axes[1, 0].plot(course_data_sorted['Date'], cumulative_xp, 
                           marker='o', label=course, color=color, linewidth=2, markersize=4)
    
    axes[1, 0].set_title('Course Progression Timeline')
    axes[1, 0].set_xlabel('Date')
    axes[1, 0].set_ylabel('Cumulative XP')
    axes[1, 0].legend()
    axes[1, 0].tick_params(axis='x', rotation=45)
    axes[1, 0].grid(True, alpha=0.3)
    
    # 4. Performance Distribution
    axes[1, 1].hist(activities['XP Earned'], bins=20, alpha=0.7, color='lightcoral', edgecolor='black')
    axes[1, 1].axvline(activities['XP Earned'].mean(), color='red', linestyle='--', 
                       linewidth=2, label=f'Mean: {activities["XP Earned"].mean():.1f}')
    axes[1, 1].axvline(activities['XP Earned'].median(), color='green', linestyle='--', 
                       linewidth=2, label=f'Median: {activities["XP Earned"].median():.1f}')
    axes[1, 1].set_title('Distribution of XP Earned per Task')
    axes[1, 1].set_xlabel('XP Earned')
    axes[1, 1].set_ylabel('Frequency')
    axes[1, 1].legend()
    
    plt.tight_layout()
    output_file = os.path.join(OUTPUT_DIR, 'performance_analysis.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Performance analysis saved as '{output_file}'")

def generate_summary_report(data):
    """Generate a comprehensive summary report"""
    stats = data['statistics']
    activities = pd.DataFrame(data['activities'])
    activities['Date'] = pd.to_datetime(activities['Date'])
    
    report = f"""
ELLA'S COURSE PROGRESS SUMMARY REPORT
=====================================

GENERAL STATISTICS:
- Total Activities: {len(activities)}
- Total XP Earned: {stats['total_xp']}
- Total Possible XP: {stats['total_possible']}
- Overall Completion Rate: {stats['completion_rate']}
- Average XP per Task: {stats['average_xp_per_task']:.1f}
- Date Range: {stats['date_range']['start']} to {stats['date_range']['end']}

COURSE BREAKDOWN:
"""
    
    for course, info in stats['course_breakdown'].items():
        report += f"""
- {course}:
  * Activities: {info['count']}
  * XP Earned: {info['xp']}
  * Average XP per Activity: {info['xp']/info['count']:.1f}
"""
    
    report += """
TASK TYPE PERFORMANCE:
"""
    
    for task_type, info in stats['task_type_breakdown'].items():
        report += f"""
- {task_type}:
  * Count: {info['count']}
  * Total XP: {info['xp']}
  * Average XP: {info['xp']/info['count']:.1f}
"""
    
    # Calculate additional insights
    report += f"""

LEARNING INSIGHTS:
- Most Active Course: {max(stats['course_breakdown'].items(), key=lambda x: x[1]['count'])[0]}
- Highest XP Course: {max(stats['course_breakdown'].items(), key=lambda x: x[1]['xp'])[0]}
- Most Common Task Type: {max(stats['task_type_breakdown'].items(), key=lambda x: x[1]['count'])[0]}
- Most Productive Task Type: {max(stats['task_type_breakdown'].items(), key=lambda x: x[1]['xp']/x[1]['count'])[0]}

ACTIVITY PATTERNS:
- Study Period: {(pd.to_datetime(stats['date_range']['end']) - pd.to_datetime(stats['date_range']['start'])).days} days
- Average Activities per Day: {len(activities) / max(1, (pd.to_datetime(stats['date_range']['end']) - pd.to_datetime(stats['date_range']['start'])).days):.1f}
- Average XP per Day: {stats['total_xp'] / max(1, (pd.to_datetime(stats['date_range']['end']) - pd.to_datetime(stats['date_range']['start'])).days):.1f}
"""
    
    output_file = os.path.join(OUTPUT_DIR, 'summary_report.txt')
    with open(output_file, 'w') as f:
        f.write(report)
    
    print(f"Summary report saved as '{output_file}'")

def main():
    """Main function to generate all analysis"""
    print("Loading course data...")
    data = load_data()
    
    print("Generating overview charts...")
    create_overview_charts(data)
    
    print("Creating interactive dashboard...")
    create_interactive_dashboard(data)
    
    print("Analyzing performance metrics...")
    create_performance_analysis(data)
    
    print("Generating summary report...")
    generate_summary_report(data)
    
    print("\n" + "="*50)
    print("ANALYSIS COMPLETE!")
    print("="*50)
    print(f"Generated files in {OUTPUT_DIR}/:")
    print("- analysis_overview.png (6 comprehensive charts)")
    print("- performance_analysis.png (4 detailed performance charts)")
    print("- interactive_dashboard.html (interactive web dashboard)")
    print("- summary_report.txt (detailed text report)")
    print(f"\nOpen {OUTPUT_DIR}/interactive_dashboard.html in your browser for the interactive experience!")

if __name__ == "__main__":
    main()