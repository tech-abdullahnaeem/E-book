#!/usr/bin/env python3
"""
Advanced E-Book Generator
A comprehensive, intelligent e-book creation system with enhanced features
"""

import os
import sys
import time
from typing import Optional, List
from pathlib import Path

import typer
from rich.console import Console
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
from rich.panel import Panel
from rich.table import Table
from rich import box
from rich.markdown import Markdown
from dotenv import load_dotenv
import yaml

# Import custom modules
from utils.content_generator import ContentGenerator
from utils.research_engine import ResearchEngine
from utils.citation_manager import CitationManager
from utils.pdf_builder import PDFBuilder

# Load environment variables
load_dotenv()

# Initialize Rich console
console = Console()
app = typer.Typer(help="Advanced E-Book Generator with AI")

# Load configuration
def load_config():
    """Load configuration from config.yaml"""
    config_path = Path(__file__).parent / "config.yaml"
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

CONFIG = load_config()


def display_banner():
    """Display beautiful ASCII banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║        🚀 ADVANCED E-BOOK GENERATOR v2.0 🚀                  ║
    ║                                                               ║
    ║        AI-Powered • Research-Backed • Professional           ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")


def select_genre() -> str:
    """Interactive genre selection with rich display"""
    console.print("\n[bold cyan]📚 Step 1: Select Your Book Genre[/bold cyan]\n")
    
    table = Table(title="Available Genres", box=box.ROUNDED, show_header=True, header_style="bold magenta")
    table.add_column("No.", style="cyan", justify="center", width=6)
    table.add_column("Genre", style="green", width=20)
    table.add_column("Tone", style="yellow", width=30)
    
    genres = list(CONFIG['genres'].keys())
    for idx, genre in enumerate(genres, 1):
        genre_config = CONFIG['genres'][genre]
        table.add_row(str(idx), genre.title(), genre_config['tone'])
    
    console.print(table)
    
    choice = IntPrompt.ask(
        "\n[bold yellow]Select genre number[/bold yellow]",
        default=1,
        show_default=True
    )
    
    if 1 <= choice <= len(genres):
        selected_genre = genres[choice - 1]
        console.print(f"\n✓ Selected: [bold green]{selected_genre.title()}[/bold green]")
        return selected_genre
    else:
        console.print("[bold red]Invalid choice. Using 'technology' as default.[/bold red]")
        return "technology"


def select_book_length() -> dict:
    """Interactive book length selection"""
    console.print("\n[bold cyan]📏 Step 2: Choose Book Length[/bold cyan]\n")
    
    table = Table(box=box.ROUNDED, show_header=True, header_style="bold magenta")
    table.add_column("No.", style="cyan", justify="center", width=6)
    table.add_column("Length", style="green", width=12)
    table.add_column("Chapters", style="yellow", width=15)
    table.add_column("Words/Section", style="blue", width=15)
    table.add_column("Subsections", style="magenta", width=15)
    
    lengths = list(CONFIG['book_length'].keys())
    for idx, length in enumerate(lengths, 1):
        length_config = CONFIG['book_length'][length]
        chapters = f"{length_config['min_chapters']}-{length_config['max_chapters']}"
        table.add_row(
            str(idx),
            length.title(),
            chapters,
            str(length_config['words_per_section']),
            str(length_config['subsections'])
        )
    
    console.print(table)
    
    choice = IntPrompt.ask(
        "\n[bold yellow]Select length number[/bold yellow]",
        default=2,
        show_default=True
    )
    
    if 1 <= choice <= len(lengths):
        selected_length = lengths[choice - 1]
        console.print(f"\n✓ Selected: [bold green]{selected_length.title()}[/bold green]")
        return CONFIG['book_length'][selected_length]
    else:
        console.print("[bold red]Invalid choice. Using 'medium' as default.[/bold red]")
        return CONFIG['book_length']['medium']


def customize_chapters(length_config: dict) -> int:
    """Let user choose exact number of chapters"""
    console.print("\n[bold cyan]📖 Step 3: Customize Chapter Count[/bold cyan]\n")
    
    min_chapters = length_config['min_chapters']
    max_chapters = length_config['max_chapters']
    
    num_chapters = IntPrompt.ask(
        f"[bold yellow]How many chapters? ({min_chapters}-{max_chapters})[/bold yellow]",
        default=min_chapters
    )
    
    if min_chapters <= num_chapters <= max_chapters:
        console.print(f"\n✓ Creating [bold green]{num_chapters} chapters[/bold green]")
        return num_chapters
    else:
        console.print(f"[yellow]Adjusting to valid range: {min_chapters}[/yellow]")
        return min_chapters


def select_optional_sections() -> dict:
    """Let user select optional front matter and back matter sections"""
    console.print("\n[bold cyan]📑 Step 4: Optional Book Sections[/bold cyan]\n")
    
    selected_sections = {
        'front_matter': [],
        'back_matter': []
    }
    
    # Front Matter Selection
    console.print("[bold yellow]Front Matter (before main content):[/bold yellow]")
    front_matter_options = CONFIG['front_matter_sections']
    
    for section in front_matter_options:
        include = Confirm.ask(f"  Include [bold green]{section}[/bold green]?", default=False)
        if include:
            selected_sections['front_matter'].append(section)
    
    console.print()
    
    # Back Matter Selection
    console.print("[bold yellow]Back Matter (after main content):[/bold yellow]")
    back_matter_options = CONFIG['back_matter_sections']
    
    for section in back_matter_options:
        include = Confirm.ask(f"  Include [bold green]{section}[/bold green]?", default=False)
        if include:
            selected_sections['back_matter'].append(section)
    
    total_sections = len(selected_sections['front_matter']) + len(selected_sections['back_matter'])
    
    if total_sections > 0:
        all_selected = selected_sections['front_matter'] + selected_sections['back_matter']
        console.print(f"\n✓ Added {total_sections} optional sections: [bold green]{', '.join(all_selected)}[/bold green]")
    else:
        console.print("\n[yellow]No optional sections selected[/yellow]")
    
    return selected_sections


def select_citation_style() -> str:
    """Select citation style"""
    console.print("\n[bold cyan]📝 Step 5: Citation Style[/bold cyan]\n")
    
    styles = CONFIG['citation_styles']
    
    table = Table(box=box.ROUNDED)
    table.add_column("No.", style="cyan", justify="center")
    table.add_column("Citation Style", style="green")
    
    for idx, style in enumerate(styles, 1):
        table.add_row(str(idx), style)
    
    console.print(table)
    
    choice = IntPrompt.ask(
        "\n[bold yellow]Select citation style[/bold yellow]",
        default=1
    )
    
    if 1 <= choice <= len(styles):
        selected_style = styles[choice - 1]
        console.print(f"\n✓ Using [bold green]{selected_style}[/bold green] style")
        return selected_style
    else:
        console.print("[yellow]Using APA as default[/yellow]")
        return "APA"


def configure_content_features() -> dict:
    """Configure content enhancement features"""
    console.print("\n[bold cyan]✨ Step 6: Content Enhancement Features[/bold cyan]\n")
    
    features = {}
    feature_descriptions = {
        "case_studies": "Real-world case studies",
        "quiz_questions": "Quiz questions at chapter ends",
        "summary_boxes": "Key point summary boxes",
        "did_you_know": "'Did You Know?' fact boxes",
        "expert_quotes": "Expert quotes and insights",
        "real_world_examples": "Real-world examples"
    }
    
    for key, description in feature_descriptions.items():
        default_value = CONFIG['content_features'].get(key, True)
        features[key] = Confirm.ask(
            f"Include [bold green]{description}[/bold green]?",
            default=default_value
        )
    
    enabled_features = [desc for key, desc in feature_descriptions.items() if features[key]]
    if enabled_features:
        console.print(f"\n✓ Enabled: [bold green]{', '.join(enabled_features)}[/bold green]")
    
    return features


@app.command()
def create(
    topic: Optional[str] = typer.Option(None, "--topic", "-t", help="E-book topic"),
    output_dir: Optional[str] = typer.Option("output", "--output", "-o", help="Output directory")
):
    """
    Create a new e-book with advanced AI generation
    """
    display_banner()
    
    # Step 0: Get topic if not provided
    if not topic:
        console.print("\n[bold cyan]🎯 What's your e-book about?[/bold cyan]")
        topic = Prompt.ask("[bold yellow]Enter your e-book topic[/bold yellow]")
    
    if not topic or len(topic) < 3:
        console.print("[bold red]Error: Topic must be at least 3 characters long[/bold red]")
        raise typer.Exit(code=1)
    
    console.print(Panel(
        f"[bold white]{topic}[/bold white]",
        title="📖 E-Book Topic",
        border_style="green"
    ))
    
    # Interactive configuration
    genre = select_genre()
    length_config = select_book_length()
    num_chapters = customize_chapters(length_config)
    optional_sections = select_optional_sections()
    citation_style = select_citation_style()
    content_features = configure_content_features()
    
    # Final confirmation
    console.print("\n[bold cyan]📋 Configuration Summary[/bold cyan]\n")
    summary_table = Table(box=box.ROUNDED)
    summary_table.add_column("Setting", style="cyan", width=25)
    summary_table.add_column("Value", style="green")
    
    summary_table.add_row("Topic", topic)
    summary_table.add_row("Genre", genre.title())
    summary_table.add_row("Chapters", str(num_chapters))
    summary_table.add_row("Words per Section", str(length_config['words_per_section']))
    summary_table.add_row("Subsections", str(length_config['subsections']))
    
    front_matter_list = optional_sections['front_matter']
    back_matter_list = optional_sections['back_matter']
    summary_table.add_row("Front Matter", ", ".join(front_matter_list) if front_matter_list else "None")
    summary_table.add_row("Back Matter", ", ".join(back_matter_list) if back_matter_list else "None")
    summary_table.add_row("Citation Style", citation_style)
    
    console.print(summary_table)
    
    if not Confirm.ask("\n[bold yellow]Proceed with e-book generation?[/bold yellow]", default=True):
        console.print("[yellow]Cancelled.[/yellow]")
        raise typer.Exit()
    
    # Start generation process
    console.print("\n[bold green]🚀 Starting E-Book Generation...[/bold green]\n")
    
    try:
        # Initialize generators
        content_gen = ContentGenerator(
            api_key=os.getenv('GEMINI_API_KEY'),
            genre=genre,
            config=CONFIG
        )
        
        research_engine = ResearchEngine(
            api_key=os.getenv('GOOGLE_API_KEY'),
            search_engine_id=os.getenv('SEARCH_ENGINE_ID')
        )
        
        citation_manager = CitationManager(style=citation_style)
        
        # Phase 1: Generate Outline
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeRemainingColumn(),
            console=console
        ) as progress:
            
            task1 = progress.add_task("[cyan]Generating outline...", total=1)
            outline = content_gen.generate_outline(topic, num_chapters, length_config)
            progress.update(task1, advance=1)
            
            console.print("\n✓ [bold green]Outline generated successfully![/bold green]\n")
            
            # Display outline
            outline_table = Table(title="📑 Book Outline", box=box.ROUNDED)
            outline_table.add_column("Section", style="cyan", width=50)
            outline_table.add_column("Type", style="green", width=20)
            
            for section in outline:
                outline_table.add_row(section['title'], section['type'])
            
            console.print(outline_table)
            console.print()
            
            # Phase 2: Research Integration
            task2 = progress.add_task("[cyan]Conducting research...", total=len(outline))
            research_data = {}
            
            for section in outline:
                if section['type'] in ['chapter', 'introduction']:
                    search_query = f"{topic} {section['title']}"
                    research_results = research_engine.search(search_query, max_results=5)
                    research_data[section['title']] = research_results
                    progress.update(task2, advance=1)
                    time.sleep(2)  # Rate limiting
                else:
                    progress.update(task2, advance=1)
            
            console.print("\n✓ [bold green]Research completed![/bold green]\n")
            
            # Phase 3: Content Generation
            task3 = progress.add_task("[cyan]Generating content...", total=len(outline))
            generated_content = []
            
            for section in outline:
                console.print(f"[yellow]Writing: {section['title']}...[/yellow]")
                
                research_context = research_data.get(section['title'], [])
                
                content = content_gen.generate_section(
                    topic=topic,
                    section=section,
                    research_context=research_context,
                    features=content_features,
                    words_target=length_config['words_per_section']
                )
                
                generated_content.append({
                    'section': section,
                    'content': content
                })
                
                progress.update(task3, advance=1)
                time.sleep(CONFIG['api_settings']['rate_limit_delay'])
            
            console.print("\n✓ [bold green]Content generation completed![/bold green]\n")
            
            # Phase 4: Generate Front Matter & Back Matter
            all_optional = optional_sections['front_matter'] + optional_sections['back_matter']
            if all_optional:
                task4 = progress.add_task("[cyan]Generating front & back matter...", total=len(all_optional))
                
                for section_name in all_optional:
                    console.print(f"[yellow]Creating: {section_name}...[/yellow]")
                    
                    optional_content = content_gen.generate_optional_section(
                        topic=topic,
                        section_name=section_name,
                        main_content=generated_content,
                        citation_manager=citation_manager
                    )
                    
                    # Determine if front matter or back matter
                    section_type = 'front_matter' if section_name in optional_sections['front_matter'] else 'back_matter'
                    
                    generated_content.append({
                        'section': {'title': section_name, 'type': section_type},
                        'content': optional_content
                    })
                    
                    progress.update(task4, advance=1)
                    time.sleep(CONFIG['api_settings']['rate_limit_delay'])
                
                console.print("\n✓ [bold green]Front & back matter completed![/bold green]\n")
            
            # Phase 5: Compile PDF
            task5 = progress.add_task("[cyan]Compiling PDF...", total=1)
            
            pdf_builder = PDFBuilder(config=CONFIG)
            output_path = pdf_builder.build(
                topic=topic,
                genre=genre,
                content=generated_content,
                citation_manager=citation_manager,
                output_dir=output_dir
            )
            
            progress.update(task5, advance=1)
        
        # Success message
        console.print("\n")
        console.print(Panel(
            f"[bold green]✓ E-Book successfully created![/bold green]\n\n"
            f"📄 Output: [cyan]{output_path}[/cyan]\n"
            f"📊 Chapters: {num_chapters}\n"
            f"📝 Total Sections: {len(generated_content)}",
            title="🎉 Success!",
            border_style="green",
            box=box.DOUBLE
        ))
        
    except Exception as e:
        console.print(f"\n[bold red]Error: {str(e)}[/bold red]")
        console.print_exception(show_locals=True)
        raise typer.Exit(code=1)


@app.command()
def version():
    """Display version information"""
    console.print(f"\n[bold cyan]Advanced E-Book Generator[/bold cyan]")
    console.print(f"Version: [green]{CONFIG['app']['version']}[/green]")
    console.print(f"Author: [yellow]{CONFIG['app']['author']}[/yellow]\n")


if __name__ == "__main__":
    app()
