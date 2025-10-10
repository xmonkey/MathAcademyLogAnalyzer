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
        
        # Calculate cumulative sum
        daily_xp['cumulative_xp'] = daily_xp['xp_numeric'].cumsum()
        
        return daily_xp
    
    def _calculate_daily_xp(self) -> pd.DataFrame:
        """Calculate daily XP with date range coverage."""
        if self.df.empty:
            return pd.DataFrame()
        
        # Group by date and sum XP
        daily_xp = self.df.groupby('date')['xp_numeric'].sum().reset_index()
        
        # Simplified approach - don't fill missing dates for now
        return daily_xp
    
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
        fig = go.Figure()
        
        # Add cumulative XP line
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['cumulative_xp'],
            mode='lines+markers',
            name='Cumulative XP',
            line=dict(color='#2E86AB', width=3),
            marker=dict(size=6),
            hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Cumulative XP: %{y}<extra></extra>'
        ))
        
        # Milestone annotations disabled due to plotly compatibility issue
        # TODO: Re-enable when plotly compatibility is resolved
        
        # Update layout
        fig.update_layout(
            title="Cumulative XP Progress",
            xaxis_title="Date",
            yaxis_title="Cumulative XP",
            hovermode='x unified',
            template='plotly_white',
            showlegend=True,
            height=600,
            xaxis=dict(
                tickformat='%Y-%m-%d',
                tickangle=45
            )
        )
        
        # Save as HTML
        output_file = f"{output_path}.html"
        fig.write_html(output_file)
        
        return output_file
    
    def _generate_static_cumulative_xp(self, df: pd.DataFrame, output_path: str) -> str:
        """Generate static cumulative XP chart using Matplotlib."""
        plt.figure(figsize=(12, 6))
        
        # Set style
        plt.style.use('default')
        
        # Plot cumulative XP
        plt.plot(df['date'], df['cumulative_xp'], 
                marker='o', linewidth=2, markersize=6, 
                color='#2E86AB', label='Cumulative XP')
        
        # Fill area under curve
        plt.fill_between(df['date'], df['cumulative_xp'], alpha=0.3, color='#2E86AB')
        
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
        
        # Add grid
        plt.grid(True, alpha=0.3)
        
        # Add legend
        plt.legend()
        
        # Adjust layout
        plt.tight_layout()
        
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
        """Generate interactive daily XP chart using Plotly."""
        fig = go.Figure()
        
        # Add daily XP bars
        fig.add_trace(go.Bar(
            x=df['date'],
            y=df['xp_numeric'],
            name='Daily XP',
            marker_color='#A23B72',
            opacity=0.8,
            hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Daily XP: %{y}<extra></extra>'
        ))
        
        # Add trend line (7-day moving average)
        if len(df) >= 7:
            df['trend'] = df['xp_numeric'].rolling(window=7, center=True).mean()
            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['trend'],
                mode='lines',
                name='7-Day Average',
                line=dict(color='#F18F01', width=2),
                hovertemplate='<b>%{x|%Y-%m-%d}</b><br>7-Day Avg: %{y:.1f}<extra></extra>'
            ))
        
        # Update layout
        fig.update_layout(
            title="Daily XP Trend",
            xaxis_title="Date",
            yaxis_title="Daily XP",
            hovermode='x unified',
            template='plotly_white',
            showlegend=True,
            height=600,
            xaxis=dict(
                tickformat='%Y-%m-%d',
                tickangle=45
            ),
            yaxis=dict(
                title="Daily XP",
                tickformat=',.0f'
            )
        )
        
        # Save as HTML
        output_file = f"{output_path}.html"
        fig.write_html(output_file)
        
        return output_file
    
    def _generate_static_daily_xp(self, df: pd.DataFrame, output_path: str) -> str:
        """Generate static daily XP chart using Matplotlib."""
        plt.figure(figsize=(14, 6))
        
        # Set style
        plt.style.use('default')
        
        # Create bar chart
        bars = plt.bar(df['date'], df['xp_numeric'], 
                      color='#A23B72', alpha=0.8, width=0.8)
        
        # Add trend line (7-day moving average)
        if len(df) >= 7:
            df['trend'] = df['xp_numeric'].rolling(window=7, center=True).mean()
            plt.plot(df['date'], df['trend'], 
                    color='#F18F01', linewidth=2, 
                    label='7-Day Average')
        
        # Formatting
        plt.title("Daily XP Trend",
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
        
        # Add legend
        plt.legend()
        
        # Adjust layout
        plt.tight_layout()
        
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
            daily_df['trend'] = daily_df['xp_numeric'].rolling(window=7, center=True).mean()
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
        
        # Task count pie chart
        ax1.pie(df['Count'], labels=df['Task Type'], autopct='%1.1f%%', startangle=90)
        ax1.set_title('Task Count Distribution')
        
        # XP distribution pie chart
        ax2.pie(df['Total XP'], labels=df['Task Type'], autopct='%1.1f%%', startangle=90)
        ax2.set_title('XP Distribution')
        
        # Main title
        fig.suptitle("Task Type Distribution",
                    fontsize=16, fontweight='bold')
        
        # Adjust layout
        plt.tight_layout()
        
        # Save as PNG
        output_file = f"{output_path}.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_file
    
    def generate_weekly_daily_stats_chart(self, output_path: Optional[str] = None, 
                                        interactive: bool = True) -> str:
        """Generate weekly and daily XP statistics chart.
        
        Args:
            output_path: Output path for the chart file
            interactive: Whether to generate interactive (Plotly) or static (Matplotlib) chart
            
        Returns:
            Path to the generated chart file
        """
        if self.df.empty:
            raise ValueError("No data available for chart generation")
        
        stats_data = self._calculate_weekly_daily_stats()
        
        if output_path is None:
            output_path = self.json_path.parent / "weekly_daily_stats_chart"
        
        if interactive:
            return self._generate_interactive_weekly_daily_stats(stats_data, output_path)
        else:
            return self._generate_static_weekly_daily_stats(stats_data, output_path)
    
    def _generate_interactive_weekly_daily_stats(self, stats_data: Dict[str, pd.DataFrame], output_path: str) -> str:
        """Generate interactive weekly/daily stats chart using Plotly."""
        daily_df = stats_data['daily']
        weekly_df = stats_data['weekly']
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Daily XP Trend', 'Weekly XP Trend', 'Daily Task Count', 'Weekly Task Count'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Daily XP trend
        fig.add_trace(go.Scatter(
            x=daily_df['Date'],
            y=daily_df['Total XP'],
            mode='lines+markers',
            name='Daily XP',
            line=dict(color='#2E86AB', width=2),
            marker=dict(size=4),
            showlegend=False
        ), row=1, col=1)
        
        # Weekly XP trend
        fig.add_trace(go.Scatter(
            x=weekly_df['Week Start'],
            y=weekly_df['Total XP'],
            mode='lines+markers',
            name='Weekly XP',
            line=dict(color='#A23B72', width=3),
            marker=dict(size=6),
            showlegend=False
        ), row=1, col=2)
        
        # Daily task count
        fig.add_trace(go.Bar(
            x=daily_df['Date'],
            y=daily_df['Task Count'],
            name='Daily Tasks',
            marker_color='#F18F01',
            opacity=0.8,
            showlegend=False
        ), row=2, col=1)
        
        # Weekly task count
        fig.add_trace(go.Bar(
            x=weekly_df['Week Start'],
            y=weekly_df['Task Count'],
            name='Weekly Tasks',
            marker_color='#C73E1D',
            opacity=0.8,
            showlegend=False
        ), row=2, col=2)
        
        # Update layout
        fig.update_layout(
            title="Weekly & Daily XP Statistics",
            template='plotly_white',
            height=800,
            showlegend=True
        )
        
        # Update x-axes
        fig.update_xaxes(title_text="Date", row=1, col=1)
        fig.update_xaxes(title_text="Week Start", row=1, col=2)
        fig.update_xaxes(title_text="Date", row=2, col=1)
        fig.update_xaxes(title_text="Week Start", row=2, col=2)
        
        # Update y-axes
        fig.update_yaxes(title_text="XP", row=1, col=1)
        fig.update_yaxes(title_text="XP", row=1, col=2)
        fig.update_yaxes(title_text="Task Count", row=2, col=1)
        fig.update_yaxes(title_text="Task Count", row=2, col=2)
        
        # Save as HTML
        output_file = f"{output_path}.html"
        fig.write_html(output_file)
        
        return output_file
    
    def _generate_static_weekly_daily_stats(self, stats_data: Dict[str, pd.DataFrame], output_path: str) -> str:
        """Generate static weekly/daily stats chart using Matplotlib."""
        daily_df = stats_data['daily']
        weekly_df = stats_data['weekly']
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # Daily XP trend
        axes[0, 0].plot(daily_df['Date'], daily_df['Total XP'], 
                       marker='o', linewidth=2, markersize=4, color='#2E86AB')
        axes[0, 0].set_title('Daily XP Trend')
        axes[0, 0].set_xlabel('Date')
        axes[0, 0].set_ylabel('XP')
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # Weekly XP trend
        axes[0, 1].plot(weekly_df['Week Start'], weekly_df['Total XP'], 
                       marker='o', linewidth=3, markersize=6, color='#A23B72')
        axes[0, 1].set_title('Weekly XP Trend')
        axes[0, 1].set_xlabel('Week Start')
        axes[0, 1].set_ylabel('XP')
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # Daily task count
        axes[1, 0].bar(daily_df['Date'], daily_df['Task Count'], 
                      color='#F18F01', alpha=0.8)
        axes[1, 0].set_title('Daily Task Count')
        axes[1, 0].set_xlabel('Date')
        axes[1, 0].set_ylabel('Task Count')
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        # Weekly task count
        axes[1, 1].bar(weekly_df['Week Start'], weekly_df['Task Count'], 
                      color='#C73E1D', alpha=0.8)
        axes[1, 1].set_title('Weekly Task Count')
        axes[1, 1].set_xlabel('Week Start')
        axes[1, 1].set_ylabel('Task Count')
        axes[1, 1].tick_params(axis='x', rotation=45)
        
        # Main title
        fig.suptitle("Weekly & Daily XP Statistics",
                    fontsize=16, fontweight='bold')
        
        # Adjust layout
        plt.tight_layout()
        
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
        ax.set_title('Daily XP Distribution')
        ax.set_ylabel('Number of Days')
        ax.set_xlabel('Daily XP Range')
        ax.tick_params(axis='x', rotation=45)
        ax.grid(True, alpha=0.3)

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}', ha='center', va='bottom')

        # Find which XP range contains the mean and median, then add annotations
        mean_range_idx = self._find_xp_range_for_value(stats['mean_daily_xp'], df)
        median_range_idx = self._find_xp_range_for_value(stats['median_daily_xp'], df)

        # Add annotations for mean and median
        if mean_range_idx is not None:
            mean_count = df.loc[mean_range_idx, 'Day Count']
            ax.annotate(f'Mean: {stats["mean_daily_xp"]:.1f}',
                       xy=(mean_range_idx, mean_count),
                       xytext=(mean_range_idx, mean_count * 1.3),
                       ha='center',
                       arrowprops=dict(arrowstyle='->', color='red', lw=2),
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='red'),
                       fontsize=10, color='red', fontweight='bold')

        if median_range_idx is not None:
            median_count = df.loc[median_range_idx, 'Day Count']
            ax.annotate(f'Median: {stats["median_daily_xp"]:.1f}',
                       xy=(median_range_idx, median_count),
                       xytext=(median_range_idx, median_count * 1.5),
                       ha='center',
                       arrowprops=dict(arrowstyle='->', color='orange', lw=2),
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='orange'),
                       fontsize=10, color='orange', fontweight='bold')

        # Main title with statistics
        fig.suptitle(f"Daily XP Distribution\n"
                    f"Mean: {stats['mean_daily_xp']:.1f} XP, Median: {stats['median_daily_xp']:.1f} XP, "
                    f"Range: {stats['min_daily_xp']:.0f}-{stats['max_daily_xp']:.0f} XP",
                    fontsize=14, fontweight='bold')

        # Adjust layout to make room for annotations
        plt.tight_layout()
        plt.subplots_adjust(top=0.85)  # Make room for suptitle

        # Save as PNG
        output_file = f"{output_path}.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()

        return output_file
    
    def generate_comprehensive_dashboard(self, output_path: Optional[str] = None) -> str:
        """Generate comprehensive dashboard with all charts integrated into one page.
        
        Args:
            output_path: Output path for the dashboard file
            
        Returns:
            Path to the generated dashboard file
        """
        if self.df.empty:
            raise ValueError("No data available for chart generation")
        
        if output_path is None:
            output_path = self.json_path.parent / "comprehensive_dashboard"
        
        # Generate all chart data
        try:
            # Get statistics
            stats = self.get_xp_statistics()
            
            # Generate all charts
            task_type_data = self._calculate_task_type_distribution()
            weekday_data = self._calculate_weekday_distribution()
            daily_dist_data, daily_dist_stats = self._calculate_daily_xp_distribution()
            weekly_daily_data = self._calculate_weekly_daily_stats()
            efficiency_data = self._calculate_efficiency_trend()
            
            # Generate the comprehensive dashboard
            return self._generate_comprehensive_dashboard_html(
                stats, task_type_data, weekday_data, daily_dist_data, 
                daily_dist_stats, weekly_daily_data, efficiency_data, output_path
            )
        except Exception as e:
            # Fallback: generate existing dashboard
            return self.generate_combined_xp_dashboard(str(output_path))
    
    def _generate_comprehensive_dashboard_html(self, stats: dict, task_type_data: pd.DataFrame, 
                                               weekday_data: pd.DataFrame, daily_dist_data: pd.DataFrame,
                                               daily_dist_stats: dict, weekly_daily_data: dict, 
                                               efficiency_data: pd.DataFrame, output_path: str) -> str:
        """Generate comprehensive dashboard HTML with all charts."""
        
        # Generate individual chart components
        charts_html = []
        
        # 1. Statistics Summary
        charts_html.append(self._generate_stats_summary_html(stats))
        
        # 2. Task Type Distribution
        charts_html.append(self._generate_task_type_chart_html(task_type_data))
        
        # 3. Weekday Distribution
        charts_html.append(self._generate_weekday_chart_html(weekday_data))
        
        # 4. Daily XP Distribution
        charts_html.append(self._generate_daily_dist_chart_html(daily_dist_data, daily_dist_stats))
        
        # 5. XP Trend Charts
        charts_html.append(self._generate_xp_trends_charts_html(weekly_daily_data))
        
        # 6. Efficiency Trend
        charts_html.append(self._generate_efficiency_chart_html(efficiency_data))
        
        # Combine all into final HTML
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Learning Analytics Dashboard</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
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
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
                .two-column {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 20px;
                }}
                @media (max-width: 768px) {{
                    .two-column {{
                        grid-template-columns: 1fr;
                    }}
                    .stats-grid {{
                        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Learning Analytics Dashboard</h1>
                <p>Comprehensive learning analysis</p>
            </div>
            
            {''.join(charts_html)}
            
            <div style="text-align: center; margin-top: 40px; padding: 20px; color: #666;">
                <p>Generated on {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>MA Log PDF Parser - Learning Analytics</p>
            </div>
        </body>
        </html>
        """
        
        # Save as HTML
        output_file = f"{output_path}.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_file
    
    def _generate_stats_summary_html(self, stats: dict) -> str:
        """Generate statistics summary HTML."""
        return f"""
        <div class="chart-container">
            <div class="chart-title">Performance Summary</div>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">{stats.get('total_xp', 0):,}</div>
                    <div class="stat-label">Total XP</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{stats.get('average_daily_xp', 0):.1f}</div>
                    <div class="stat-label">Average Daily XP</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{stats.get('active_days', 0)}</div>
                    <div class="stat-label">Active Days</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{stats.get('max_daily_xp', 0):,}</div>
                    <div class="stat-label">Best Day</div>
                </div>
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
        
        stats = {
            'total_xp': int(cumulative_df['cumulative_xp'].max()) if not cumulative_df.empty else 0,
            'average_daily_xp': float(daily_df['xp_numeric'].mean()) if not daily_df.empty else 0,
            'max_daily_xp': int(daily_df['xp_numeric'].max()) if not daily_df.empty else 0,
            'min_daily_xp': int(daily_df['xp_numeric'].min()) if not daily_df.empty else 0,
            'total_days': len(daily_df) if not daily_df.empty else 0,
            'active_days': int((daily_df['xp_numeric'] > 0).sum()) if not daily_df.empty else 0,
            'date_range': {
                'start': daily_df['date'].min().isoformat() if not daily_df.empty else None,
                'end': daily_df['date'].max().isoformat() if not daily_df.empty else None
            },
            'recent_trend': self._calculate_recent_trend(daily_df)
        }
        
        return stats
    
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
    
    def _calculate_weekly_daily_stats(self) -> Dict[str, pd.DataFrame]:
        """Calculate weekly and daily XP statistics."""
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
        
        return {
            'daily': daily_stats,
            'weekly': weekly_summary
        }
    
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