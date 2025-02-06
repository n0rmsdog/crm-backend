import typer
from pymongo import MongoClient
from rich.console import Console
from rich.table import Table
from datetime import datetime

app = typer.Typer()
console = Console()

# Connect to MongoDB Atlas
client = MongoClient("mongodb+srv://n0rms:2m6dUSyTbwvfpbFq@cluster0.nf19p.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["crm_backend"]  # Use the "crm_backend" database
calendar_collection = db["calendar"]  # Create or connect to "calendar" collection

@app.command()
def schedule(email: str, description: str, date: str):
    """Schedule a job for a specific date (Format: YYYY-MM-DD)"""
    try:
        job_date = datetime.strptime(date, "%Y-%m-%d")
        job = {"customer_email": email, "description": description, "date": job_date}
        calendar_collection.insert_one(job)
        console.print(f"[bold green]Job scheduled for {email} on {date}![/bold green]")
    except ValueError:
        console.print("[bold red]Error: Date must be in YYYY-MM-DD format.[/bold red]")

@app.command()
def list():
    """List all scheduled jobs"""
    jobs = calendar_collection.find().sort("date")
    
    table = Table(title="Scheduled Jobs")
    table.add_column("Customer Email", style="cyan")
    table.add_column("Description", style="magenta")
    table.add_column("Date", style="yellow")

    for job in jobs:
        table.add_row(job["customer_email"], job["description"], job["date"].strftime("%Y-%m-%d"))

    console.print(table)

@app.command()
def delete(email: str, date: str):
    """Delete a scheduled job"""
    try:
        job_date = datetime.strptime(date, "%Y-%m-%d")
        result = calendar_collection.delete_one({"customer_email": email, "date": job_date})
        
        if result.deleted_count == 0:
            console.print("[bold red]Error: No matching job found![/bold red]")
        else:
            console.print(f"[bold green]Scheduled job for {email} on {date} deleted![/bold green]")
    except ValueError:
        console.print("[bold red]Error: Date must be in YYYY-MM-DD format.[/bold red]")

if __name__ == "__main__":
    app()

