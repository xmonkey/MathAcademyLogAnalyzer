#!/usr/bin/env python3
"""
Simple command-line chart generator for Ella's course data
Usage: python simple_charts.py [chart_type]
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import sys
import os

# Ensure output directory exists
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_data():
    """Load Ella's course data"""
    with open('ella_course_data.json', 'r') as f:
        return json.load(f)

def create_course_pie_chart(data):
    """Create simple pie chart of courses"""
    stats = data['statistics']
    course_xp = {course: info['xp'] for course, info in stats['course_breakdown'].items()}
    
    plt.figure(figsize=(8, 6))
    plt.pie(course_xp.values(), labels=course_xp.keys(), autopct='%1.1f%%')
    plt.title('Ella\'s XP Distribution by Course')
    plt.tight_layout()
    output_file = os.path.join(OUTPUT_DIR, 'course_pie_chart.png')
    plt.savefig(output_file, dpi=150)
    plt.close()
    print(f"Created: {output_file}")

def create_daily_progress_chart(data):
    """Create simple line chart of daily progress"""
    stats = data['statistics']
    daily_data = pd.DataFrame([
        {'Date': date, 'XP': info['total_xp']}
        for date, info in stats['daily_breakdown'].items()
    ])
    daily_data['Date'] = pd.to_datetime(daily_data['Date'])
    daily_data = daily_data.sort_values('Date')
    
    plt.figure(figsize=(12, 6))
    plt.plot(daily_data['Date'], daily_data['XP'], marker='o', linewidth=2)
    plt.title('Ella\'s Daily XP Progress')
    plt.xlabel('Date')
    plt.ylabel('XP Earned')
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    output_file = os.path.join(OUTPUT_DIR, 'daily_progress_chart.png')
    plt.savefig(output_file, dpi=150)
    plt.close()
    print(f"Created: {output_file}")

def create_task_type_bar_chart(data):
    """Create bar chart of task types"""
    stats = data['statistics']
    task_counts = {task: info['count'] for task, info in stats['task_type_breakdown'].items()}
    
    plt.figure(figsize=(10, 6))
    bars = plt.bar(task_counts.keys(), task_counts.values())
    plt.title('Ella\'s Task Type Distribution')
    plt.xlabel('Task Type')
    plt.ylabel('Number of Tasks')
    plt.xticks(rotation=45)
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}', ha='center', va='bottom')
    
    plt.tight_layout()
    output_file = os.path.join(OUTPUT_DIR, 'task_type_chart.png')
    plt.savefig(output_file, dpi=150)
    plt.close()
    print(f"Created: {output_file}")

def create_all_charts():
    """Create all simple charts"""
    print("Generating simple charts for Ella's data...")
    data = load_data()
    
    create_course_pie_chart(data)
    create_daily_progress_chart(data)
    create_task_type_bar_chart(data)
    
    print("\nSimple charts generated successfully!")
    print(f"Files created in {OUTPUT_DIR}/:")
    print("- course_pie_chart.png")
    print("- daily_progress_chart.png") 
    print("- task_type_chart.png")

def show_help():
    print("Simple Chart Generator for Ella's Course Data")
    print("=" * 45)
    print("Usage: python simple_charts.py [option]")
    print("\nOptions:")
    print("  all     - Generate all charts (default)")
    print("  pie     - Course distribution pie chart")
    print("  line    - Daily progress line chart") 
    print("  bar     - Task type bar chart")
    print("  help    - Show this help message")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        option = sys.argv[1].lower()
    else:
        option = "all"
    
    if option == "help":
        show_help()
    elif option == "pie":
        create_course_pie_chart(load_data())
    elif option == "line":
        create_daily_progress_chart(load_data())
    elif option == "bar":
        create_task_type_bar_chart(load_data())
    elif option == "all":
        create_all_charts()
    else:
        print(f"Unknown option: {option}")
        show_help()