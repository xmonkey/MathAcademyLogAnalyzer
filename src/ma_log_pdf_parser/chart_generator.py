"""Chart generation module for learning progress visualization."""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import numpy as np


class ChartGenerator:
    """Generate charts for learning progress data analysis."""
    
    def __init__(self, json_path: str):
        """Initialize chart generator with JSON data.
        
        Args:
            json_path: Path to the JSON file containing learning progress data
        """
        self.json_path = Path(json_path)
        self.data = self._load_data()
        self.df = self._process_data()
        
    def _load_data(self) -> Dict[str, Any]:
        """Load data from JSON file."""
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"JSON file not found: {self.json_path}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON file: {self.json_path}")
    
    def _process_data(self) -> pd.DataFrame:
        """Process JSON data into pandas DataFrame."""
        activities = self.data.get('activities', [])

        if not activities:
            return pd.DataFrame()

        # Convert to DataFrame
        df = pd.DataFrame(activities)

        # Convert date strings to datetime
        df['date'] = pd.to_datetime(df['Date'])

        # Extract XP values (handle both string and numeric)
        df['xp_numeric'] = pd.to_numeric(df['XP Earned'], errors='coerce')

        # Sort by date
        df = df.sort_values('date')

        return df
    
    def _calculate_cumulative_xp(self) -> pd.DataFrame:
        """Calculate cumulative XP by date."""
        if self.df.empty:
            return pd.DataFrame()

        # Group by date and sum XP
        daily_xp = self.df.groupby('date')['xp_numeric'].sum().reset_index()

        # CRITICAL: Sort by date to ensure correct cumulative calculation
        daily_xp = daily_xp.sort_values('date')

        # Calculate cumulative sum (now in correct date order)
        daily_xp['cumulative_xp'] = daily_xp['xp_numeric'].cumsum()

        return daily_xp

    def _calculate_cumulative_xp_by_course(self) -> pd.DataFrame:
        """Calculate cumulative XP by date and course."""
        if self.df.empty:
            return pd.DataFrame()

        # Group by date and course, sum XP
        daily_course_xp = self.df.groupby(['date', 'Course'])['xp_numeric'].sum().reset_index()

        # Sort by date and course
        daily_course_xp = daily_course_xp.sort_values(['date', 'Course'])

        # Calculate cumulative sum for each course
        daily_course_xp['cumulative_xp'] = daily_course_xp.groupby('Course')['xp_numeric'].cumsum()

        # Also calculate overall cumulative total for reference
        overall_daily = daily_course_xp.groupby('date')['xp_numeric'].sum().reset_index()
        overall_daily['cumulative_xp'] = overall_daily['xp_numeric'].cumsum()
        overall_daily['Course'] = 'Total'
        overall_daily = overall_daily[['date', 'Course', 'xp_numeric', 'cumulative_xp']]

        # Combine course data with total
        result = pd.concat([daily_course_xp, overall_daily], ignore_index=True)

        return result

    def _calculate_cumulative_xp_with_dominant_course(self) -> pd.DataFrame:
        """Calculate cumulative XP with dominant course color for each day."""
        if self.df.empty:
            return pd.DataFrame()

        # Group by date and course, sum XP
        daily_course_xp = self.df.groupby(['date', 'Course'])['xp_numeric'].sum().reset_index()

        # Find the dominant course for each day (course with most XP)
        dominant_course = daily_course_xp.loc[daily_course_xp.groupby('date')['xp_numeric'].idxmax()]
        dominant_course = dominant_course.rename(columns={'Course': 'dominant_course'})

        # Calculate daily total XP
        daily_total = self.df.groupby('date')['xp_numeric'].sum().reset_index()

        # Merge with dominant course info
        daily_data = pd.merge(daily_total, dominant_course[['date', 'dominant_course']], on='date', how='left')

        # CRITICAL: Sort by date to ensure correct cumulative calculation
        daily_data = daily_data.sort_values('date')

        # Calculate cumulative XP (now in correct date order)
        daily_data['cumulative_xp'] = daily_data['xp_numeric'].cumsum()

        # Fill missing dominant course (for days with no data)
        daily_data['dominant_course'] = daily_data['dominant_course'].fillna('Unknown')

        return daily_data

    def _get_course_appearance_order(self) -> List[str]:
        """Get courses in the order they first appear in the data."""
        if self.df.empty:
            return []

        # Get unique courses in order of first appearance
        courses_in_order = []
        seen_courses = set()

        for _, row in self.df.iterrows():
            course = row['Course']
            if course not in seen_courses:
                courses_in_order.append(course)
                seen_courses.add(course)

        return courses_in_order

    def _generate_course_colors(self) -> Dict[str, str]:
        """Generate colors dynamically for all courses in the data.

        Returns:
            Dictionary mapping course names to color hex codes
        """
        if self.df.empty:
            return {}

        # Get all unique courses
        all_courses = self.df['Course'].unique().tolist()

        # Color generation strategies for better visual distinction
        color_palettes = [
            # Primary palette - distinctive colors
            ['#A23B72', '#F18F01', '#C73E1D', '#4ECDC4', '#95E77E', '#2E86AB', '#9B59B6', '#E67E22'],
            # Secondary palette - extended colors
            ['#3498DB', '#E74C3C', '#F39C12', '#27AE60', '#8E44AD', '#16A085', '#D35400', '#2980B9'],
            # Tertiary palette - more variations
            ['#1ABC9C', '#34495E', '#F1C40F', '#E67E22', '#95A5A6', '#D35400', '#C0392B', '#7F8C8D'],
            # Additional colors for many courses
            ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F'],
            # More diverse colors
            ['#85C1E2', '#F8B739', '#52B788', '#E76F51', '#8E9AAF', '#C9ADA7', '#F2CC8F', '#81B29A']
        ]

        # Combine all palettes
        all_colors = []
        for palette in color_palettes:
            all_colors.extend(palette)

        # If we still need more colors, generate them programmatically
        if len(all_courses) > len(all_colors):
            additional_colors = self._generate_distinct_colors(len(all_courses) - len(all_colors))
            all_colors.extend(additional_colors)

        # Assign colors to courses
        colors = {}
        for i, course in enumerate(all_courses):
            if i < len(all_colors):
                colors[course] = all_colors[i]
            else:
                # Fallback to generated color
                colors[course] = self._generate_distinct_colors(1)[0]

        return colors

    def print_course_colors(self) -> None:
        """Print the color assignments for all courses.

        This method is useful for debugging and for users to see
        which colors are assigned to which courses.
        """
        colors = self._generate_course_colors()

        if not colors:
            print("No courses found or no data available.")
            return

        print("Course Color Assignments:")
        print("-" * 40)

        for course, color in colors.items():
            print(f"{course:30} {color}")

        print(f"\nTotal courses: {len(colors)}")

    def _generate_distinct_colors(self, count: int) -> List[str]:
        """Generate visually distinct colors programmatically.

        Args:
            count: Number of colors to generate

        Returns:
            List of hex color codes
        """
        colors = []

        # Use HSV color space for better distribution
        golden_ratio = 0.618033988749895
        h = 0.5  # Start hue

        for i in range(count):
            # Generate hue with golden ratio for better distribution
            h = (h + golden_ratio) % 1.0

            # Vary saturation and value for more distinction
            saturation = 0.6 + (i % 3) * 0.15  # 0.6, 0.75, 0.9
            value = 0.7 + (i % 2) * 0.2        # 0.7, 0.9

            # Convert HSV to RGB
            import colorsys
            rgb = colorsys.hsv_to_rgb(h, saturation, value)
            hex_color = '#{:02x}{:02x}{:02x}'.format(
                int(rgb[0] * 255),
                int(rgb[1] * 255),
                int(rgb[2] * 255)
            )
            colors.append(hex_color)

        return colors

    def _calculate_course_cumulative_xp(self) -> Dict[str, int]:
        """Calculate cumulative XP for each course.

        Returns:
            Dictionary mapping course names to their cumulative XP values
        """
        if self.df.empty:
            return {}

        # Group by course and sum XP
        course_xp = self.df.groupby('Course')['xp_numeric'].sum().reset_index()
        course_xp.columns = ['Course', 'Cumulative XP']

        # Convert to dictionary
        course_cumulative_xp = {}
        for _, row in course_xp.iterrows():
            course_cumulative_xp[row['Course']] = int(row['Cumulative XP'])

        return course_cumulative_xp

    def _calculate_daily_xp(self) -> pd.DataFrame:
        """Calculate daily XP with complete calendar date coverage."""
        if self.df.empty:
            return pd.DataFrame()

        # Group by date and sum XP
        daily_xp = self.df.groupby('date')['xp_numeric'].sum().reset_index()

        # Create complete date range from min to max date
        min_date = daily_xp['date'].min()
        max_date = daily_xp['date'].max()
        all_dates = pd.date_range(start=min_date, end=max_date, freq='D')

        # Create complete dataframe with all calendar dates
        complete_df = pd.DataFrame({'date': all_dates})

        # Merge with actual data (missing dates get 0 XP)
        daily_xp = complete_df.merge(daily_xp, on='date', how='left')
        daily_xp['xp_numeric'] = daily_xp['xp_numeric'].fillna(0)

        return daily_xp

    def _calculate_daily_xp_with_dominant_course(self) -> pd.DataFrame:
        """Calculate daily XP with dominant course color for each day."""
        if self.df.empty:
            return pd.DataFrame()

        # Group by date and course, sum XP
        daily_course_xp = self.df.groupby(['date', 'Course'])['xp_numeric'].sum().reset_index()

        # Find the dominant course for each day (course with most XP)
        dominant_course = daily_course_xp.loc[daily_course_xp.groupby('date')['xp_numeric'].idxmax()]
        dominant_course = dominant_course.rename(columns={'Course': 'dominant_course'})

        # Calculate daily total XP
        daily_total = self.df.groupby('date')['xp_numeric'].sum().reset_index()

        # Merge with dominant course info
        daily_data = pd.merge(daily_total, dominant_course[['date', 'dominant_course']], on='date', how='left')

        # Create complete date range from min to max date
        min_date = daily_data['date'].min()
        max_date = daily_data['date'].max()
        all_dates = pd.date_range(start=min_date, end=max_date, freq='D')

        # Create complete dataframe with all calendar dates
        complete_df = pd.DataFrame({'date': all_dates})

        # Merge with actual data (missing dates get 0 XP and Unknown course)
        daily_data = complete_df.merge(daily_data, on='date', how='left')
        daily_data['xp_numeric'] = daily_data['xp_numeric'].fillna(0)
        daily_data['dominant_course'] = daily_data['dominant_course'].fillna('Unknown')

        return daily_data

    def generate_cumulative_xp_chart(self, output_path: Optional[str] = None, 
                                   interactive: bool = True) -> str:
        """Generate cumulative XP chart.
        
        Args:
            output_path: Output path for the chart file
            interactive: Whether to generate interactive (Plotly) or static (Matplotlib) chart
            
        Returns:
            Path to the generated chart file
        """
        if self.df.empty:
            raise ValueError("No data available for chart generation")
        
        cumulative_df = self._calculate_cumulative_xp()
        
        if output_path is None:
            output_path = self.json_path.parent / "cumulative_xp_chart"
        
        if interactive:
            return self._generate_interactive_cumulative_xp(cumulative_df, output_path)
        else:
            return self._generate_static_cumulative_xp(cumulative_df, output_path)
    
    def _generate_interactive_cumulative_xp(self, df: pd.DataFrame, output_path: str) -> str:
        """Generate interactive cumulative XP chart using Plotly."""
        # Calculate cumulative XP with dominant course colors
        colored_df = self._calculate_cumulative_xp_with_dominant_course()

        fig = go.Figure()

        # Generate colors dynamically for all courses
        colors = self._generate_course_colors()
        # Ensure we have a default color for unknown courses
        colors['Unknown'] = '#2E86AB'

        # Create segments with careful boundary handling to avoid overlap
        if not colored_df.empty:
            fig = go.Figure()

            # Find segments where the dominant course changes
            segments = []
            current_course = colored_df.iloc[0]['dominant_course']
            start_idx = 0

            for i in range(1, len(colored_df)):
                if colored_df.iloc[i]['dominant_course'] != current_course:
                    # Create a segment from start_idx to i-1 (exclude boundary point to avoid overlap)
                    segment = colored_df.iloc[start_idx:i]
                    if not segment.empty:
                        segments.append((segment, current_course))
                    current_course = colored_df.iloc[i]['dominant_course']
                    start_idx = i

            # Add the last segment
            segment = colored_df.iloc[start_idx:]
            if not segment.empty:
                segments.append((segment, current_course))

            # Add each segment with its course color
            for idx, (segment, course) in enumerate(segments):
                color = colors.get(course, colors['Unknown'])

                # Create hover text for each data point
                hover_text = [f'Date: {date.strftime("%Y-%m-%d")}<br>Cumulative XP: {cum_xp}<br>Daily XP: {daily_xp}<br>Main Course: {course}'
                              for date, cum_xp, daily_xp in zip(segment['date'], segment['cumulative_xp'], segment['xp_numeric'])]

                fig.add_trace(go.Scatter(
                    x=segment['date'],
                    y=segment['cumulative_xp'],
                    mode='lines+markers',
                    name=course,
                    line=dict(color=color, width=3),
                    marker=dict(size=6, color=color),
                    hovertext=hover_text,
                    hovertemplate='%{hovertext}<extra></extra>',
                    showlegend=False,
                    hoverinfo='text'
                ))

        # Create a custom legend showing course colors in appearance order
        legend_items = []
        course_order = self._get_course_appearance_order()

        # Filter to only courses that appear as dominant courses, in appearance order
        for course in course_order:
            if course in colored_df['dominant_course'].values and course != 'Unknown':
                color = colors.get(course, colors['Unknown'])
                legend_items.append(f'<span style="color:{color}">●</span> {course}')

        # Update layout
        fig.update_layout(
            title="Cumulative XP Progress",
            xaxis_title="Date",
            yaxis_title="Cumulative XP",
            hovermode='x',  # Back to x-axis based hover
            template='plotly_white',
            showlegend=True,
            height=650,  # Increased height to accommodate legend
            margin=dict(t=100, b=50, l=50, r=50),  # Add more top margin for legend
            xaxis=dict(
                tickformat='%Y-%m-%d',
                tickangle=45
            ),
            legend=dict(
                title="Course",
                orientation="v",
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01,
                bgcolor="rgba(255,255,255,0.9)",
                bordercolor="#CCCCCC",
                borderwidth=1,
                tracegroupgap=5
            )
        )

        # Add a single trace for the legend in appearance order
        if not colored_df.empty:
            # Calculate cumulative XP for each course
            course_cumulative_xp = self._calculate_course_cumulative_xp()

            course_order = self._get_course_appearance_order()
            for course in course_order:
                if course in colored_df['dominant_course'].values and course != 'Unknown':
                    color = colors.get(course, colors['Unknown'])
                    cumulative_xp = course_cumulative_xp.get(course, 0)
                    legend_name = f"{course} ({cumulative_xp:,} XP)"
                    fig.add_trace(go.Scatter(
                        x=[None], y=[None],
                        mode='markers',
                        name=legend_name,
                        marker=dict(color=color, size=10),
                        showlegend=True
                    ))

        # Save as HTML
        output_file = f"{output_path}.html"
        fig.write_html(output_file)

        return output_file
    
    def _generate_static_cumulative_xp(self, df: pd.DataFrame, output_path: str) -> str:
        """Generate static cumulative XP chart using Matplotlib."""
        # Calculate cumulative XP with dominant course colors
        colored_df = self._calculate_cumulative_xp_with_dominant_course()

        plt.figure(figsize=(14, 8))

        # Set style
        plt.style.use('default')

        # Generate colors dynamically for all courses
        colors = self._generate_course_colors()
        # Ensure we have a default color for unknown courses
        colors['Unknown'] = '#2E86AB'

        # Plot colored segments
        if not colored_df.empty:
            # Split the data into segments where the dominant course changes
            segments = []
            current_course = colored_df.iloc[0]['dominant_course']
            start_idx = 0

            for i in range(1, len(colored_df)):
                if colored_df.iloc[i]['dominant_course'] != current_course:
                    # Create a segment from start_idx to i-1
                    segment = colored_df.iloc[start_idx:i]
                    segments.append((segment, current_course))
                    current_course = colored_df.iloc[i]['dominant_course']
                    start_idx = i

            # Add the last segment
            segment = colored_df.iloc[start_idx:]
            segments.append((segment, current_course))

            # Plot each segment with its color
            for segment, course in segments:
                color = colors.get(course, colors['Unknown'])

                plt.plot(segment['date'], segment['cumulative_xp'],
                        marker='o', linewidth=3, markersize=6,
                        color=color, alpha=0.9)

                # Add subtle fill under each segment
                plt.fill_between(segment['date'], segment['cumulative_xp'],
                               alpha=0.2, color=color)

        # Formatting
        plt.title("Cumulative XP Progress",
                 fontsize=16, fontweight='bold')
        plt.xlabel("Date", fontsize=12)
        plt.ylabel("Cumulative XP", fontsize=12)

        # Format x-axis
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        interval = max(1, len(df) // 10)
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=interval))
        plt.xticks(rotation=45)

        # Format y-axis with commas
        plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):,}'))

        # Add grid
        plt.grid(True, alpha=0.3)

        # Create custom legend in appearance order
        legend_elements = []
        course_order = self._get_course_appearance_order()

        # Calculate cumulative XP for each course
        course_cumulative_xp = self._calculate_course_cumulative_xp()

        # Filter to only courses that appear as dominant courses, in appearance order
        for course in course_order:
            if course in colored_df['dominant_course'].values and course != 'Unknown':
                color = colors.get(course, colors['Unknown'])
                cumulative_xp = course_cumulative_xp.get(course, 0)
                label_name = f"{course} ({cumulative_xp:,} XP)"
                legend_elements.append(plt.Line2D([0], [0], color=color, linewidth=3, label=label_name))

        if legend_elements:
            # Place legend inside the plot area in the upper left
            plt.legend(handles=legend_elements, loc='upper left', framealpha=0.95,
                      fancybox=True, shadow=True, fontsize=9)

        # Adjust layout to make room for data
        plt.tight_layout()
        # Adjust left margin slightly to accommodate legend
        plt.subplots_adjust(left=0.15)

        # Save as PNG
        output_file = f"{output_path}.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()

        return output_file
    
    def generate_daily_xp_chart(self, output_path: Optional[str] = None, 
                               interactive: bool = True) -> str:
        """Generate daily XP trend chart.
        
        Args:
            output_path: Output path for the chart file
            interactive: Whether to generate interactive (Plotly) or static (Matplotlib) chart
            
        Returns:
            Path to the generated chart file
        """
        if self.df.empty:
            raise ValueError("No data available for chart generation")
        
        daily_df = self._calculate_daily_xp()
        
        if output_path is None:
            output_path = self.json_path.parent / "daily_xp_chart"
        
        if interactive:
            return self._generate_interactive_daily_xp(daily_df, output_path)
        else:
            return self._generate_static_daily_xp(daily_df, output_path)
    
    def _generate_interactive_daily_xp(self, df: pd.DataFrame, output_path: str) -> str:
        """Generate interactive daily XP chart using Plotly with course-based colors."""
        # Calculate daily XP with dominant course colors
        colored_df = self._calculate_daily_xp_with_dominant_course()
        fig = go.Figure()

        # Generate colors dynamically for all courses
        colors = self._generate_course_colors()
        # Ensure we have a default color for unknown courses
        colors['Unknown'] = '#2E86AB'

        # Create segments for different colors
        if not colored_df.empty:
            # Split the data into segments where the dominant course changes
            segments = []
            current_course = colored_df.iloc[0]['dominant_course']
            start_idx = 0
            for i in range(1, len(colored_df)):
                if colored_df.iloc[i]['dominant_course'] != current_course:
                    # Create a segment from start_idx to i-1
                    segment = colored_df.iloc[start_idx:i]
                    segments.append((segment, current_course))
                    current_course = colored_df.iloc[i]['dominant_course']
                    start_idx = i
            # Add the last segment
            segment = colored_df.iloc[start_idx:]
            segments.append((segment, current_course))

            # Add each segment as a separate trace
        for segment, course in segments:
            color = colors.get(course, colors['Unknown'])
            # Create custom hover text for each data point
            hover_text = []
            for date, daily_xp in zip(segment['date'], segment['xp_numeric']):
                hover_info = f'Main Course: {course}<br>Daily XP: {daily_xp}'
                hover_text.append(hover_info)

            fig.add_trace(go.Bar(
                x=segment['date'],
                y=segment['xp_numeric'],
                name=f'Daily XP ({course})',
                marker_color=color,
                opacity=0.8,
                hovertext=hover_text,
                hovertemplate='%{hovertext}<extra></extra>',
                showlegend=False
            ))

        # Add trend line (7-day moving average) with standard hover for unified mode
        if len(df) >= 7:
            df['trend'] = df['xp_numeric'].rolling(window=7, center=False).mean()
            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['trend'],
                mode='lines',
                name='7-Day Average',
                line=dict(color='#F18F01', width=2),
                hovertemplate='7-Day Avg: %{y:.1f}<extra></extra>'
            ))

        # Create a custom legend showing course colors in appearance order
        legend_items = []
        course_order = self._get_course_appearance_order()
        # Filter to only courses that appear as dominant courses, in appearance order
        for course in course_order:
            if course in colored_df['dominant_course'].values and course != 'Unknown':
                color = colors.get(course, colors['Unknown'])
                # Calculate total XP for this course
                course_total = self.df[self.df['Course'] == course]['xp_numeric'].sum()
                legend_name = f"{course} ({course_total:,} XP)"
                legend_items.append(f'<span style="color:{color}">●</span> {legend_name}')

        # Update layout
        fig.update_layout(
            title="Daily XP Trend by Course",
            xaxis_title="Date",
            yaxis_title="Daily XP",
            hovermode='x unified',
            template='plotly_white',
            showlegend=True,
            height=650,  # Increased height to accommodate legend
            margin=dict(t=100, b=50, l=50, r=50),  # Add more top margin for legend
            xaxis=dict(
                tickformat='%Y-%m-%d',
                tickangle=45
            ),
            yaxis=dict(
                title="Daily XP",
                tickformat=',.0f'
            ),
            legend=dict(
                title="Course (Total XP)",
                orientation="v",
                yanchor="top",
                y=0.99,
                xanchor="right",
                x=0.99,
                bgcolor="rgba(255,255,255,0.9)",
                bordercolor="#CCCCCC",
                borderwidth=1,
                tracegroupgap=5
            )
        )

        # Add course legend traces
        for course in course_order:
            if course in colored_df['dominant_course'].values and course != 'Unknown':
                color = colors.get(course, colors['Unknown'])
                course_total = self.df[self.df['Course'] == course]['xp_numeric'].sum()
                legend_name = f"{course} ({course_total:,} XP)"
                fig.add_trace(go.Scatter(
                    x=[None], y=[None],
                    mode='markers',
                    name=legend_name,
                    marker=dict(color=color, size=10),
                    showlegend=True
                ))

        # Save as HTML
        output_file = f"{output_path}.html"
        fig.write_html(output_file)

        return output_file
    
    def _generate_static_daily_xp(self, df: pd.DataFrame, output_path: str) -> str:
        """Generate static daily XP chart using Matplotlib with course-based colors."""
        # Calculate daily XP with dominant course colors
        colored_df = self._calculate_daily_xp_with_dominant_course()

        plt.figure(figsize=(14, 8))

        # Set style
        plt.style.use('default')

        # Generate colors dynamically for all courses
        colors = self._generate_course_colors()
        # Ensure we have a default color for unknown courses
        colors['Unknown'] = '#2E86AB'

        # Plot colored segments
        if not colored_df.empty:
            # Split the data into segments where the dominant course changes
            segments = []
            current_course = colored_df.iloc[0]['dominant_course']
            start_idx = 0
            for i in range(1, len(colored_df)):
                if colored_df.iloc[i]['dominant_course'] != current_course:
                    # Create a segment from start_idx to i-1
                    segment = colored_df.iloc[start_idx:i]
                    segments.append((segment, current_course))
                    current_course = colored_df.iloc[i]['dominant_course']
                    start_idx = i
            # Add the last segment
            segment = colored_df.iloc[start_idx:]
            segments.append((segment, current_course))

            # Plot each segment with its color
            for segment, course in segments:
                color = colors.get(course, colors['Unknown'])
                plt.bar(segment['date'], segment['xp_numeric'],
                       color=color, alpha=0.8, width=0.8,
                       label=f'{course}')

        # Add trend line (7-day moving average) - use the original df for calculation
        if len(df) >= 7:
            df['trend'] = df['xp_numeric'].rolling(window=7, center=False).mean()
            plt.plot(df['date'], df['trend'],
                    color='#F18F01', linewidth=2,
                    label='7-Day Average', zorder=10)

        # Formatting
        plt.title("Daily XP Trend by Course",
                 fontsize=16, fontweight='bold')
        plt.xlabel("Date", fontsize=12)
        plt.ylabel("Daily XP", fontsize=12)

        # Format x-axis
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        interval = max(1, len(df) // 15)
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=interval))
        plt.xticks(rotation=45)

        # Format y-axis
        plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):,}'))

        # Add grid
        plt.grid(True, alpha=0.3)

        # Create custom legend with course totals
        legend_elements = []
        course_order = self._get_course_appearance_order()
        for course in course_order:
            if course in colored_df['dominant_course'].values and course != 'Unknown':
                color = colors.get(course, colors['Unknown'])
                course_total = self.df[self.df['Course'] == course]['xp_numeric'].sum()
                label_name = f"{course} ({course_total:,} XP)"
                legend_elements.append(plt.Rectangle((0,0), 1, 1, color=color, alpha=0.8, label=label_name))

        # Add 7-day average to legend
        legend_elements.append(plt.Line2D([0], [0], color='#F18F01', linewidth=2, label='7-Day Average'))

        if legend_elements:
            # Check if left area has high bars that would overlap with legend
            left_quarter_date = df['date'].min() + pd.Timedelta(days=len(df) // 4)
            max_left_xp = df[df['date'] <= left_quarter_date]['xp_numeric'].max()
            overall_max_xp = df['xp_numeric'].max()

            # Dynamically choose legend position based on data distribution
            if max_left_xp > overall_max_xp * 0.6:  # If left has tall bars, place legend on right
                legend_loc = 'upper right'
            else:
                legend_loc = 'upper left'

            plt.legend(handles=legend_elements, loc=legend_loc, framealpha=0.95,
                      fancybox=True, shadow=True, fontsize=9)

        # Adjust layout to make room for data
        plt.tight_layout()
        # Adjust left margin slightly to accommodate legend
        plt.subplots_adjust(left=0.15)

        # Save as PNG
        output_file = f"{output_path}.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()

        return output_file
    
    def generate_combined_xp_dashboard(self, output_path: Optional[str] = None) -> str:
        """Generate combined dashboard with both cumulative and daily XP charts.
        
        Args:
            output_path: Output path for the dashboard file
            
        Returns:
            Path to the generated dashboard file
        """
        if self.df.empty:
            raise ValueError("No data available for dashboard generation")
        
        if output_path is None:
            output_path = self.json_path.parent / "xp_dashboard"
        
        cumulative_df = self._calculate_cumulative_xp()
        daily_df = self._calculate_daily_xp()
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Cumulative XP Progress', 'Daily XP Trend'),
            vertical_spacing=0.12,
            specs=[[{"secondary_y": False}],
                   [{"secondary_y": False}]]
        )
        
        # Add cumulative XP line
        fig.add_trace(
            go.Scatter(
                x=cumulative_df['date'],
                y=cumulative_df['cumulative_xp'],
                mode='lines+markers',
                name='Cumulative XP',
                line=dict(color='#2E86AB', width=3),
                marker=dict(size=6)
            ),
            row=1, col=1
        )
        
        # Add daily XP bars
        fig.add_trace(
            go.Bar(
                x=daily_df['date'],
                y=daily_df['xp_numeric'],
                name='Daily XP',
                marker_color='#A23B72',
                opacity=0.8
            ),
            row=2, col=1
        )
        
        # Add 7-day trend line to daily chart
        if len(daily_df) >= 7:
            daily_df['trend'] = daily_df['xp_numeric'].rolling(window=7, center=False).mean()
            fig.add_trace(
                go.Scatter(
                    x=daily_df['date'],
                    y=daily_df['trend'],
                    mode='lines',
                    name='7-Day Average',
                    line=dict(color='#F18F01', width=2)
                ),
                row=2, col=1
            )
        
        # Update layout
        fig.update_layout(
            title="Learning Progress Dashboard",
            template='plotly_white',
            showlegend=True,
            height=800,
            hovermode='x unified'
        )
        
        # Update x-axes
        fig.update_xaxes(
            tickformat='%Y-%m-%d',
            tickangle=45,
            row=1, col=1
        )
        fig.update_xaxes(
            tickformat='%Y-%m-%d',
            tickangle=45,
            row=2, col=1
        )
        
        # Update y-axes
        fig.update_yaxes(title_text="Cumulative XP", row=1, col=1)
        fig.update_yaxes(title_text="Daily XP", row=2, col=1)
        
        # Save as HTML
        output_file = f"{output_path}.html"
        fig.write_html(output_file)
        
        return output_file
    
    def generate_task_type_pie_chart(self, output_path: Optional[str] = None, 
                                    interactive: bool = True) -> str:
        """Generate task type distribution pie chart.
        
        Args:
            output_path: Output path for the chart file
            interactive: Whether to generate interactive (Plotly) or static (Matplotlib) chart
            
        Returns:
            Path to the generated chart file
        """
        if self.df.empty:
            raise ValueError("No data available for chart generation")
        
        task_distribution = self._calculate_task_type_distribution()
        
        if output_path is None:
            output_path = self.json_path.parent / "task_type_pie_chart"
        
        if interactive:
            return self._generate_interactive_task_type_pie(task_distribution, output_path)
        else:
            return self._generate_static_task_type_pie(task_distribution, output_path)
    
    def _generate_interactive_task_type_pie(self, df: pd.DataFrame, output_path: str) -> str:
        """Generate interactive task type pie chart using Plotly."""
        # Create subplots
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Task Count Distribution', 'XP Distribution'),
            specs=[[{"type": "pie"}, {"type": "pie"}]]
        )

        # Task count pie chart
        fig.add_trace(go.Pie(
            labels=df['Task Type'],
            values=df['Count'],
            name="Task Count",
            hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Percentage: %{text}%<extra></extra>",
            textinfo='label+percent',
            textposition='inside',
            showlegend=False
        ), row=1, col=1)

        # XP distribution pie chart
        fig.add_trace(go.Pie(
            labels=df['Task Type'],
            values=df['Total XP'],
            name="XP Distribution",
            hovertemplate="<b>%{label}</b><br>Total XP: %{value}<br>Percentage: %{text}%<extra></extra>",
            textinfo='label+percent',
            textposition='inside',
            showlegend=False
        ), row=1, col=2)

        # Update layout
        fig.update_layout(
            title="Task Type Distribution",
            template='plotly_white',
            height=500,
            showlegend=True
        )

        # Save as HTML
        output_file = f"{output_path}.html"
        fig.write_html(output_file)

        return output_file
    
    def _generate_static_task_type_pie(self, df: pd.DataFrame, output_path: str) -> str:
        """Generate static task type pie chart using Matplotlib."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

        # Custom autopct function to hide percentages for items under 5%
        def autopct_filter(pct):
            return ('%1.1f%%' % pct) if pct >= 5.0 else ''

        # Create custom labels: hide labels for items under 3%, show for others
        def create_labels(data, percentages):
            labels = []
            for i, pct in enumerate(percentages):
                if pct >= 3.0:
                    labels.append(data.iloc[i])
                else:
                    labels.append('')
            return labels

        # Calculate percentages for label filtering
        count_percentages = (df['Count'] / df['Count'].sum() * 100).values
        xp_percentages = (df['Total XP'] / df['Total XP'].sum() * 100).values

        # Create filtered labels
        count_labels = create_labels(df['Task Type'], count_percentages)
        xp_labels = create_labels(df['Task Type'], xp_percentages)

        # Task count pie chart (no individual legend)
        ax1.pie(df['Count'], labels=count_labels, autopct=autopct_filter, startangle=90)
        ax1.set_title('Task Count Distribution')

        # XP distribution pie chart (no individual legend)
        ax2.pie(df['Total XP'], labels=xp_labels, autopct=autopct_filter, startangle=90)
        ax2.set_title('XP Distribution')
        
        # Create a shared legend at the bottom
        # Create proxy artists for legend
        from matplotlib.patches import Patch
        legend_elements = [Patch(facecolor=plt.cm.tab10(i), label=task_type)
                          for i, task_type in enumerate(df['Task Type'])]

        # Add legend at the bottom center
        fig.legend(handles=legend_elements, title="Task Types",
                   loc='lower center', bbox_to_anchor=(0.5, -0.05), ncol=len(df['Task Type']))

        # Main title
        fig.suptitle("Task Type Distribution",
                    fontsize=16, fontweight='bold')

        # Adjust layout to make room for bottom legend
        plt.tight_layout()
        plt.subplots_adjust(bottom=0.15)  # Make room for legend at bottom
        
        # Save as PNG
        output_file = f"{output_path}.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_file
    
    def generate_multi_level_stats_chart(self, output_path: Optional[str] = None,
                                      interactive: bool = True) -> str:
        """Generate monthly, weekly and daily XP statistics comparison chart.

        Args:
            output_path: Output path for the chart file
            interactive: Whether to generate interactive (Plotly) or static (Matplotlib) chart

        Returns:
            Path to the generated chart file
        """
        if self.df.empty:
            raise ValueError("No data available for chart generation")

        stats_data = self._calculate_monthly_weekly_daily_stats()

        if output_path is None:
            output_path = self.json_path.parent / "multi_level_stats_chart"

        if interactive:
            return self._generate_interactive_multi_level_stats(stats_data, output_path)
        else:
            return self._generate_static_multi_level_stats(stats_data, output_path)
    
    def _generate_interactive_multi_level_stats(self, stats_data: Dict[str, pd.DataFrame], output_path: str) -> str:
        """Generate interactive monthly/weekly/daily stats chart using Plotly with bar charts and task type differentiation."""
        # Get both regular stats and task type breakdown
        regular_stats = stats_data
        task_type_stats = self._calculate_monthly_weekly_daily_stats_by_task_type()

        # Create subplots with 3 rows and 2 columns
        # Order: Daily (row 1) → Weekly (row 2) → Monthly (row 3)
        # First column: XP by task type (bar), Second column: Task counts by task type (bar)
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=('Daily XP', 'Daily Task Count',
                          'Weekly XP', 'Weekly Task Count',
                          'Monthly XP', 'Monthly Task Count'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )

        # Daily XP by task type (row 1, col 1) - Grouped bar chart
        for task_type, task_data in task_type_stats['daily'].items():
            df = task_data['data']
            fig.add_trace(go.Bar(
                x=df['Date'],
                y=df['Total XP'],
                name=f'{task_type}',
                marker_color=task_data['color'],
                opacity=0.8,
                showlegend=True
            ), row=1, col=1)

        # Daily task count by task type (row 1, col 2) - Grouped bar chart
        for task_type, task_data in task_type_stats['daily'].items():
            df = task_data['data']
            fig.add_trace(go.Bar(
                x=df['Date'],
                y=df['Task Count'],
                name=f'{task_type} Tasks',
                marker_color=task_data['color'],
                opacity=0.8,
                showlegend=False  # Hide duplicate legend
            ), row=1, col=2)

        # Weekly XP by task type (row 2, col 1) - Grouped bar chart
        for task_type, task_data in task_type_stats['weekly'].items():
            df = task_data['data']
            fig.add_trace(go.Bar(
                x=df['Week Start'],
                y=df['Total XP'],
                name=f'{task_type} XP',
                marker_color=task_data['color'],
                opacity=0.8,
                showlegend=False  # Hide duplicate legend
            ), row=2, col=1)

        # Weekly task count by task type (row 2, col 2) - Grouped bar chart
        for task_type, task_data in task_type_stats['weekly'].items():
            df = task_data['data']
            fig.add_trace(go.Bar(
                x=df['Week Start'],
                y=df['Task Count'],
                name=f'{task_type} Tasks',
                marker_color=task_data['color'],
                opacity=0.8,
                showlegend=False  # Hide duplicate legend
            ), row=2, col=2)

        # Monthly XP by task type (row 3, col 1) - Grouped bar chart
        for task_type, task_data in task_type_stats['monthly'].items():
            df = task_data['data']
            fig.add_trace(go.Bar(
                x=df['Month Start'],
                y=df['Total XP'],
                name=f'{task_type} XP',
                marker_color=task_data['color'],
                opacity=0.8,
                showlegend=False  # Hide duplicate legend
            ), row=3, col=1)

        # Monthly task count by task type (row 3, col 2) - Grouped bar chart
        for task_type, task_data in task_type_stats['monthly'].items():
            df = task_data['data']
            fig.add_trace(go.Bar(
                x=df['Month Start'],
                y=df['Task Count'],
                name=f'{task_type} Tasks',
                marker_color=task_data['color'],
                opacity=0.8,
                showlegend=False  # Hide duplicate legend
            ), row=3, col=2)

        # Update layout
        fig.update_layout(
            title="Monthly, Weekly & Daily Learning Statistics",
            template='plotly_white',
            height=1200,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.05,  # Position legend below the chart
                xanchor="center",
                x=0.5,
                itemclick=False,  # Disable click events
                itemdoubleclick=False  # Disable double-click events
            ),
            barmode='stack'  # Stack bars for each time period
        )

        # Update x-axes
        fig.update_xaxes(title_text="Date", row=1, col=1)
        fig.update_xaxes(title_text="Date", row=1, col=2)
        fig.update_xaxes(title_text="Week", row=2, col=1)
        fig.update_xaxes(title_text="Week", row=2, col=2)
        fig.update_xaxes(title_text="Month", row=3, col=1)
        fig.update_xaxes(title_text="Month", row=3, col=2)

        # Update y-axes
        fig.update_yaxes(title_text="XP", row=1, col=1)
        fig.update_yaxes(title_text="Task Count", row=1, col=2)
        fig.update_yaxes(title_text="XP", row=2, col=1)
        fig.update_yaxes(title_text="Task Count", row=2, col=2)
        fig.update_yaxes(title_text="XP", row=3, col=1)
        fig.update_yaxes(title_text="Task Count", row=3, col=2)

        # Save as HTML
        output_file = f"{output_path}.html"
        fig.write_html(output_file)

        return output_file

    def _generate_static_multi_level_stats(self, stats_data: Dict[str, pd.DataFrame], output_path: str) -> str:
        """Generate static monthly/weekly/daily stats chart using Matplotlib with bar charts and task type differentiation."""
        # Get task type breakdown
        task_type_stats = self._calculate_monthly_weekly_daily_stats_by_task_type()

        # Create subplots with 3 rows and 2 columns
        fig, axes = plt.subplots(3, 2, figsize=(18, 16))

        # Helper function to plot stacked bars
        def plot_stacked_bars(ax, data_dict, title, x_label, y_label, value_column):
            """Plot stacked bar chart for multiple task types."""
            # Get all unique dates and sort them
            all_dates = set()
            for task_data in data_dict.values():
                all_dates.update(task_data['data']['Date' if 'Date' in task_data['data'].columns else
                                                    'Week Start' if 'Week Start' in task_data['data'].columns else 'Month Start'])

            # For daily data, create complete date range
            if 'Date' in next(iter(data_dict.values()))['data'].columns:
                min_date = min(all_dates)
                max_date = max(all_dates)
                all_dates = pd.date_range(start=min_date, end=max_date, freq='D')
            else:
                all_dates = sorted(list(all_dates))

            # Prepare data for stacking
            bottom_values = [0] * len(all_dates)

            for task_type, task_data in data_dict.items():
                df = task_data['data']
                color = task_data['color']

                # Align data with all dates
                y_values = []
                for date in all_dates:
                    if 'Date' in df.columns:
                        matching = df[df['Date'] == date]
                    elif 'Week Start' in df.columns:
                        matching = df[df['Week Start'] == date]
                    else:
                        matching = df[df['Month Start'] == date]

                    if not matching.empty:
                        y_values.append(matching[value_column].iloc[0])
                    else:
                        y_values.append(0)

                # Plot stacked bars
                positions = list(range(len(all_dates)))
                ax.bar(positions, y_values, bottom=bottom_values, label=task_type,
                      color=color, alpha=0.8, width=0.8)

                # Update bottom values for next stack
                for i in range(len(bottom_values)):
                    bottom_values[i] += y_values[i]

            # Format date labels - ensure uniform spacing and avoid overlap
            if all_dates is not None and len(all_dates) > 0 and hasattr(all_dates[0], 'day'):
                # Calculate optimal interval to show max 8-10 labels uniformly
                max_labels = 8
                interval = max(1, len(all_dates) // max_labels)

                if len(all_dates) <= 15:
                    # Small datasets - show all dates
                    date_labels = [d.strftime('%m/%d') for d in all_dates]
                    tick_positions = positions
                else:
                    # Medium to large datasets - show uniformly spaced dates
                    date_labels = []
                    tick_positions = []

                    # Always show the first date
                    date_labels.append(all_dates[0].strftime('%m/%d'))
                    tick_positions.append(0)

                    # Show uniformly spaced dates in between
                    for i in range(1, len(all_dates) - 1):
                        if i % interval == 0:
                            date_labels.append(all_dates[i].strftime('%m/%d'))
                            tick_positions.append(i)

                    # Always show the last date
                    if len(all_dates) > 1:
                        date_labels.append(all_dates[-1].strftime('%m/%d'))
                        tick_positions.append(len(all_dates) - 1)

            else:
                # Weekly dates
                date_labels = [d.strftime('%m/%d') for d in all_dates]
                tick_positions = positions

            ax.set_xticks(tick_positions)
            ax.set_xticklabels(date_labels, rotation=45)

            # Set labels and title
            ax.set_xlabel(x_label)
            ax.set_ylabel(y_label)
            ax.set_title(title, fontsize=14, fontweight='bold')
            # Remove individual legends - we'll create a shared one at the bottom
            ax.grid(True, alpha=0.3)

        # Daily XP by task type (row 1, col 1)
        plot_stacked_bars(axes[0, 0], task_type_stats['daily'],
                         'Daily XP', 'Date', 'XP', 'Total XP')

        # Daily task count by task type (row 1, col 2)
        plot_stacked_bars(axes[0, 1], task_type_stats['daily'],
                         'Daily Task Count', 'Date', 'Task Count', 'Task Count')

        # Weekly XP by task type (row 2, col 1)
        plot_stacked_bars(axes[1, 0], task_type_stats['weekly'],
                         'Weekly XP', 'Week', 'XP', 'Total XP')

        # Weekly task count by task type (row 2, col 2)
        plot_stacked_bars(axes[1, 1], task_type_stats['weekly'],
                         'Weekly Task Count', 'Week', 'Task Count', 'Task Count')

        # Monthly XP by task type (row 3, col 1)
        plot_stacked_bars(axes[2, 0], task_type_stats['monthly'],
                         'Monthly XP', 'Month', 'XP', 'Total XP')

        # Monthly task count by task type (row 3, col 2)
        plot_stacked_bars(axes[2, 1], task_type_stats['monthly'],
                         'Monthly Task Count', 'Month', 'Task Count', 'Task Count')

        # Main title
        fig.suptitle("Monthly, Weekly & Daily Learning Statistics",
                    fontsize=18, fontweight='bold', y=0.98)

        # Create a shared legend at the bottom
        # Create proxy artists for legend using the same colors as in the data
        from matplotlib.patches import Patch
        task_types = list(task_type_stats['daily'].keys())
        colors = [task_type_stats['daily'][task_type]['color'] for task_type in task_types]
        legend_elements = [Patch(facecolor=color, label=task_type)
                          for task_type, color in zip(task_types, colors)]

        # Add legend at the bottom center
        fig.legend(handles=legend_elements, title="Task Types",
                   loc='lower center', bbox_to_anchor=(0.5, -0.02), ncol=len(task_types),
                   fontsize=12, title_fontsize=14)

        # Adjust layout to make room for bottom legend
        plt.tight_layout(rect=[0, 0.05, 1, 0.96])
        plt.subplots_adjust(bottom=0.1)  # Make room for legend at bottom

        # Save as PNG
        output_file = f"{output_path}.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()

        return output_file

    def generate_efficiency_trend_chart(self, output_path: Optional[str] = None,
                                     interactive: bool = True) -> str:
        """Generate learning efficiency trend chart.
        
        Args:
            output_path: Output path for the chart file
            interactive: Whether to generate interactive (Plotly) or static (Matplotlib) chart
            
        Returns:
            Path to the generated chart file
        """
        if self.df.empty:
            raise ValueError("No data available for chart generation")
        
        efficiency_df = self._calculate_efficiency_trend()
        
        if output_path is None:
            output_path = self.json_path.parent / "efficiency_trend_chart"
        
        if interactive:
            return self._generate_interactive_efficiency_trend(efficiency_df, output_path)
        else:
            return self._generate_static_efficiency_trend(efficiency_df, output_path)
    
    def _generate_interactive_efficiency_trend(self, df: pd.DataFrame, output_path: str) -> str:
        """Generate interactive efficiency trend chart using Plotly."""
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Daily Efficiency Rate', 'XP Earned vs Possible'),
            vertical_spacing=0.12,
            specs=[[{"secondary_y": False}],
                   [{"secondary_y": False}]]
        )

        # Efficiency rate line
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['Efficiency Rate'],
            mode='lines+markers',
            name='Daily Efficiency',
            line=dict(color='#2E86AB', width=2),
            marker=dict(size=4),
            hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Efficiency: %{y:.1f}%<extra></extra>'
        ), row=1, col=1)

        # 7-day average efficiency
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['7-Day Avg Efficiency'],
            mode='lines',
            name='7-Day Average',
            line=dict(color='#F18F01', width=3),
            hovertemplate='<b>%{x|%Y-%m-%d}</b><br>7-Day Avg: %{y:.1f}%<extra></extra>'
        ), row=1, col=1)

        # XP comparison on single Y-axis
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['Earned XP'],
            mode='lines+markers',
            name='Earned XP',
            line=dict(color='#2E86AB', width=2),
            marker=dict(size=4),
            showlegend=False
        ), row=2, col=1)

        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['Possible XP'],
            mode='lines+markers',
            name='Possible XP',
            line=dict(color='#A23B72', width=2, dash='dash'),
            marker=dict(size=4),
            showlegend=False
        ), row=2, col=1)

        # Add 100% efficiency reference line
        fig.add_hline(y=100, line_dash="dash", line_color="gray",
                      annotation_text="100% Efficiency", row=1, col=1)

        # Update layout
        fig.update_layout(
            title="Learning Efficiency Trend",
            template='plotly_white',
            height=800,
            showlegend=True,
            hovermode='x unified'
        )

        # Update x-axes
        fig.update_xaxes(title_text="Date", row=1, col=1)
        fig.update_xaxes(title_text="Date", row=2, col=1)

        # Update y-axes (single Y-axis for XP comparison)
        fig.update_yaxes(title_text="Efficiency Rate (%)", row=1, col=1)
        fig.update_yaxes(title_text="XP", row=2, col=1)

        # Save as HTML
        output_file = f"{output_path}.html"
        fig.write_html(output_file)

        return output_file
    
    def _generate_static_efficiency_trend(self, df: pd.DataFrame, output_path: str) -> str:
        """Generate static efficiency trend chart using Matplotlib."""
        fig, axes = plt.subplots(2, 1, figsize=(14, 10))

        # Efficiency rate
        axes[0].plot(df['date'], df['Efficiency Rate'],
                    marker='o', linewidth=2, markersize=4,
                    color='#2E86AB', label='Daily Efficiency')
        axes[0].plot(df['date'], df['7-Day Avg Efficiency'],
                    linewidth=3, color='#F18F01', label='7-Day Average')
        axes[0].axhline(y=100, color='gray', linestyle='--', alpha=0.7, label='100% Efficiency')
        axes[0].set_title('Learning Efficiency Rate')
        axes[0].set_xlabel('Date')
        axes[0].set_ylabel('Efficiency Rate (%)')
        axes[0].legend()
        axes[0].tick_params(axis='x', rotation=45)
        axes[0].grid(True, alpha=0.3)

        # XP comparison on single Y-axis
        axes[1].plot(df['date'], df['Earned XP'],
                    marker='o', linewidth=2, markersize=4,
                    color='#2E86AB', label='Earned XP')
        axes[1].plot(df['date'], df['Possible XP'],
                    linewidth=2, linestyle='--',
                    color='#A23B72', label='Possible XP')
        axes[1].set_title('XP Earned vs Possible')
        axes[1].set_xlabel('Date')
        axes[1].set_ylabel('XP')
        axes[1].legend()
        axes[1].tick_params(axis='x', rotation=45)
        axes[1].grid(True, alpha=0.3)

        # Main title
        fig.suptitle("Learning Efficiency Trend",
                    fontsize=16, fontweight='bold')

        # Adjust layout
        plt.tight_layout()

        # Save as PNG
        output_file = f"{output_path}.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()

        return output_file
    
    def generate_weekday_distribution_chart(self, output_path: Optional[str] = None, 
                                            interactive: bool = True) -> str:
        """Generate weekday XP distribution chart.
        
        Args:
            output_path: Output path for the chart file
            interactive: Whether to generate interactive (Plotly) or static (Matplotlib) chart
            
        Returns:
            Path to the generated chart file
        """
        if self.df.empty:
            raise ValueError("No data available for chart generation")
        
        weekday_df = self._calculate_weekday_distribution()
        
        if output_path is None:
            output_path = self.json_path.parent / "weekday_distribution"
        
        if interactive:
            return self._generate_interactive_weekday_distribution(weekday_df, output_path)
        else:
            return self._generate_static_weekday_distribution(weekday_df, output_path)
    
    def _generate_interactive_weekday_distribution(self, df: pd.DataFrame, output_path: str) -> str:
        """Generate interactive weekday distribution chart using Plotly."""
        fig = go.Figure()

        # Average Daily XP by weekday
        fig.add_trace(go.Bar(
            x=df['Weekday'],
            y=df['Average Daily XP'],
            name='Average Daily XP',
            marker_color='#F18F01',
            hovertemplate='<b>%{x}</b><br>Average Daily XP: %{y:.1f}<extra></extra>'
        ))

        # Update layout
        fig.update_layout(
            title="Average Daily XP by Weekday",
            template='plotly_white',
            height=500,
            showlegend=False,
            xaxis_title="Weekday",
            yaxis_title="Average Daily XP"
        )
        
        # Save as HTML
        output_file = f"{output_path}.html"
        fig.write_html(output_file)
        return output_file
    
    def _generate_static_weekday_distribution(self, df: pd.DataFrame, output_path: str) -> str:
        """Generate static weekday distribution chart using Matplotlib."""
        fig, ax = plt.subplots(figsize=(12, 6))

        # Average Daily XP by weekday
        bars = ax.bar(df['Weekday'], df['Average Daily XP'], color='#F18F01', alpha=0.8)
        ax.set_title("Average Daily XP by Weekday",
                    fontsize=16, fontweight='bold')
        ax.set_ylabel('Average Daily XP')
        ax.set_xlabel('Weekday')
        ax.tick_params(axis='x', rotation=45)
        ax.grid(True, alpha=0.3)

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}', ha='center', va='bottom')

        # Adjust layout
        plt.tight_layout()

        # Save as PNG
        output_file = f"{output_path}.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()

        return output_file
    
    def generate_daily_xp_distribution_chart(self, output_path: Optional[str] = None, 
                                           interactive: bool = True) -> str:
        """Generate daily XP distribution chart (histogram of daily XP counts).
        
        Args:
            output_path: Output path for the chart file
            interactive: Whether to generate interactive (Plotly) or static (Matplotlib) chart
            
        Returns:
            Path to the generated chart file
        """
        if self.df.empty:
            raise ValueError("No data available for chart generation")
        
        distribution_data, stats = self._calculate_daily_xp_distribution()
        
        if output_path is None:
            output_path = self.json_path.parent / "daily_xp_distribution"
        
        if interactive:
            return self._generate_interactive_daily_xp_distribution(distribution_data, stats, output_path)
        else:
            return self._generate_static_daily_xp_distribution(distribution_data, stats, output_path)
    
    def _generate_interactive_daily_xp_distribution(self, df: pd.DataFrame, stats: dict, output_path: str) -> str:
        """Generate interactive daily XP distribution chart using Plotly."""
        fig = go.Figure()

        # Create histogram bars
        fig.add_trace(go.Bar(
            x=df['Range Label'],
            y=df['Day Count'],
            name='Day Count',
            marker_color='#2E86AB',
            hovertemplate='<b>%{x}</b><br>Days: %{y}<extra></extra>'
        ))

        # Create annotations for mean and median instead of vertical lines
        # This works better with categorical x-axis
        annotations = []

        # Find which XP range contains the mean
        mean_range_idx = self._find_xp_range_for_value(stats['mean_daily_xp'], df)
        if mean_range_idx is not None:
            mean_count = df.loc[mean_range_idx, 'Day Count']
            annotations.append(
                go.layout.Annotation(
                    x=mean_range_idx,
                    y=mean_count * 1.1,
                    text=f"Mean: {stats['mean_daily_xp']:.1f}",
                    showarrow=True,
                    arrowhead=2,
                    arrowsize=1,
                    arrowwidth=2,
                    arrowcolor="red",
                    ax=0,
                    ay=-30,
                    bordercolor="red",
                    borderwidth=2,
                    bgcolor="white"
                )
            )

        # Find which XP range contains the median
        median_range_idx = self._find_xp_range_for_value(stats['median_daily_xp'], df)
        if median_range_idx is not None:
            median_count = df.loc[median_range_idx, 'Day Count']
            annotations.append(
                go.layout.Annotation(
                    x=median_range_idx,
                    y=median_count * 1.2,
                    text=f"Median: {stats['median_daily_xp']:.1f}",
                    showarrow=True,
                    arrowhead=2,
                    arrowsize=1,
                    arrowwidth=2,
                    arrowcolor="orange",
                    ax=0,
                    ay=-30,
                    bordercolor="orange",
                    borderwidth=2,
                    bgcolor="white"
                )
            )

        # Update layout
        fig.update_layout(
            title=f"Daily XP Distribution<br>"
                  f"<sub>Mean: {stats['mean_daily_xp']:.1f} XP, Median: {stats['median_daily_xp']:.1f} XP, "
                  f"Range: {stats['min_daily_xp']:.0f}-{stats['max_daily_xp']:.0f} XP</sub>",
            template='plotly_white',
            height=500,
            showlegend=False,
            xaxis_title="Daily XP Range",
            yaxis_title="Number of Days",
            annotations=annotations
        )

        # Save as HTML
        output_file = f"{output_path}.html"
        fig.write_html(output_file)
        return output_file

    def _find_xp_range_for_value(self, value: float, df: pd.DataFrame) -> Optional[int]:
        """Find which XP range contains the given value. Returns the index in the DataFrame."""
        for idx, range_val in enumerate(df['XP Range']):
            if range_val.left <= value <= range_val.right:
                return idx
        return None
    
    def _generate_static_daily_xp_distribution(self, df: pd.DataFrame, stats: dict, output_path: str) -> str:
        """Generate static daily XP distribution chart using Matplotlib."""
        fig, ax = plt.subplots(figsize=(12, 6))

        # Create histogram bars
        bars = ax.bar(df['Range Label'], df['Day Count'], color='#2E86AB', alpha=0.8)
        ax.set_ylabel('Number of Days')
        ax.set_xlabel('Daily XP Range')
        ax.tick_params(axis='x', rotation=45)
        ax.grid(True, alpha=0.3)

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}', ha='center', va='bottom')

        # Removed Mean and Median annotations to keep the chart clean

        # Main title with statistics in smaller font
        fig.suptitle("Daily XP Distribution", fontsize=14, fontweight='bold', y=0.98)

        # Add statistics subtitle with smaller font
        fig.text(0.5, 0.92,
                f"Mean: {stats['mean_daily_xp']:.1f} XP, Median: {stats['median_daily_xp']:.1f} XP, "
                f"Range: {stats['min_daily_xp']:.0f}-{stats['max_daily_xp']:.0f} XP",
                ha='center', va='top', fontsize=10, style='italic')

        # Adjust layout - need more space for longer title
        plt.tight_layout()
        plt.subplots_adjust(top=0.85)

        # Save as PNG
        output_file = f"{output_path}.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()

        return output_file
    
    def generate_comprehensive_dashboard(self, output_path: Optional[str] = None) -> str:
        """Generate simplified dashboard with Performance Summary only.

        Args:
            output_path: Output path for the dashboard file

        Returns:
            Path to the generated dashboard file
        """
        if self.df.empty:
            raise ValueError("No data available for chart generation")

        if output_path is None:
            output_path = self.json_path.parent / "comprehensive_dashboard"

        return self._generate_comprehensive_dashboard_html(
            self.get_xp_statistics(), output_path
        )
    
    def _generate_comprehensive_dashboard_html(self, stats: dict, output_path: str) -> str:
        """Generate simplified dashboard HTML with Performance Summary and Learning Heatmap."""

        # Calculate heatmap data
        heatmap_data = self._calculate_learning_heatmap_data()

        # Save as HTML
        output_file = f"{output_path}.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Math Academy Learning Dashboard</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                    padding: 20px;
                    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                    color: white;
                    border-radius: 10px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 2.5em;
                    font-weight: 300;
                }}
                .header p {{
                    margin: 10px 0 0 0;
                    font-size: 1.1em;
                    opacity: 0.9;
                }}
                .chart-container {{
                    background: white;
                    margin: 20px 0;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .chart-title {{
                    font-size: 1.4em;
                    color: #333;
                    margin-bottom: 15px;
                    border-bottom: 2px solid #667eea;
                    padding-bottom: 10px;
                }}
                .stats-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 15px;
                    margin-bottom: 20px;
                }}
                .stat-card {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 20px;
                    border-radius: 8px;
                    text-align: center;
                }}
                .stat-value {{
                    font-size: 2em;
                    font-weight: bold;
                    margin: 0;
                }}
                .stat-label {{
                    font-size: 0.9em;
                    opacity: 0.9;
                    margin: 5px 0 0 0;
                }}
                .heatmap-container {{
                    background: white;
                    margin: 20px 0;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    text-align: center;
                }}
                .heatmap-title {{
                    font-size: 1.4em;
                    color: #333;
                    margin-bottom: 15px;
                    border-bottom: 2px solid #667eea;
                    padding-bottom: 10px;
                }}
                .heatmap-wrapper {{
                    overflow-x: auto;
                    margin-bottom: 20px;
                    display: inline-block;
                }}
                .heatmap-grid {{
                    display: grid;
                    grid-template-columns: 30px repeat(53, 15px);
                    gap: 3px;
                    font-size: 12px;
                    min-width: 850px;
                }}
                .weekday-label {{
                    display: flex;
                    align-items: center;
                    justify-content: flex-end;
                    padding-right: 8px;
                    font-weight: 400;
                    color: #586069;
                    font-size: 10px;
                    line-height: 15px;
                    text-transform: none;
                }}
                .month-label {{
                    grid-column: 2 / -1;
                    display: flex;
                    align-items: center;
                    font-weight: 500;
                    color: #586069;
                    font-size: 11px;
                    margin-bottom: 5px;
                    margin-top: 10px;
                }}
                .heatmap-day {{
                    width: 15px;
                    height: 15px;
                    border-radius: 3px;
                    cursor: pointer;
                    transition: transform 0.1s ease;
                    position: relative;
                }}
                .heatmap-day:hover {{
                    transform: scale(1.2);
                    z-index: 10;
                }}
                .heatmap-legend {{
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 10px;
                    margin-top: 15px;
                    font-size: 11px;
                    color: #586069;
                }}
                .legend-item {{
                    display: flex;
                    align-items: center;
                    gap: 5px;
                }}
                .legend-box {{
                    width: 15px;
                    height: 15px;
                    border-radius: 3px;
                }}
                .tooltip {{
                    position: absolute;
                    background: rgba(0, 0, 0, 0.8);
                    color: white;
                    padding: 8px 12px;
                    border-radius: 6px;
                    font-size: 12px;
                    pointer-events: none;
                    z-index: 1000;
                    display: none;
                    white-space: nowrap;
                }}
                @media (max-width: 768px) {{
                    .stats-grid {{
                        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                    }}
                      .heatmap-day {{
                        width: 12px;
                        height: 12px;
                    }}
                    .weekday-label {{
                        font-size: 9px;
                        line-height: 12px;
                    }}
                    .month-label {{
                        font-size: 10px;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Math Academy Learning Dashboard</h1>
                <p>Learning Progress & Performance Analytics</p>
            </div>

            {self._generate_stats_summary_html(stats)}

            {self._generate_learning_heatmap_html(heatmap_data)}

            <div style="text-align: center; margin-top: 40px; padding: 20px; color: #666;">
                <p>Generated by <a href="https://github.com/xmonkey/MathAcademyLogAnalyzer/" target="_blank" style="color: #667eea; text-decoration: none;">MathAcademyLogAnalyzer</a> on {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>

            <div class="tooltip" id="tooltip"></div>
        </body>
        </html>
        """)

        return output_file

    def _generate_learning_heatmap_html(self, heatmap_data: dict) -> str:
        """Generate learning heatmap HTML similar to GitHub contribution graph."""
        if not heatmap_data or not heatmap_data.get('data'):
            return ""

        data = heatmap_data['data']
        color_levels = heatmap_data['color_levels']
        stats = heatmap_data['stats']

        # Convert data to DataFrame for easier manipulation
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])

        # GitHub-style: weeks as columns, days of week as rows
        # Create week groups (53 weeks in a year) with Sunday-starting weeks
        df['weekday_num'] = df['date'].dt.weekday  # Monday=0, Sunday=6
        df['iso_week'] = df['date'].dt.isocalendar().week
        df['iso_year'] = df['date'].dt.isocalendar().year

        # Calculate GitHub-style week (Sunday-starting)
        # For GitHub, week changes on Sunday, not Monday
        # If it's Sunday, it belongs to the next GitHub week
        github_week_adjustment = ((df['weekday_num'] + 1) % 7)  # Sunday=6 -> 0, Monday=0 -> 1, etc.
        df['github_week'] = df['iso_week'] + github_week_adjustment

        # Handle year transition when Sunday pushes to next year's week 1
        year_adjustment = ((df['iso_week'] + github_week_adjustment - 1) // 52)  # Number of 52-week blocks
        df['github_year'] = df['iso_year'] + year_adjustment

        df['year_week'] = df['github_year'].astype(str) + '-' + df['github_week'].astype(str).str.zfill(2)

        # Get all unique weeks in chronological order (fixed 53 weeks layout)
        # Make sure current week is the last one
        all_weeks = sorted(df['year_week'].unique())

        # Get current week to ensure it's included and positioned at the end
        current_date = datetime.now()
        current_year_week = f"{current_date.year}-{current_date.isocalendar().week:02d}"

        # Ensure current week is in the list (even if no data)
        if current_year_week not in all_weeks:
            all_weeks.append(current_year_week)

        # Take last 53 weeks, ensuring current week is the last one
        weeks = all_weeks[-53:]  # Last 53 weeks with current week at the end

        # **CRITICAL FIX**:
        # Sort weeks by actual date to ensure chronological order from left to right
        # This fixes the main issue where dates weren't in time order
        week_dates = []
        for week in weeks:
            week_data = df[df['year_week'] == week]
            if not week_data.empty:
                week_dates.append((week, week_data.iloc[0]['date']))

        # Sort by actual date to ensure proper chronological order
        week_dates.sort(key=lambda x: x[1])  # Sort by date

        # **INTEGRATION FIX**:
        # Replace the original weeks array with the chronologically sorted weeks
        weeks = [week for week, _ in week_dates]

        # Get weekday order starting from Sunday (GitHub style)
        weekday_order = [6, 0, 1, 2, 3, 4, 5]  # Sun, Mon, Tue, Wed, Thu, Fri, Sat
        # Remove all weekday labels - completely empty
        weekday_names = ['', '', '', '', '', '', '']

        # Build month labels (span multiple weeks)
        month_labels = []
        current_month = None
        week_start_index = 0

        for i, week in enumerate(weeks):
            if not df[df['year_week'] == week].empty:
                week_data = df[df['year_week'] == week].iloc[0]
                week_date = week_data['date']
                month_name = week_data['month_name']

                if month_name != current_month:
                    if current_month is not None:
                        # Add previous month label with span
                        span = i - week_start_index
                        month_labels.append({
                            'month': current_month,
                            'span': span,
                            'start_index': week_start_index,
                            'end_index': i - 1
                        })

                    current_month = month_name
                    week_start_index = i

        # Add last month
        if current_month is not None:
            span = len(weeks) - week_start_index
            month_labels.append({
                'month': current_month,
                'span': span,
                'start_index': week_start_index,
                'end_index': len(weeks) - 1
            })

        # Build the HTML structure row by row
        heatmap_html = []

        # Row 1: Empty corner cell + Month labels
        heatmap_html.append('<div></div>')  # Empty corner cell
        for label in month_labels:
            # Grid column calculation: start_index + 2 (empty corner + first data column starts at column 2)
            grid_col = label['start_index'] + 2
            grid_span = label['span']
            heatmap_html.append(f'''
            <div class="month-label" style="grid-column: {grid_col} / span {grid_span};">{label['month']}</div>
            ''')

        # Create a proper GitHub-style grid: 53 weeks × 7 days = 371 cells max
        # We need to build the grid week by week, not weekday by weekday

        # First, create a mapping of (week_index, weekday) -> data
        week_index_map = {week: i for i, week in enumerate(weeks)}

        # Build the data grid: week_index × weekday
        data_grid = {}
        for _, row in df.iterrows():
            week = row['year_week']
            weekday = row['weekday_num']
            if week in week_index_map:
                week_idx = week_index_map[week]
                data_grid[(week_idx, weekday)] = row

        # **CHRONOLOGICAL GRID FIX**:
        # Build a proper chronological grid that dates progress from left to right
        # Create a complete date sequence for the grid

        # **DATE RANGE FIX**: Use a standard 365-day range ending at current date
        # This ensures the heatmap shows the expected time window (e.g., from Oct 2024 to Oct 2025)
        max_date = self.df['date'].max()  # Use latest date in data as end point

        # Create exactly 365 days of data (standard GitHub contribution graph)
        grid_end_date = max_date
        grid_start_date = max_date - pd.Timedelta(days=364)  # 365 days inclusive

        # **WEEK ALIGNMENT FIX**: Ensure the grid starts on a Sunday and ends on a Saturday
        # Find the Sunday before our start date to ensure proper week alignment
        days_since_sunday = (grid_start_date.weekday() + 1) % 7  # Monday=0 -> 1, Sunday=6 -> 0
        aligned_start_date = grid_start_date - pd.Timedelta(days=days_since_sunday)

        # Find the Saturday after our end date to complete the last week
        days_until_saturday = (5 - grid_end_date.weekday()) % 7  # Friday=4 -> 1, Saturday=5 -> 0
        aligned_end_date = grid_end_date + pd.Timedelta(days=days_until_saturday)

        # Create complete date range with proper week alignment
        grid_dates = pd.date_range(start=aligned_start_date, end=aligned_end_date, freq='D')

        print(f"Grid date range: {aligned_start_date.date()} to {aligned_end_date.date()} ({len(grid_dates)} days)")

        # **SIMPLIFIED GRID APPROACH**:
        # Build the grid directly using the chronological date sequence
        # This ensures proper week alignment and fills all cells correctly

        # Convert grid dates to DataFrame for easier lookup
        grid_df = pd.DataFrame({'date': grid_dates})
        grid_df['weekday_num'] = grid_df['date'].dt.weekday  # Monday=0, Sunday=6

        # **KEY FIX**: Build week groups starting from Sunday for proper GitHub-style alignment
        # Find the first Sunday in our grid to serve as week anchor
        first_sunday = None
        for date in grid_dates:
            if date.weekday() == 6:  # Sunday
                first_sunday = date
                break

        if first_sunday is None:
            # If no Sunday found, use the first date and adjust to previous Sunday
            first_sunday = grid_dates[0]
            days_to_sunday = (first_sunday.weekday() + 1) % 7
            first_sunday = first_sunday - pd.Timedelta(days=days_to_sunday)

        print(f"First Sunday anchor: {first_sunday.date()}")

        # **WEEK COLUMN MAPPING**: Map each date to its correct column position
        week_column_map = {}
        current_week_start = first_sunday
        week_col = 0

        # Process dates week by week
        while current_week_start <= grid_dates[-1] and week_col < 53:
            # Define the current week (Sunday to Saturday)
            week_end = current_week_start + pd.Timedelta(days=6)

            # Process each day in this week
            for day_offset in range(7):
                current_date = current_week_start + pd.Timedelta(days=day_offset)
                weekday_idx = current_date.weekday()  # Monday=0, Sunday=6

                # Only add dates that are within our grid range
                if current_date in grid_dates:
                    week_column_map[(week_col, weekday_idx)] = current_date

            # Move to next week
            current_week_start = week_end + pd.Timedelta(days=1)
            week_col += 1

        print(f"Created week column mapping with {len(week_column_map)} date positions")
        print(f"Week columns used: {week_col}")

        # Rows 2-8: Weekday labels + heatmap days (7 rows for Sun-Sat)
        for weekday_idx in weekday_order:
            # Weekday label (completely empty now)
            heatmap_html.append('<div class="weekday-label"></div>')

            # Days for this weekday across all weeks - ensure exactly 53 cells per row
            for week_idx in range(53):  # Fixed 53 weeks for complete grid
                # **SIMPLIFIED APPROACH**: Get the date for this grid position
                grid_date = week_column_map.get((week_idx, weekday_idx))

                if grid_date is not None:
                    # Look for actual data on this date
                    date_data = df[df['date'].dt.date == grid_date.date()]

                    if not date_data.empty:
                        # Use actual data
                        xp = date_data['daily_xp'].iloc[0]
                        color_level = date_data['color_level'].iloc[0]
                        color = color_levels[str(color_level)]

                        # Format date for tooltip
                        date_str = grid_date.strftime('%Y-%m-%d')
                        day_name = grid_date.strftime('%A')
                        tooltip_text = f"{date_str} ({day_name})<br>XP: {int(xp)}"

                        heatmap_html.append(f'''
                        <div class="heatmap-day"
                             style="background-color: {color};"
                             data-date="{date_str}"
                             data-xp="{xp}"
                             onmouseover="showTooltip(event, '{tooltip_text}')"
                             onmouseout="hideTooltip()">
                        </div>
                        ''')
                    else:
                        # No activity data for this date (but date exists in grid)
                        date_str = grid_date.strftime('%Y-%m-%d')
                        day_name = grid_date.strftime('%A')
                        tooltip_text = f"{date_str} ({day_name})<br>XP: 0"

                        heatmap_html.append(f'''
                        <div class="heatmap-day"
                             style="background-color: {color_levels['0']};"
                             data-date="{date_str}"
                             data-xp="0.0"
                             onmouseover="showTooltip(event, '{tooltip_text}')"
                             onmouseout="hideTooltip()">
                        </div>
                        ''')
                else:
                    # Empty cell beyond our date range
                    heatmap_html.append(f'''
                    <div class="heatmap-day"
                         style="background-color: {color_levels['0']};"
                         data-date=""
                         data-xp="0.0"
                         onmouseover="showTooltip(event, 'No data')"
                         onmouseout="hideTooltip()">
                    </div>
                    ''')

        # Combine all parts with fixed 53-week grid template
        heatmap_html_content = f'''
        <div class="heatmap-container">
            <div class="heatmap-title">Learning Activity Heatmap</div>

            <div class="heatmap-wrapper">
                <div class="heatmap-grid">
                    {"".join(heatmap_html)}
                </div>
            </div>

            <div class="heatmap-legend">
                <div class="legend-item">
                    <div class="legend-box" style="background-color: {color_levels['0']};"></div>
                    <span>No activity</span>
                </div>
                <div class="legend-item">
                    <div class="legend-box" style="background-color: {color_levels['1']};"></div>
                    <span>Less than 15 XP</span>
                </div>
                <div class="legend-item">
                    <div class="legend-box" style="background-color: {color_levels['2']};"></div>
                    <span>15-29 XP</span>
                </div>
                <div class="legend-item">
                    <div class="legend-box" style="background-color: {color_levels['3']};"></div>
                    <span>30+ XP</span>
                </div>
            </div>

          </div>

        <script>
        function showTooltip(event, text) {{
            const tooltip = document.getElementById('tooltip');
            tooltip.innerHTML = text;
            tooltip.style.display = 'block';
            tooltip.style.left = (event.pageX + 10) + 'px';
            tooltip.style.top = (event.pageY - 30) + 'px';
        }}

        function hideTooltip() {{
            const tooltip = document.getElementById('tooltip');
            tooltip.style.display = 'none';
        }}
        </script>
        '''

        return heatmap_html_content

    def _generate_stats_summary_html(self, stats: dict) -> str:
        """Generate statistics summary HTML."""
        longest_streak = stats.get('longest_streak', {})
        current_streak = stats.get('current_streak', {})

        # Format date ranges for display
        def format_date_range(start_date, end_date):
            if start_date and end_date:
                start = pd.to_datetime(start_date).strftime('%m-%d')
                end = pd.to_datetime(end_date).strftime('%m-%d')
                return f"{start} to {end}"
            return ""

        longest_range = format_date_range(
            longest_streak.get('start_date'),
            longest_streak.get('end_date')
        )

        current_range = format_date_range(
            current_streak.get('start_date'),
            current_streak.get('end_date')
        )

        # Generate all stat cards
        stat_cards = []

        # Performance stats cards (gradient background)
        longest_subtext = f"<div style='font-size: 0.8em; opacity: 0.8; margin-top: 5px;'>{longest_range}</div>" if longest_range else ""
        current_subtext = f"<div style='font-size: 0.8em; opacity: 0.8; margin-top: 5px;'>{current_range}</div>" if current_range else ""

        stat_cards.extend([
            f'<div class="stat-card">'
            f'    <div class="stat-value">{stats.get("total_xp", 0):,}</div>'
            f'    <div class="stat-label">Total XP</div>'
            f'</div>',
            f'<div class="stat-card">'
            f'    <div class="stat-value">{stats.get("average_daily_xp", 0):.1f}</div>'
            f'    <div class="stat-label">Average Daily XP</div>'
            f'</div>',
            f'<div class="stat-card">'
            f'    <div class="stat-value">{stats.get("active_days", 0)}</div>'
            f'    <div class="stat-label">Active Days</div>'
            f'    <div style="font-size: 0.8em; opacity: 0.8; margin-top: 5px;">of {stats.get("total_days", 0)} days</div>'
            f'</div>',
            f'<div class="stat-card">'
            f'    <div class="stat-value">{longest_streak.get("length", 0)}</div>'
            f'    <div class="stat-label">Longest Streak</div>'
            f'{longest_subtext}'
            f'</div>',
            f'<div class="stat-card">'
            f'    <div class="stat-value">{current_streak.get("length", 0)}</div>'
            f'    <div class="stat-label">Current Streak</div>'
            f'{current_subtext}'
            f'</div>'
        ])

        # Add task type cards with distinct colors
        task_type_stats = stats.get('task_type_stats', [])
        if task_type_stats:
            # Define display names for task types
            display_names = {
                'Lesson': 'Lessons',
                'Review': 'Reviews',
                'Quiz': 'Quizzes',
                'Multistep': 'Multisteps',
                'Placement': 'Diagnostics',
                'Supplemental': 'Activities'
            }

            # Define colors for task types
            colors = {
                'Lesson': '#2E86AB',
                'Review': '#A23B72',
                'Quiz': '#C73E1D',
                'Multistep': '#F18F01',
                'Placement': '#6A994E',
                'Supplemental': '#8B5CF6'
            }

            for task_stat in task_type_stats:
                task_type = task_stat.get('Task Type', '')
                count = task_stat.get('Count', 0)
                xp = task_stat.get('Total XP', 0)

                # Use display name if available, otherwise use original name
                display_name = display_names.get(task_type, task_type)
                color = colors.get(task_type, '#6B7280')

                stat_cards.append(f"""
                <div class="stat-card" style="background: {color};">
                    <div class="stat-value">{count:,}</div>
                    <div class="stat-label">{display_name}</div>
                    <div style="font-size: 0.8em; opacity: 0.9; margin-top: 5px;">{xp:,} XP</div>
                </div>
                """)

        # Separate performance cards and activity cards
        performance_cards = stat_cards[:5]  # Total XP, Average Daily XP, Active Days, Longest Streak, Current Streak
        activity_cards = stat_cards[5:]  # All activity type cards

        return f"""
        <div class="chart-container">
            <div class="chart-title">Summary</div>
            <div class="stats-grid">
                {''.join(performance_cards)}
            </div>
            <div class="stats-grid" style="margin-top: 20px;">
                {''.join(activity_cards)}
            </div>
        </div>
        """

    
    def _generate_task_type_chart_html(self, data: pd.DataFrame) -> str:
        """Generate task type distribution chart HTML."""
        # Create subplots for two pie charts
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Task Count Distribution', 'XP Distribution'),
            specs=[[{"type": "pie"}, {"type": "pie"}]]
        )

        # Task count pie chart
        fig.add_trace(go.Pie(
            labels=data['Task Type'],
            values=data['Count'],
            name="Task Count",
            hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Percentage: %{text}%<extra></extra>",
            textinfo='label+percent',
            textposition='inside',
            showlegend=False
        ), row=1, col=1)

        # XP distribution pie chart
        fig.add_trace(go.Pie(
            labels=data['Task Type'],
            values=data['Total XP'],
            name="XP Distribution",
            hovertemplate="<b>%{label}</b><br>Total XP: %{value}<br>Percentage: %{text}%<extra></extra>",
            textinfo='label+percent',
            textposition='inside',
            showlegend=False
        ), row=1, col=2)

        fig.update_layout(
            title="Task Type Distribution",
            template='plotly_white',
            height=400,
            showlegend=True
        )

        chart_id = 'task_type_chart'
        chart_html = f'<div id="{chart_id}" style="height: 400px;"></div>'
        chart_js = f'Plotly.newPlot("{chart_id}", {fig.to_json()}, {{responsive: true}});'

        return f"""
        <div class="chart-container">
            <div class="chart-title">Task Type Distribution</div>
            <div class="two-column">
                {chart_html}
            </div>
            <script>{chart_js}</script>
        </div>
        """
    
    def _generate_weekday_chart_html(self, data: pd.DataFrame) -> str:
        """Generate weekday distribution chart HTML."""
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=data['Weekday'],
            y=data['Average Daily XP'],
            name='Average Daily XP',
            marker_color='#F18F01',
            hovertemplate='<b>%{x}</b><br>Average Daily XP: %{y:.1f}<extra></extra>'
        ))

        fig.update_layout(
            title="Average Daily XP by Weekday",
            template='plotly_white',
            height=400,
            showlegend=False,
            xaxis_title="Weekday",
            yaxis_title="Average Daily XP"
        )
        
        chart_id = 'weekday_chart'
        chart_html = f'<div id="{chart_id}" style="height: 400px;"></div>'
        chart_js = f'Plotly.newPlot("{chart_id}", {fig.to_json()}, {{responsive: true}});'
        
        return f"""
        <div class="chart-container">
            <div class="chart-title">Average Daily XP by Weekday</div>
            <div class="two-column">
                {chart_html}
            </div>
            <script>{chart_js}</script>
        </div>
        """
    
    def _generate_daily_dist_chart_html(self, data: pd.DataFrame, stats: dict) -> str:
        """Generate daily XP distribution chart HTML."""
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=data['Range Label'],
            y=data['Day Count'],
            name='Day Count',
            marker_color='#2E86AB',
            hovertemplate='<b>%{x}</b><br>Days: %{y}<extra></extra>'
        ))
        
        fig.update_layout(
            title=f"Daily XP Distribution (Mean: {stats['mean_daily_xp']:.1f} XP)",
            template='plotly_white',
            height=400,
            showlegend=False,
            xaxis_title="Daily XP Range",
            yaxis_title="Number of Days"
        )
        
        chart_id = 'daily_dist_chart'
        chart_html = f'<div id="{chart_id}" style="height: 400px;"></div>'
        chart_js = f'Plotly.newPlot("{chart_id}", {fig.to_json()}, {{responsive: true}});'
        
        return f"""
        <div class="chart-container">
            <div class="chart-title">Daily XP Distribution</div>
            <div class="two-column">
                {chart_html}
            </div>
            <script>{chart_js}</script>
        </div>
        """
    
    def _generate_xp_trends_charts_html(self, data: dict) -> str:
        """Generate XP trend charts HTML."""
        daily_data = data.get('daily', pd.DataFrame())
        weekly_data = data.get('weekly', pd.DataFrame())
        
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Daily XP Trend', 'Weekly XP Trend'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        if not daily_data.empty:
            fig.add_trace(go.Scatter(
                x=daily_data['Date'],
                y=daily_data['Total XP'],
                mode='lines+markers',
                name='Daily XP',
                line=dict(color='#2E86AB', width=2),
                marker=dict(size=4)
            ), row=1, col=1)
        
        if not weekly_data.empty:
            fig.add_trace(go.Scatter(
                x=weekly_data['Week Start'],
                y=weekly_data['Total XP'],
                mode='lines+markers',
                name='Weekly XP',
                line=dict(color='#F18F01', width=3),
                marker=dict(size=6)
            ), row=1, col=2)
        
        fig.update_layout(
            template='plotly_white',
            height=400,
            showlegend=False
        )
        
        chart_id = 'xp_trends_chart'
        chart_html = f'<div id="{chart_id}" style="height: 400px;"></div>'
        chart_js = f'Plotly.newPlot("{chart_id}", {fig.to_json()}, {{responsive: true}});'
        
        return f"""
        <div class="chart-container">
            <div class="chart-title">XP Trends</div>
            <div class="two-column">
                {chart_html}
            </div>
            <script>{chart_js}</script>
        </div>
        """
    
    def _generate_efficiency_chart_html(self, data: pd.DataFrame) -> str:
        """Generate efficiency trend chart HTML."""
        if data.empty:
            return ""
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=data['date'],
            y=data['Efficiency Rate'],
            mode='lines+markers',
            name='Daily Efficiency',
            line=dict(color='#2E86AB', width=2),
            marker=dict(size=4)
        ))
        
        fig.add_trace(go.Scatter(
            x=data['date'],
            y=data['7-Day Avg Efficiency'],
            mode='lines',
            name='7-Day Average',
            line=dict(color='#F18F01', width=3)
        ))
        
        fig.add_hline(y=100, line_dash="dash", line_color="gray", 
                     annotation_text="100% Efficiency")
        
        fig.update_layout(
            title="Learning Efficiency Trend",
            template='plotly_white',
            height=400,
            showlegend=True,
            xaxis_title="Date",
            yaxis_title="Efficiency Rate (%)"
        )
        
        chart_id = 'efficiency_chart'
        chart_html = f'<div id="{chart_id}" style="height: 400px;"></div>'
        chart_js = f'Plotly.newPlot("{chart_id}", {fig.to_json()}, {{responsive: true}});'
        
        return f"""
        <div class="chart-container">
            <div class="chart-title">Learning Efficiency Trend</div>
            <div class="two-column">
                {chart_html}
            </div>
            <script>{chart_js}</script>
        </div>
        """
    
    def get_xp_statistics(self) -> Dict[str, Any]:
        """Get XP statistics for the learning data.
        
        Returns:
            Dictionary containing XP statistics
        """
        if self.df.empty:
            return {}
        
        daily_df = self._calculate_daily_xp()
        cumulative_df = self._calculate_cumulative_xp()
        
        longest_streak_data = self._calculate_longest_streak(daily_df)
        current_streak_data = self._calculate_current_streak()

        # Calculate task type statistics
        task_type_stats = self._calculate_task_type_distribution()

        stats = {
            'total_xp': int(cumulative_df['cumulative_xp'].max()) if not cumulative_df.empty else 0,
            'average_daily_xp': float(daily_df['xp_numeric'].mean()) if not daily_df.empty else 0,
            'longest_streak': longest_streak_data,
            'current_streak': current_streak_data,
            'min_daily_xp': int(daily_df['xp_numeric'].min()) if not daily_df.empty else 0,
            'total_days': len(daily_df) if not daily_df.empty else 0,
            'active_days': int((daily_df['xp_numeric'] > 0).sum()) if not daily_df.empty else 0,
            'date_range': {
                'start': daily_df['date'].min().isoformat() if not daily_df.empty else None,
                'end': daily_df['date'].max().isoformat() if not daily_df.empty else None
            },
            'recent_trend': self._calculate_recent_trend(daily_df),
            'task_type_stats': task_type_stats.to_dict('records') if not task_type_stats.empty else []
        }
        
        return stats
    
    def _calculate_longest_streak(self, daily_df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate the longest consecutive days with study activity.

        Args:
            daily_df: DataFrame containing daily XP data

        Returns:
            Dictionary containing streak length and date range
        """
        if self.df.empty:
            return {'length': 0, 'start_date': None, 'end_date': None}

        # Get the date range from the data
        min_date = self.df['date'].min().date()
        max_date = self.df['date'].max().date()

        # Create a complete date range (all calendar days)
        date_range = pd.date_range(start=min_date, end=max_date, freq='D')

        # Count activities per day from the original data
        daily_activity_count = self.df.groupby(self.df['date'].dt.date).size().reset_index()
        daily_activity_count.columns = ['date', 'activity_count']
        daily_activity_count['date'] = pd.to_datetime(daily_activity_count['date'])

        # Create a dictionary for quick lookup of activity counts
        activity_dict = dict(zip(daily_activity_count['date'].dt.date, daily_activity_count['activity_count']))

        # Calculate consecutive streaks across all calendar days
        max_streak = 0
        current_streak = 0
        current_streak_start = None
        max_streak_start = None
        max_streak_end = None

        for date in date_range:
            date_key = date.date()
            has_activity = activity_dict.get(date_key, 0) > 0

            if has_activity:
                if current_streak == 0:
                    current_streak_start = date_key
                current_streak += 1

                if current_streak > max_streak:
                    max_streak = current_streak
                    max_streak_start = current_streak_start
                    max_streak_end = date_key
            else:
                current_streak = 0
                current_streak_start = None

        return {
            'length': max_streak,
            'start_date': max_streak_start.isoformat() if max_streak_start else None,
            'end_date': max_streak_end.isoformat() if max_streak_end else None
        }

    def _calculate_current_streak(self) -> Dict[str, Any]:
        """Calculate the current consecutive days with study activity ending on the last day of records.

        Returns:
            Dictionary containing current streak length and date range
        """
        if self.df.empty:
            return {'length': 0, 'start_date': None, 'end_date': None}

        # Get the date range from the data
        min_date = self.df['date'].min().date()
        max_date = self.df['date'].max().date()

        # Create a complete date range (all calendar days)
        date_range = pd.date_range(start=min_date, end=max_date, freq='D')

        # Count activities per day from the original data
        daily_activity_count = self.df.groupby(self.df['date'].dt.date).size().reset_index()
        daily_activity_count.columns = ['date', 'activity_count']
        daily_activity_count['date'] = pd.to_datetime(daily_activity_count['date'])

        # Create a dictionary for quick lookup of activity counts
        activity_dict = dict(zip(daily_activity_count['date'].dt.date, daily_activity_count['activity_count']))

        # Calculate current streak by iterating backwards from the last day
        current_streak = 0
        current_streak_end = max_date  # The last day of records
        current_streak_start = None

        # Start from the last day and go backwards
        for date in reversed(date_range):
            date_key = date.date()
            has_activity = activity_dict.get(date_key, 0) > 0

            if has_activity:
                current_streak += 1
                current_streak_start = date_key
            else:
                # Stop as soon as we hit a day without activity
                break

        return {
            'length': current_streak,
            'start_date': current_streak_start.isoformat() if current_streak_start else None,
            'end_date': current_streak_end.isoformat() if current_streak_end else None
        }

    def _calculate_recent_trend(self, daily_df: pd.DataFrame) -> Dict[str, float]:
        """Calculate recent XP trend (last 7 days vs previous 7 days)."""
        if len(daily_df) < 14:
            return {'change_percent': 0.0, 'direction': 'insufficient_data'}

        recent_7_days = daily_df.tail(7)['xp_numeric'].mean()
        previous_7_days = daily_df.iloc[-14:-7]['xp_numeric'].mean()

        if previous_7_days == 0:
            change_percent = 100.0 if recent_7_days > 0 else 0.0
        else:
            change_percent = ((recent_7_days - previous_7_days) / previous_7_days) * 100

        direction = 'increasing' if change_percent > 0 else 'decreasing' if change_percent < 0 else 'stable'

        return {
            'change_percent': float(change_percent),
            'direction': direction,
            'recent_average': float(recent_7_days),
            'previous_average': float(previous_7_days)
        }
    
    def _calculate_task_type_distribution(self) -> pd.DataFrame:
        """Calculate task type distribution for pie chart."""
        if self.df.empty:
            return pd.DataFrame()
        
        # Group by task type and count
        task_counts = self.df['Task'].value_counts().reset_index()
        task_counts.columns = ['Task Type', 'Count']
        
        # Calculate XP by task type
        task_xp = self.df.groupby('Task')['xp_numeric'].sum().reset_index()
        task_xp.columns = ['Task Type', 'Total XP']
        
        # Merge count and XP data
        task_distribution = pd.merge(task_counts, task_xp, on='Task Type')
        
        # Calculate percentages
        task_distribution['Count Percentage'] = (task_distribution['Count'] / task_distribution['Count'].sum() * 100).round(1)
        task_distribution['XP Percentage'] = (task_distribution['Total XP'] / task_distribution['Total XP'].sum() * 100).round(1)
        
        return task_distribution
    
    def _calculate_monthly_weekly_daily_stats(self) -> Dict[str, pd.DataFrame]:
        """Calculate monthly, weekly and daily XP statistics."""
        if self.df.empty:
            return {}

        # Daily stats
        daily_stats = self.df.groupby('date').agg({
            'xp_numeric': ['sum', 'count', 'mean']
        }).reset_index()
        daily_stats.columns = ['Date', 'Total XP', 'Task Count', 'Average XP']

        # Add day of week
        daily_stats['Day of Week'] = daily_stats['Date'].dt.day_name()

        # Weekly stats
        weekly_stats = self.df.copy()
        weekly_stats['Week'] = weekly_stats['date'].dt.isocalendar().week
        weekly_stats['Year'] = weekly_stats['date'].dt.year

        weekly_summary = weekly_stats.groupby(['Year', 'Week']).agg({
            'xp_numeric': ['sum', 'count', 'mean']
        }).reset_index()
        weekly_summary.columns = ['Year', 'Week', 'Total XP', 'Task Count', 'Average XP']

        # Create week start date (Monday of each week)
        weekly_summary['Week Start'] = pd.to_datetime(
            weekly_summary['Year'].astype(str) + '-01-01'
        ) + pd.to_timedelta((weekly_summary['Week'] - 1) * 7, unit='D')

        # Monthly stats
        monthly_stats = self.df.copy()
        monthly_stats['Month'] = monthly_stats['date'].dt.month
        monthly_stats['Year'] = monthly_stats['date'].dt.year

        monthly_summary = monthly_stats.groupby(['Year', 'Month']).agg({
            'xp_numeric': ['sum', 'count', 'mean']
        }).reset_index()
        monthly_summary.columns = ['Year', 'Month', 'Total XP', 'Task Count', 'Average XP']

        # Create month start date
        monthly_summary['Month Start'] = pd.to_datetime(
            monthly_summary['Year'].astype(str) + '-' + monthly_summary['Month'].astype(str).str.zfill(2) + '-01'
        )

        # Add month name
        monthly_summary['Month Name'] = monthly_summary['Month Start'].dt.strftime('%B')

        return {
            'daily': daily_stats,
            'weekly': weekly_summary,
            'monthly': monthly_summary
        }

    def _calculate_monthly_weekly_daily_stats_by_task_type(self) -> Dict[str, Dict[str, pd.DataFrame]]:
        """Calculate monthly, weekly and daily XP statistics broken down by task type."""
        if self.df.empty:
            return {}

        # Get unique task types
        task_types = self.df['Task'].unique()
        colors = {
            'Lesson': '#2E86AB',
            'Review': '#A23B72',
            'Quiz': '#C73E1D',
            'Multistep': '#F18F01',
            'Placement': '#6A994E',
            'Supplemental': '#8B5CF6'
        }

        result = {
            'daily': {},
            'weekly': {},
            'monthly': {}
        }

        # Generate default colors for unknown task types if needed
        default_colors = ['#6B7280', '#374151', '#1F2937', '#111827', '#4B5563',
                         '#9CA3AF', '#D1D5DB', '#E5E7EB', '#F3F4F6', '#F9FAFB']
        unknown_task_index = 0

        def get_task_color(task_type):
            """Get color for task type, using default color for unknown types."""
            task_color = colors.get(task_type)
            if task_color is None:
                nonlocal unknown_task_index
                task_color = default_colors[unknown_task_index % len(default_colors)]
                unknown_task_index += 1
            return task_color

        # Daily stats by task type
        for task_type in task_types:
            task_data = self.df[self.df['Task'] == task_type]
            if not task_data.empty:
                daily_stats = task_data.groupby('date').agg({
                    'xp_numeric': ['sum', 'count', 'mean']
                }).reset_index()
                daily_stats.columns = ['Date', 'Total XP', 'Task Count', 'Average XP']
                result['daily'][task_type] = {
                    'data': daily_stats,
                    'color': get_task_color(task_type)
                }

        # Weekly stats by task type
        for task_type in task_types:
            task_data = self.df[self.df['Task'] == task_type].copy()
            if not task_data.empty:
                task_data['Week'] = task_data['date'].dt.isocalendar().week
                task_data['Year'] = task_data['date'].dt.year

                weekly_summary = task_data.groupby(['Year', 'Week']).agg({
                    'xp_numeric': ['sum', 'count', 'mean']
                }).reset_index()
                weekly_summary.columns = ['Year', 'Week', 'Total XP', 'Task Count', 'Average XP']

                # Create week start date (Monday of each week)
                weekly_summary['Week Start'] = pd.to_datetime(
                    weekly_summary['Year'].astype(str) + '-01-01'
                ) + pd.to_timedelta((weekly_summary['Week'] - 1) * 7, unit='D')

                result['weekly'][task_type] = {
                    'data': weekly_summary,
                    'color': get_task_color(task_type)
                }

        # Monthly stats by task type
        for task_type in task_types:
            task_data = self.df[self.df['Task'] == task_type].copy()
            if not task_data.empty:
                task_data['Month'] = task_data['date'].dt.month
                task_data['Year'] = task_data['date'].dt.year

                monthly_summary = task_data.groupby(['Year', 'Month']).agg({
                    'xp_numeric': ['sum', 'count', 'mean']
                }).reset_index()
                monthly_summary.columns = ['Year', 'Month', 'Total XP', 'Task Count', 'Average XP']

                # Create month start date
                monthly_summary['Month Start'] = pd.to_datetime(
                    monthly_summary['Year'].astype(str) + '-' + monthly_summary['Month'].astype(str).str.zfill(2) + '-01'
                )

                result['monthly'][task_type] = {
                    'data': monthly_summary,
                    'color': get_task_color(task_type)
                }

        return result
    
    def _calculate_efficiency_trend(self) -> pd.DataFrame:
        """Calculate learning efficiency trend (XP completion rate over time)."""
        if self.df.empty:
            return pd.DataFrame()
        
        # Calculate daily efficiency
        daily_efficiency = self.df.groupby('date').apply(
            lambda x: pd.Series({
                'Earned XP': x['xp_numeric'].sum(),
                'Possible XP': pd.to_numeric(x['XP Possible'], errors='coerce').sum(),
                'Task Count': len(x)
            }),
            include_groups=False
        ).reset_index()
        
        # Calculate efficiency rate
        daily_efficiency['Efficiency Rate'] = (
            daily_efficiency['Earned XP'] / daily_efficiency['Possible XP'] * 100
        ).round(1)
        
        # Handle division by zero
        daily_efficiency['Efficiency Rate'] = daily_efficiency['Efficiency Rate'].fillna(0)
        
        # Calculate 7-day moving average
        daily_efficiency['7-Day Avg Efficiency'] = daily_efficiency['Efficiency Rate'].rolling(
            window=7, min_periods=1
        ).mean().round(1)
        
        return daily_efficiency
    
    def _calculate_weekday_distribution(self) -> pd.DataFrame:
        """Calculate daily XP distribution by weekday."""
        if self.df.empty:
            return pd.DataFrame()

        # First calculate daily XP totals using a more direct approach
        df_copy = self.df.copy()
        df_copy['weekday'] = df_copy['date'].dt.day_name()
        daily_xp = df_copy.groupby(['date', 'weekday'])['xp_numeric'].sum().reset_index()
        daily_xp.columns = ['date', 'weekday', 'daily_xp']

        # Then calculate average daily XP for each weekday
        weekday_stats = daily_xp.groupby('weekday')['daily_xp'].agg(['mean', 'sum', 'count']).reset_index()
        weekday_stats.columns = ['Weekday', 'Average Daily XP', 'Total XP', 'Number of Days']

        # Order weekdays correctly
        weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        weekday_stats['Weekday'] = pd.Categorical(weekday_stats['Weekday'], categories=weekday_order, ordered=True)
        weekday_stats = weekday_stats.sort_values('Weekday')

        # Calculate percentages
        total_xp = weekday_stats['Total XP'].sum()
        weekday_stats['XP Percentage'] = (weekday_stats['Total XP'] / total_xp * 100).round(1)

        return weekday_stats
    
    def _calculate_daily_xp_distribution(self) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Calculate daily XP distribution (histogram of daily XP counts)."""
        if self.df.empty:
            return pd.DataFrame(), {}

        # Calculate daily XP totals
        daily_xp = self.df.groupby('date')['xp_numeric'].sum().reset_index()
        daily_xp.columns = ['Date', 'Daily XP']

        # Create XP ranges/bins for histogram
        xp_min = daily_xp['Daily XP'].min()
        xp_max = daily_xp['Daily XP'].max()
        xp_mean = daily_xp['Daily XP'].mean()
        xp_median = daily_xp['Daily XP'].median()

        # Create bins with integer boundaries
        bins = min(10, len(daily_xp))  # Max 10 bins
        daily_xp['XP Range'] = pd.cut(daily_xp['Daily XP'], bins=bins, include_lowest=True)

        # Count days in each XP range
        distribution = daily_xp['XP Range'].value_counts().sort_index().reset_index()
        distribution.columns = ['XP Range', 'Day Count']

        # Format XP Range labels as integers and handle negative ranges separately
        def format_range_label(range_obj):
            if range_obj is None:
                return "Unknown"

            left, right = range_obj.left, range_obj.right

            # Always use consistent format with dash
            return f"{int(left)}-{int(right)}"

        distribution['Range Label'] = distribution['XP Range'].apply(format_range_label)

        # Calculate statistics
        stats = {
            'min_daily_xp': xp_min,
            'max_daily_xp': xp_max,
            'mean_daily_xp': xp_mean,
            'median_daily_xp': xp_median,
            'total_days': len(daily_xp)
        }

        return distribution, stats

    def _calculate_learning_heatmap_data(self) -> Dict[str, Any]:
        """Calculate learning heatmap data similar to GitHub contribution graph.

        Returns:
            Dictionary containing heatmap data with dates, XP values, and metadata
        """
        if self.df.empty:
            return {}

        # Calculate daily XP totals
        daily_xp = self.df.groupby('date')['xp_numeric'].sum().reset_index()
        daily_xp.columns = ['date', 'daily_xp']

        # Get the last day from the data and create a 1-year range
        max_date = self.df['date'].max().date()
        min_date = max_date - pd.Timedelta(days=364)  # Last 365 days (52 weeks)

        # Create a complete date range for the last year
        date_range = pd.date_range(start=min_date, end=max_date, freq='D')

        # Create a complete dataframe with all dates
        full_df = pd.DataFrame({'date': date_range})

        # Merge with daily XP data
        heatmap_df = pd.merge(full_df, daily_xp, on='date', how='left')
        heatmap_df['daily_xp'] = heatmap_df['daily_xp'].fillna(0)

        # Determine color levels based on XP thresholds
        def get_color_level(xp):
            if xp == 0:
                return 0  # No activity - gray
            elif xp < 15:
                return 1  # Light green
            elif xp < 30:
                return 2  # Medium green
            else:
                return 3  # Dark green

        heatmap_df['color_level'] = heatmap_df['daily_xp'].apply(get_color_level)

        # Add GitHub-style week and day information (Sunday-starting weeks)
        heatmap_df['weekday_num'] = heatmap_df['date'].dt.weekday  # Monday=0, Sunday=6
        heatmap_df['weekday_name'] = heatmap_df['date'].dt.strftime('%a')
        heatmap_df['iso_week'] = heatmap_df['date'].dt.isocalendar().week
        heatmap_df['iso_year'] = heatmap_df['date'].dt.isocalendar().year

        # Calculate GitHub-style week (Sunday-starting)
        # For GitHub, week changes on Sunday, not Monday
        # If it's Sunday, it belongs to the next GitHub week
        github_week_adjustment = ((heatmap_df['weekday_num'] + 1) % 7)  # Sunday=6 -> 0, Monday=0 -> 1, etc.
        heatmap_df['github_week'] = heatmap_df['iso_week'] + github_week_adjustment

        # Handle year transition when Sunday pushes to next year's week 1
        year_adjustment = ((heatmap_df['iso_week'] + github_week_adjustment - 1) // 52)  # Number of 52-week blocks
        heatmap_df['github_year'] = heatmap_df['iso_year'] + year_adjustment

        heatmap_df['year_week'] = heatmap_df['github_year'].astype(str) + '-' + heatmap_df['github_week'].astype(str).str.zfill(2)

        heatmap_df['weekday_num'] = heatmap_df['date'].dt.weekday  # Monday=0, Sunday=6
        heatmap_df['weekday_name'] = heatmap_df['date'].dt.strftime('%a')
        heatmap_df['week_num'] = heatmap_df['github_week']
        heatmap_df['year'] = heatmap_df['github_year']
        heatmap_df['month'] = heatmap_df['date'].dt.month
        # Ensure date is datetime for strftime
        if not pd.api.types.is_datetime64_any_dtype(heatmap_df['date']):
            heatmap_df['date'] = pd.to_datetime(heatmap_df['date'])
        heatmap_df['month_name'] = heatmap_df['date'].dt.strftime('%b')
        heatmap_df['day'] = heatmap_df['date'].dt.day

        # Calculate statistics
        total_active_days = (heatmap_df['daily_xp'] > 0).sum()
        total_days = len(heatmap_df)

        # Calculate current streak (from the end)
        current_streak = 0
        for i in range(len(heatmap_df) - 1, -1, -1):
            if heatmap_df.iloc[i]['daily_xp'] > 0:
                current_streak += 1
            else:
                break

        return {
            'data': heatmap_df.to_dict('records'),
            'date_range': {
                'start': min_date.isoformat(),
                'end': max_date.isoformat()
            },
            'stats': {
                'total_active_days': int(total_active_days),
                'total_days': int(total_days),
                'current_streak': int(current_streak),
                'max_daily_xp': int(heatmap_df['daily_xp'].max()),
                'average_xp': float(heatmap_df[heatmap_df['daily_xp'] > 0]['daily_xp'].mean()) if total_active_days > 0 else 0
            },
            'color_levels': {
                '0': '#ebedf0',  # Gray - no activity
                '1': '#9be9a8',  # Light green - XP < 15
                '2': '#40c463',  # Medium green - 15 <= XP < 30
                '3': '#30a14e'   # Dark green - XP >= 30
            }
        }

    
