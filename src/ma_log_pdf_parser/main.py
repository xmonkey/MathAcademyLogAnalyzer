import click
import json
from pathlib import Path
from .pdf_parser import PDFParser
from .course_parser import CourseProgressParser
from .chart_generator import ChartGenerator
from . import __version__


@click.group()
def cli():
    """Math Academy Log Analyzer - Complete PDF analysis toolkit.

    This tool analyzes Math Academy activity log PDFs and generates comprehensive
    reports including Excel spreadsheets, JSON data, interactive charts, and
    static visualizations.
    """
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
@click.option("--chart-type", type=click.Choice(['all', 'xp', 'task-type', 'multi-level', 'efficiency', 'weekday', 'daily-dist', 'dashboard']),
              default='all', help="Specify chart type to generate")
def chart(json_path, output, static, dashboard, chart_type):
    """Generate charts from learning progress JSON data.

    Chart types: XP charts (cumulative and daily trends), task type distribution
    (dual pie charts: task count and XP), multi-level statistics (monthly/weekly/daily
    comparison), learning efficiency trend, average daily XP by weekday, daily XP
    distribution (histogram), and comprehensive dashboard.

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
        
        if chart_type == 'all' or chart_type == 'multi-level':
            multi_level_path = chart_gen.generate_multi_level_stats_chart(
                str(output_dir / "multi_level_stats"),
                interactive=not static
            )
            generated_charts.append(f"Multi-level statistics chart: {multi_level_path}")
        
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
@click.argument("pdf_path", type=click.Path(exists=True))
@click.option("--output-dir", "-o", type=click.Path(), help="Output directory for all generated files")
@click.option("--name", "-n", help="Base name for generated files (defaults to PDF filename)")
@click.option("--static-only", is_flag=True, help="Generate only static PNG charts (no interactive HTML)")
@click.option("--interactive-only", is_flag=True, help="Generate only interactive HTML charts (no static PNG)")
@click.option("--data-only", is_flag=True, help="Generate only data files (Excel and JSON, no charts)")
@click.option("--charts-only", is_flag=True, help="Generate only chart files (no Excel or JSON)")
def generate_all(pdf_path, output_dir, name, static_only, interactive_only, data_only, charts_only):
    """Generate all output formats from PDF in one command.

    This command processes a Math Academy activity log PDF and generates:
    - Excel file (.xlsx) with course progress data
    - JSON file with parsed data for chart generation
    - Interactive HTML charts (for web viewing)
    - Static PNG charts (for reports/documents)

    By default, generates all formats. Use options to control output types.
    """
    try:
        import time
        start_time = time.time()

        # Setup paths
        pdf_path_obj = Path(pdf_path)
        if output_dir:
            output_path = Path(output_dir)
        else:
            output_path = pdf_path_obj.parent

        # Create output directory if it doesn't exist
        output_path.mkdir(exist_ok=True)

        # Determine base filename
        if name:
            base_name = name
        else:
            base_name = pdf_path_obj.stem

        click.echo(f"Processing PDF: {pdf_path}")
        click.echo(f"Output directory: {output_path}")
        click.echo(f"Base filename: {base_name}")
        click.echo()

        # Determine what to generate
        generate_data = not charts_only
        generate_charts = not data_only
        generate_interactive = not static_only
        generate_static = not interactive_only

        generated_files = []

        # Step 1: Parse course data from PDF
        if generate_data or generate_charts:
            click.echo("Step 1: Parsing course data from PDF...")
            parser_instance = CourseProgressParser(pdf_path)
            data = parser_instance.parse_course_data()

            if not data:
                click.echo("No course data found in PDF. Cannot proceed.", err=True)
                return

            click.echo(f"  ✓ Parsed {len(data)} activity records")

        # Step 2: Generate data files (Excel and JSON)
        if generate_data:
            click.echo("Step 2: Generating data files...")

            # Generate Excel file
            excel_path = output_path / f"{base_name}.xlsx"
            parser_instance.export_to_excel(str(excel_path), data)
            generated_files.append(f"Excel: {excel_path}")
            click.echo(f"  ✓ Excel file: {excel_path}")

            # Generate JSON file
            json_path = output_path / f"{base_name}.json"
            parser_instance.export_to_json(str(json_path), data)
            generated_files.append(f"JSON: {json_path}")
            click.echo(f"  ✓ JSON file: {json_path}")

        # Step 3: Generate charts
        if generate_charts:
            click.echo("Step 3: Generating charts...")

            # Use JSON file for chart generation
            json_file_path = output_path / f"{base_name}.json" if generate_data else None
            if not json_file_path or not json_file_path.exists():
                # If JSON wasn't generated in step 2, create temporary JSON
                json_file_path = output_path / f"{base_name}_temp.json"
                parser_instance.export_to_json(str(json_file_path), data)
                generated_files.append(f"Temporary JSON: {json_file_path}")

            chart_gen = ChartGenerator(str(json_file_path))

            # Create charts subdirectory
            charts_dir = output_path / "charts"
            charts_dir.mkdir(exist_ok=True)

            # Generate interactive charts
            if generate_interactive:
                click.echo("  Generating interactive HTML charts...")

                # Comprehensive dashboard
                dashboard_path = chart_gen.generate_comprehensive_dashboard(
                    str(charts_dir / f"{base_name}_dashboard")
                )
                generated_files.append(f"Interactive Dashboard: {dashboard_path}")

                # Individual charts
                cumulative_path = chart_gen.generate_cumulative_xp_chart(
                    str(charts_dir / f"{base_name}_cumulative_xp"),
                    interactive=True
                )
                generated_files.append(f"Interactive Cumulative XP: {cumulative_path}")

                daily_path = chart_gen.generate_daily_xp_chart(
                    str(charts_dir / f"{base_name}_daily_xp"),
                    interactive=True
                )
                generated_files.append(f"Interactive Daily XP: {daily_path}")

                task_type_path = chart_gen.generate_task_type_pie_chart(
                    str(charts_dir / f"{base_name}_task_type"),
                    interactive=True
                )
                generated_files.append(f"Interactive Task Type: {task_type_path}")

                # Generate additional interactive charts
                multi_level_path = chart_gen.generate_multi_level_stats_chart(
                    str(charts_dir / f"{base_name}_multi_level_stats"),
                    interactive=True
                )
                generated_files.append(f"Interactive Multi-level Stats: {multi_level_path}")

                efficiency_path = chart_gen.generate_efficiency_trend_chart(
                    str(charts_dir / f"{base_name}_efficiency_trend"),
                    interactive=True
                )
                generated_files.append(f"Interactive Efficiency Trend: {efficiency_path}")

                weekday_path = chart_gen.generate_weekday_distribution_chart(
                    str(charts_dir / f"{base_name}_weekday_distribution"),
                    interactive=True
                )
                generated_files.append(f"Interactive Weekday Distribution: {weekday_path}")

                daily_dist_path = chart_gen.generate_daily_xp_distribution_chart(
                    str(charts_dir / f"{base_name}_daily_xp_distribution"),
                    interactive=True
                )
                generated_files.append(f"Interactive Daily XP Distribution: {daily_dist_path}")

                click.echo(f"    ✓ Generated interactive charts in {charts_dir}")

            # Generate static charts
            if generate_static:
                click.echo("  Generating static PNG charts...")

                # Individual charts
                static_cumulative_path = chart_gen.generate_cumulative_xp_chart(
                    str(charts_dir / f"{base_name}_cumulative_xp_static"),
                    interactive=False
                )
                generated_files.append(f"Static Cumulative XP: {static_cumulative_path}")

                static_daily_path = chart_gen.generate_daily_xp_chart(
                    str(charts_dir / f"{base_name}_daily_xp_static"),
                    interactive=False
                )
                generated_files.append(f"Static Daily XP: {static_daily_path}")

                static_task_type_path = chart_gen.generate_task_type_pie_chart(
                    str(charts_dir / f"{base_name}_task_type_static"),
                    interactive=False
                )
                generated_files.append(f"Static Task Type: {static_task_type_path}")

                # Generate additional static charts
                static_multi_level_path = chart_gen.generate_multi_level_stats_chart(
                    str(charts_dir / f"{base_name}_multi_level_stats_static"),
                    interactive=False
                )
                generated_files.append(f"Static Multi-level Stats: {static_multi_level_path}")

                static_efficiency_path = chart_gen.generate_efficiency_trend_chart(
                    str(charts_dir / f"{base_name}_efficiency_trend_static"),
                    interactive=False
                )
                generated_files.append(f"Static Efficiency Trend: {static_efficiency_path}")

                static_weekday_path = chart_gen.generate_weekday_distribution_chart(
                    str(charts_dir / f"{base_name}_weekday_distribution_static"),
                    interactive=False
                )
                generated_files.append(f"Static Weekday Distribution: {static_weekday_path}")

                static_daily_dist_path = chart_gen.generate_daily_xp_distribution_chart(
                    str(charts_dir / f"{base_name}_daily_xp_distribution_static"),
                    interactive=False
                )
                generated_files.append(f"Static Daily XP Distribution: {static_daily_dist_path}")

                click.echo(f"    ✓ Generated static charts in {charts_dir}")

            # Clean up temporary JSON if created
            if not generate_data and json_file_path.name.endswith("_temp.json") and json_file_path.exists():
                json_file_path.unlink()
                generated_files = [f for f in generated_files if "Temporary JSON" not in f]

        # Calculate processing time
        end_time = time.time()
        processing_time = end_time - start_time

        # Summary
        click.echo()
        click.echo("=" * 60)
        click.echo("GENERATION COMPLETE")
        click.echo("=" * 60)
        click.echo(f"Processing time: {processing_time:.1f} seconds")
        click.echo(f"Total files generated: {len(generated_files)}")
        click.echo()
        click.echo("Generated files:")
        for file_info in generated_files:
            click.echo(f"  • {file_info}")

        # Show statistics
        if generate_data or generate_charts:
            stats = chart_gen.get_xp_statistics() if generate_charts else None
            if stats:
                click.echo()
                click.echo("XP Statistics:")
                click.echo(f"  Total XP: {stats['total_xp']:,}")
                click.echo(f"  Average Daily XP: {stats['average_daily_xp']:.1f}")
                click.echo(f"  Active Days: {stats['active_days']}/{stats['total_days']}")

        click.echo()
        click.echo(f"All files saved to: {output_path}")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        import traceback
        click.echo(f"Debug info: {traceback.format_exc()}", err=True)


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