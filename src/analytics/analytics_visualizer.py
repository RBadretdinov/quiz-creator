"""
Analytics Visualizer

This module provides text-based visualization capabilities for analytics data,
creating charts, graphs, and visual representations using ASCII characters.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import math

logger = logging.getLogger(__name__)

class AnalyticsVisualizer:
    """Text-based analytics visualizer for console output."""
    
    def __init__(self):
        """Initialize the analytics visualizer."""
        self.chart_width = 60
        self.chart_height = 20
        
        logger.info("Analytics visualizer initialized")
    
    def create_bar_chart(self, data: Dict[str, float], title: str = "Bar Chart", 
                        max_width: int = 60) -> str:
        """
        Create a text-based bar chart.
        
        Args:
            data: Dictionary of label-value pairs
            title: Chart title
            max_width: Maximum width of the chart
            
        Returns:
            Formatted bar chart string
        """
        try:
            if not data:
                return f"{title}\nNo data available\n"
            
            # Find maximum value for scaling
            max_value = max(data.values()) if data.values() else 1
            
            chart = []
            chart.append(f"{title}")
            chart.append("=" * len(title))
            chart.append("")
            
            # Create bars
            for label, value in data.items():
                # Calculate bar length
                bar_length = int((value / max_value) * max_width) if max_value > 0 else 0
                bar = "█" * bar_length
                
                # Format the bar
                chart.append(f"{label:<20} │{bar:<{max_width}} {value:.1f}")
            
            chart.append("")
            return "\n".join(chart)
            
        except Exception as e:
            logger.error(f"Failed to create bar chart: {e}")
            return f"{title}\nError creating chart: {e}\n"
    
    def create_line_chart(self, data: List[Dict[str, Any]], title: str = "Line Chart",
                         x_field: str = "date", y_field: str = "value") -> str:
        """
        Create a text-based line chart.
        
        Args:
            data: List of data points with x and y values
            title: Chart title
            x_field: Field name for x-axis values
            y_field: Field name for y-axis values
            
        Returns:
            Formatted line chart string
        """
        try:
            if not data:
                return f"{title}\nNo data available\n"
            
            # Extract values
            x_values = [point.get(x_field, "") for point in data]
            y_values = [point.get(y_field, 0) for point in data]
            
            # Find min and max values
            min_y = min(y_values) if y_values else 0
            max_y = max(y_values) if y_values else 1
            
            chart = []
            chart.append(f"{title}")
            chart.append("=" * len(title))
            chart.append("")
            
            # Create chart grid
            for i in range(self.chart_height, 0, -1):
                line = []
                y_pos = min_y + (max_y - min_y) * (i - 1) / (self.chart_height - 1)
                
                for j, (x_val, y_val) in enumerate(zip(x_values, y_values)):
                    if j < len(x_values) - 1:
                        # Interpolate between points
                        next_y = y_values[j + 1] if j + 1 < len(y_values) else y_val
                        if min(y_val, next_y) <= y_pos <= max(y_val, next_y):
                            line.append("●")
                        elif abs(y_val - y_pos) < (max_y - min_y) / (self.chart_height * 2):
                            line.append("●")
                        else:
                            line.append(" ")
                    else:
                        if abs(y_val - y_pos) < (max_y - min_y) / (self.chart_height * 2):
                            line.append("●")
                        else:
                            line.append(" ")
                
                # Add y-axis label
                y_label = f"{y_pos:.1f}" if y_pos != 0 else "0"
                chart.append(f"{y_label:>6} │{''.join(line)}")
            
            # Add x-axis
            chart.append("       └" + "─" * len(x_values))
            
            # Add x-axis labels
            x_labels = []
            for i, x_val in enumerate(x_values):
                if i % max(1, len(x_values) // 10) == 0:  # Show every 10th label
                    x_labels.append(f"{x_val:<6}")
                else:
                    x_labels.append("      ")
            
            chart.append("       " + "".join(x_labels))
            chart.append("")
            
            return "\n".join(chart)
            
        except Exception as e:
            logger.error(f"Failed to create line chart: {e}")
            return f"{title}\nError creating chart: {e}\n"
    
    def create_pie_chart(self, data: Dict[str, float], title: str = "Pie Chart") -> str:
        """
        Create a text-based pie chart representation.
        
        Args:
            data: Dictionary of label-value pairs
            title: Chart title
            
        Returns:
            Formatted pie chart string
        """
        try:
            if not data:
                return f"{title}\nNo data available\n"
            
            total = sum(data.values())
            if total == 0:
                return f"{title}\nNo data available\n"
            
            chart = []
            chart.append(f"{title}")
            chart.append("=" * len(title))
            chart.append("")
            
            # Create pie chart representation
            chart.append("Pie Chart Representation:")
            chart.append("")
            
            # Calculate percentages and create segments
            segments = []
            for label, value in data.items():
                percentage = (value / total) * 100
                segments.append((label, value, percentage))
            
            # Sort by value (largest first)
            segments.sort(key=lambda x: x[1], reverse=True)
            
            # Display segments
            for label, value, percentage in segments:
                bar_length = int(percentage / 2)  # Scale for display
                bar = "█" * bar_length
                chart.append(f"{label:<20} {bar:<30} {percentage:.1f}% ({value})")
            
            chart.append("")
            chart.append(f"Total: {total}")
            chart.append("")
            
            return "\n".join(chart)
            
        except Exception as e:
            logger.error(f"Failed to create pie chart: {e}")
            return f"{title}\nError creating chart: {e}\n"
    
    def create_histogram(self, data: List[float], title: str = "Histogram",
                        bins: int = 10) -> str:
        """
        Create a text-based histogram.
        
        Args:
            data: List of numeric values
            title: Chart title
            bins: Number of bins for the histogram
            
        Returns:
            Formatted histogram string
        """
        try:
            if not data:
                return f"{title}\nNo data available\n"
            
            # Find min and max values
            min_val = min(data)
            max_val = max(data)
            
            # Create bins
            bin_width = (max_val - min_val) / bins if max_val > min_val else 1
            bin_counts = [0] * bins
            
            # Count values in each bin
            for value in data:
                bin_index = min(int((value - min_val) / bin_width), bins - 1)
                bin_counts[bin_index] += 1
            
            # Find maximum count for scaling
            max_count = max(bin_counts) if bin_counts else 1
            
            chart = []
            chart.append(f"{title}")
            chart.append("=" * len(title))
            chart.append("")
            
            # Create histogram bars
            for i, count in enumerate(bin_counts):
                bin_start = min_val + i * bin_width
                bin_end = min_val + (i + 1) * bin_width
                bar_length = int((count / max_count) * self.chart_width) if max_count > 0 else 0
                bar = "█" * bar_length
                
                chart.append(f"{bin_start:.1f}-{bin_end:.1f} │{bar:<{self.chart_width}} {count}")
            
            chart.append("")
            chart.append(f"Total values: {len(data)}")
            chart.append(f"Range: {min_val:.1f} to {max_val:.1f}")
            chart.append("")
            
            return "\n".join(chart)
            
        except Exception as e:
            logger.error(f"Failed to create histogram: {e}")
            return f"{title}\nError creating chart: {e}\n"
    
    def create_heatmap(self, data: List[List[float]], title: str = "Heatmap",
                      x_labels: List[str] = None, y_labels: List[str] = None) -> str:
        """
        Create a text-based heatmap.
        
        Args:
            data: 2D list of numeric values
            title: Chart title
            x_labels: Labels for x-axis
            y_labels: Labels for y-axis
            
        Returns:
            Formatted heatmap string
        """
        try:
            if not data or not data[0]:
                return f"{title}\nNo data available\n"
            
            # Find min and max values
            all_values = [val for row in data for val in row]
            min_val = min(all_values)
            max_val = max(all_values)
            
            chart = []
            chart.append(f"{title}")
            chart.append("=" * len(title))
            chart.append("")
            
            # Create heatmap
            for i, row in enumerate(data):
                line = []
                for j, value in enumerate(row):
                    # Normalize value to 0-1 range
                    normalized = (value - min_val) / (max_val - min_val) if max_val > min_val else 0
                    
                    # Map to heatmap character
                    if normalized < 0.2:
                        char = "░"
                    elif normalized < 0.4:
                        char = "▒"
                    elif normalized < 0.6:
                        char = "▓"
                    else:
                        char = "█"
                    
                    line.append(char)
                
                # Add row label
                row_label = y_labels[i] if y_labels and i < len(y_labels) else f"Row {i+1}"
                chart.append(f"{row_label:<10} │{''.join(line)}")
            
            # Add column labels
            if x_labels:
                chart.append("           " + "".join(f"{label:<2}" for label in x_labels[:len(data[0])]))
            
            chart.append("")
            chart.append(f"Range: {min_val:.1f} to {max_val:.1f}")
            chart.append("")
            
            return "\n".join(chart)
            
        except Exception as e:
            logger.error(f"Failed to create heatmap: {e}")
            return f"{title}\nError creating chart: {e}\n"
    
    def create_gauge(self, value: float, max_value: float, title: str = "Gauge",
                    label: str = "Value") -> str:
        """
        Create a text-based gauge.
        
        Args:
            value: Current value
            max_value: Maximum value
            title: Gauge title
            label: Value label
            
        Returns:
            Formatted gauge string
        """
        try:
            if max_value <= 0:
                return f"{title}\nInvalid maximum value\n"
            
            # Calculate percentage
            percentage = min(value / max_value, 1.0)
            
            # Create gauge
            gauge_width = 40
            filled_width = int(percentage * gauge_width)
            empty_width = gauge_width - filled_width
            
            gauge = "█" * filled_width + "░" * empty_width
            
            chart = []
            chart.append(f"{title}")
            chart.append("=" * len(title))
            chart.append("")
            chart.append(f"{label}: {value:.1f} / {max_value:.1f}")
            chart.append("")
            chart.append(f"│{gauge}│ {percentage:.1%}")
            chart.append("")
            
            return "\n".join(chart)
            
        except Exception as e:
            logger.error(f"Failed to create gauge: {e}")
            return f"{title}\nError creating gauge: {e}\n"
    
    def create_progress_bar(self, current: int, total: int, title: str = "Progress",
                           width: int = 40) -> str:
        """
        Create a text-based progress bar.
        
        Args:
            current: Current progress value
            total: Total progress value
            title: Progress bar title
            width: Width of the progress bar
            
        Returns:
            Formatted progress bar string
        """
        try:
            if total <= 0:
                return f"{title}\nInvalid total value\n"
            
            # Calculate progress
            progress = min(current / total, 1.0)
            filled_width = int(progress * width)
            empty_width = width - filled_width
            
            bar = "█" * filled_width + "░" * empty_width
            
            chart = []
            chart.append(f"{title}")
            chart.append("=" * len(title))
            chart.append("")
            chart.append(f"Progress: {current} / {total}")
            chart.append("")
            chart.append(f"│{bar}│ {progress:.1%}")
            chart.append("")
            
            return "\n".join(chart)
            
        except Exception as e:
            logger.error(f"Failed to create progress bar: {e}")
            return f"{title}\nError creating progress bar: {e}\n"
    
    def create_summary_table(self, data: Dict[str, Any], title: str = "Summary") -> str:
        """
        Create a formatted summary table.
        
        Args:
            data: Dictionary of key-value pairs
            title: Table title
            
        Returns:
            Formatted table string
        """
        try:
            if not data:
                return f"{title}\nNo data available\n"
            
            table = []
            table.append(f"{title}")
            table.append("=" * len(title))
            table.append("")
            
            # Find maximum key length for alignment
            max_key_length = max(len(str(key)) for key in data.keys()) if data else 0
            
            # Create table rows
            for key, value in data.items():
                if isinstance(value, (int, float)):
                    value_str = f"{value:.2f}" if isinstance(value, float) else str(value)
                else:
                    value_str = str(value)
                
                table.append(f"{str(key):<{max_key_length}} │ {value_str}")
            
            table.append("")
            
            return "\n".join(table)
            
        except Exception as e:
            logger.error(f"Failed to create summary table: {e}")
            return f"{title}\nError creating table: {e}\n"
    
    def create_trend_analysis(self, data: List[Dict[str, Any]], 
                              title: str = "Trend Analysis") -> str:
        """
        Create a trend analysis visualization.
        
        Args:
            data: List of data points with timestamps and values
            title: Analysis title
            
        Returns:
            Formatted trend analysis string
        """
        try:
            if not data:
                return f"{title}\nNo data available\n"
            
            analysis = []
            analysis.append(f"{title}")
            analysis.append("=" * len(title))
            analysis.append("")
            
            # Extract values and timestamps
            values = [point.get('value', 0) for point in data]
            timestamps = [point.get('timestamp', '') for point in data]
            
            if len(values) < 2:
                analysis.append("Insufficient data for trend analysis")
                return "\n".join(analysis)
            
            # Calculate trend
            first_value = values[0]
            last_value = values[-1]
            trend_direction = "increasing" if last_value > first_value else "decreasing" if last_value < first_value else "stable"
            trend_magnitude = abs(last_value - first_value)
            
            # Calculate average
            average = sum(values) / len(values)
            
            # Calculate volatility (standard deviation)
            variance = sum((x - average) ** 2 for x in values) / len(values)
            volatility = math.sqrt(variance)
            
            # Create trend line
            trend_line = self.create_line_chart(data, "Trend Line", "timestamp", "value")
            
            analysis.append(f"Trend Direction: {trend_direction}")
            analysis.append(f"Trend Magnitude: {trend_magnitude:.2f}")
            analysis.append(f"Average Value: {average:.2f}")
            analysis.append(f"Volatility: {volatility:.2f}")
            analysis.append("")
            analysis.append(trend_line)
            
            return "\n".join(analysis)
            
        except Exception as e:
            logger.error(f"Failed to create trend analysis: {e}")
            return f"{title}\nError creating trend analysis: {e}\n"
