import click
import json
from pathlib import Path
from .pdf_parser import PDFParser
from .course_parser import CourseProgressParser
from .chart_generator import ChartGenerator
from . import __version__


@click.group()
def cli():
    """PDF parsing tools using pdfplumber."""
    pass


@cli.command()
def version():
    """Show version information."""
    click.echo(f"mathacademy-analyzer version {__version__}")


@cli.command()
@click.argument("pdf_path", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option("--pages", is_flag=True, help="Extract text by page")
def text(pdf_path, output, pages):
    """Extract text from a PDF file."""
    try:
        parser = PDFParser(pdf_path)
        
        if pages:
            result = parser.extract_text_by_page()
            if output:
                with open(output, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                click.echo(f"Text by page saved to {output}")
            else:
                for i, page_text in enumerate(result, 1):
                    click.echo(f"=== Page {i} ===")
                    click.echo(page_text)
                    click.echo()
        else:
            result = parser.extract_text()
            if output:
                with open(output, 'w', encoding='utf-8') as f:
                    f.write(result)
                click.echo(f"Text saved to {output}")
            else:
                click.echo(result)
                
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@cli.command()
@click.argument("pdf_path", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option("--pages", is_flag=True, help="Extract tables by page")
def tables(pdf_path, output, pages):
    """Extract tables from a PDF file."""
    try:
        parser = PDFParser(pdf_path)
        
        if pages:
            result = parser.extract_tables_by_page()
            if output:
                with open(output, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                click.echo(f"Tables by page saved to {output}")
            else:
                for page_num, page_tables in result.items():
                    click.echo(f"=== Page {page_num} ===")
                    for i, table in enumerate(page_tables, 1):
                        click.echo(f"Table {i}:")
                        for row in table:
                            click.echo(" | ".join(str(cell) if cell else "" for cell in row))
                        click.echo()
        else:
            result = parser.extract_tables()
            if output:
                with open(output, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                click.echo(f"Tables saved to {output}")
            else:
                for i, table in enumerate(result, 1):
                    click.echo(f"Table {i}:")
                    for row in table:
                        click.echo(" | ".join(str(cell) if cell else "" for cell in row))
                    click.echo()
                    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@cli.command()
@click.argument("pdf_path", type=click.Path(exists=True))
def info(pdf_path):
    """Display PDF metadata and information."""
    try:
        parser = PDFParser(pdf_path)
        
        click.echo(f"PDF file: {pdf_path}")
        click.echo(f"Pages: {parser.get_page_count()}")
        
        metadata = parser.get_metadata()
        if metadata:
            click.echo("\nMetadata:")
            for key, value in metadata.items():
                click.echo(f"  {key}: {value}")
        else:
            click.echo("\nNo metadata found")
            
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@cli.command()
@click.argument("pdf_path", type=click.Path(exists=True))
@click.argument("search_term")
@click.option("--output", "-o", type=click.Path(), help="Output file path")
def search(pdf_path, search_term, output):
    """Search for text in a PDF file."""
    try:
        parser = PDFParser(pdf_path)
        results = parser.search_text(search_term)
        
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            click.echo(f"Search results saved to {output}")
        else:
            if results:
                click.echo(f"Found '{search_term}' in {len(results)} locations:")
                for result in results:
                    click.echo(f"  Page {result['page']}: {result['context']}")
            else:
                click.echo(f"'{search_term}' not found in the PDF")
                
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@cli.command()
@click.argument("pdf_path", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Output file path")
def positions(pdf_path, output):
    """Extract text with position information."""
    try:
        parser = PDFParser(pdf_path)
        result = parser.extract_text_with_positions()
        
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            click.echo(f"Text positions saved to {output}")
        else:
            for item in result[:100]:  # Limit output for console
                click.echo(f"Page {item['page']}: '{item['text']}' at ({item['x0']:.1f}, {item['top']:.1f})")
            
            if len(result) > 100:
                click.echo(f"... and {len(result) - 100} more characters")
                
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@cli.command()
@click.argument("pdf_path", type=click.Path(exists=True))
@click.argument("output_path", type=click.Path())
@click.option("--json-only", is_flag=True, help="Export only JSON format")
@click.option("--excel-only", is_flag=True, help="Export only Excel format")
def export(pdf_path, output_path, json_only, excel_only):
    """Export course progress data from PDF to Excel and JSON files.
    
    By default, exports both Excel and JSON files. Use --json-only or --excel-only 
    to export only one format. The JSON file will have the same name as the output 
    path but with .json extension.
    """
    try:
        parser_instance = CourseProgressParser(pdf_path)
        click.echo(f"Parsing PDF: {pdf_path}")
        
        data = parser_instance.parse_course_data()
        
        # Generate file paths
        from pathlib import Path
        output_path_obj = Path(output_path)
        
        # Determine output formats
        export_excel = not json_only
        export_json = not excel_only
        
        if export_excel and export_json:
            # Both formats
            json_path = output_path_obj.with_suffix('.json')
            parser_instance.export_to_excel_and_json(str(output_path_obj), str(json_path), data)
        elif export_excel:
            # Excel only
            parser_instance.export_to_excel(output_path, data)
        elif export_json:
            # JSON only
            json_path = output_path_obj.with_suffix('.json')
            parser_instance.export_to_json(str(json_path), data)
        
        click.echo(f"Successfully exported {len(data)} records")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@cli.command()
@click.argument("json_path", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Output directory for chart files")
@click.option("--static", is_flag=True, help="Generate static PNG charts instead of interactive HTML")
@click.option("--dashboard", is_flag=True, help="Generate combined dashboard")
@click.option("--chart-type", type=click.Choice(['all', 'xp', 'task-type', 'weekly-daily', 'efficiency', 'weekday', 'daily-dist', 'dashboard']), 
              default='all', help="Specify chart type to generate")
def chart(json_path, output, static, dashboard, chart_type):
    """Generate charts from learning progress JSON data.

    Chart types: XP charts (cumulative and daily trends), task type distribution
    (dual pie charts: task count and XP), weekly/daily XP statistics, learning
    efficiency trend, average daily XP by weekday, daily XP distribution
    (histogram), and comprehensive dashboard.

    By default, generates all charts. Use --chart-type for specific charts.
    Use --static for PNG images instead of interactive HTML.
    """
    try:
        chart_gen = ChartGenerator(json_path)
        
        # Set output directory
        if output:
            output_dir = Path(output)
        else:
            output_dir = Path(json_path).parent
        
        output_dir.mkdir(exist_ok=True)
        
        click.echo(f"Generating charts from: {json_path}")
        click.echo(f"Output directory: {output_dir}")
        
        # Display basic statistics
        stats = chart_gen.get_xp_statistics()
        if stats:
            click.echo(f"\nXP Statistics:")
            click.echo(f"  Total XP: {stats['total_xp']:,}")
            click.echo(f"  Average Daily XP: {stats['average_daily_xp']:.1f}")
            click.echo(f"  Active Days: {stats['active_days']}/{stats['total_days']}")
            if stats['recent_trend']['direction'] != 'insufficient_data':
                trend_dir = stats['recent_trend']['direction']
                trend_pct = stats['recent_trend']['change_percent']
                click.echo(f"  Recent Trend: {trend_dir} ({trend_pct:+.1f}%)")
        
        generated_charts = []
        
        if dashboard or chart_type == 'all' or chart_type == 'xp':
            if dashboard:
                # Generate combined dashboard
                dashboard_path = chart_gen.generate_combined_xp_dashboard(str(output_dir / "xp_dashboard"))
                generated_charts.append(f"Dashboard: {dashboard_path}")
            else:
                # Generate XP charts
                cumulative_path = chart_gen.generate_cumulative_xp_chart(
                    str(output_dir / "cumulative_xp"), 
                    interactive=not static
                )
                daily_path = chart_gen.generate_daily_xp_chart(
                    str(output_dir / "daily_xp"), 
                    interactive=not static
                )
                generated_charts.append(f"Cumulative XP chart: {cumulative_path}")
                generated_charts.append(f"Daily XP chart: {daily_path}")
        
        if chart_type == 'all' or chart_type == 'task-type':
            task_type_path = chart_gen.generate_task_type_pie_chart(
                str(output_dir / "task_type_distribution"),
                interactive=not static
            )
            generated_charts.append(f"Task type distribution chart: {task_type_path}")
        
        if chart_type == 'all' or chart_type == 'weekly-daily':
            weekly_daily_path = chart_gen.generate_weekly_daily_stats_chart(
                str(output_dir / "weekly_daily_stats"),
                interactive=not static
            )
            generated_charts.append(f"Weekly/daily statistics chart: {weekly_daily_path}")
        
        if chart_type == 'all' or chart_type == 'efficiency':
            efficiency_path = chart_gen.generate_efficiency_trend_chart(
                str(output_dir / "efficiency_trend"),
                interactive=not static
            )
            generated_charts.append(f"Learning efficiency chart: {efficiency_path}")
        
        if chart_type == 'all' or chart_type == 'weekday':
            weekday_path = chart_gen.generate_weekday_distribution_chart(
                str(output_dir / "weekday_distribution"),
                interactive=not static
            )
            generated_charts.append(f"Average Daily XP by weekday chart: {weekday_path}")
        
        if chart_type == 'all' or chart_type == 'daily-dist':
            daily_dist_path = chart_gen.generate_daily_xp_distribution_chart(
                str(output_dir / "daily_xp_distribution"),
                interactive=not static
            )
            generated_charts.append(f"Daily XP distribution chart: {daily_dist_path}")
        
        if chart_type == 'all' or chart_type == 'dashboard':
            dashboard_path = chart_gen.generate_comprehensive_dashboard(
                str(output_dir / "comprehensive_dashboard")
            )
            generated_charts.append(f"Comprehensive dashboard: {dashboard_path}")
        
        # Display generated charts
        if generated_charts:
            click.echo(f"\nGenerated charts:")
            for chart_info in generated_charts:
                click.echo(f"  {chart_info}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@cli.command()
@click.argument("json_path", type=click.Path(exists=True))
def stats(json_path):
    """Display XP statistics from learning progress JSON data."""
    try:
        chart_gen = ChartGenerator(json_path)
        stats = chart_gen.get_xp_statistics()
        
        if not stats:
            click.echo("No statistics available - no data found in JSON file")
            return
        
        click.echo(f"XP Statistics for {Path(json_path).stem}")
        click.echo("=" * 50)
        click.echo(f"Total XP: {stats['total_xp']:,}")
        click.echo(f"Average Daily XP: {stats['average_daily_xp']:.1f}")
        click.echo(f"Maximum Daily XP: {stats['max_daily_xp']:,}")
        click.echo(f"Minimum Daily XP: {stats['min_daily_xp']:,}")
        click.echo(f"Active Days: {stats['active_days']}/{stats['total_days']}")
        
        if stats['date_range']['start'] and stats['date_range']['end']:
            click.echo(f"Date Range: {stats['date_range']['start']} to {stats['date_range']['end']}")
        
        if stats['recent_trend']['direction'] != 'insufficient_data':
            trend = stats['recent_trend']
            click.echo(f"\nRecent Trend (7-day comparison):")
            click.echo(f"  Direction: {trend['direction']}")
            click.echo(f"  Change: {trend['change_percent']:+.1f}%")
            click.echo(f"  Recent Average: {trend['recent_average']:.1f} XP/day")
            click.echo(f"  Previous Average: {trend['previous_average']:.1f} XP/day")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


def main():
    """Entry point for the application."""
    cli()


if __name__ == "__main__":
    main()