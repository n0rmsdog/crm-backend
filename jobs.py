import typer
from pymongo import MongoClient
from rich.console import Console
from rich.table import Table
from datetime import datetime, timedelta

app = typer.Typer()
console = Console()

# Connect to MongoDB Atlas
client = MongoClient("mongodb+srv://n0rms:2m6dUSyTbwvfpbFq@cluster0.nf19p.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["crm_backend"]  # Use the "crm_backend" database
jobs_collection = db["jobs"]  # Create or connect to the "jobs" collection

@app.command()
def add(
    customer_email: str,
    description: str,
    assigned_to: str = typer.Option(None, "--assigned-to", help="Assign job to an employee"),
    status: str = "Pending",
    due_date: str = typer.Option(None, "--due-date", help="Job due date (YYYY-MM-DD)")
):
    """Assign a job with an optional due date"""
    try:
        due_date_obj = datetime.strptime(due_date, "%Y-%m-%d") if due_date else None
    except ValueError:
        console.print("[bold red]Error: Invalid date format. Use YYYY-MM-DD.[/bold red]")
        return
    
    job = {
        "customer_email": customer_email,
        "description": description,
        "assigned_to": assigned_to if assigned_to else "Not Assigned",
        "status": status,
        "due_date": due_date_obj,
        "completion_notes": None,
        "completed_at": None,
        "created_at": datetime.now().astimezone()
    }
    jobs_collection.insert_one(job)
    console.print(f"[bold green]Job added for {customer_email} (Assigned to: {assigned_to if assigned_to else 'Not Assigned'})![/bold green]")

@app.command()
def list():
    """List all jobs"""
    jobs = jobs_collection.find().sort("due_date", 1)
    
    table = Table(title="Jobs")
    table.add_column("Customer Email", style="cyan")
    table.add_column("Description", style="magenta")
    table.add_column("Assigned To", style="blue")
    table.add_column("Status", style="yellow")
    table.add_column("Due Date", style="red")
    table.add_column("Completed At", style="green")

    for job in jobs:
        assigned_to = job.get("assigned_to", "Not Assigned")
        due_date = job["due_date"].strftime("%Y-%m-%d") if job.get("due_date") else "No Due Date"
        completed_at = job["completed_at"].strftime("%Y-%m-%d %H:%M") if job.get("completed_at") else "Not Completed"
        table.add_row(job["customer_email"], job["description"], assigned_to, job["status"], due_date, completed_at)

    console.print(table)

@app.command()
def complete(email: str, notes: str = typer.Option(None, "--notes", help="Completion notes")):
    """Mark a job as completed with optional notes"""
    result = jobs_collection.update_one(
        {"customer_email": email, "status": "Pending"},
        {"$set": {"status": "Completed", "completed_at": datetime.now().astimezone(), "completion_notes": notes}}
    )
    
    if result.matched_count == 0:
        console.print("[bold red]Error: No pending job found for this customer![/bold red]")
    else:
        console.print(f"[bold green]Job for {email} marked as Completed![/bold green]")

@app.command(name="view-notes")  # Force command name without changing function name
def view_notes(email: str):
    """View job completion notes"""
    job = jobs_collection.find_one({"customer_email": email})

    if job:
        notes = job.get("completion_notes", "No notes available")
        console.print(f"[bold cyan]Completion Notes for {email}: {notes}[/bold cyan]")
    else:
        console.print("[bold red]Error: Job not found![/bold red]")

@app.command(name="list-assigned")
def list_assigned(email: str):
    """List jobs assigned to a specific employee"""
    jobs = jobs_collection.find({"assigned_to": email}).sort("due_date", 1)

    table = Table(title=f"Jobs Assigned to {email}")
    table.add_column("Customer Email", style="cyan")
    table.add_column("Description", style="magenta")
    table.add_column("Status", style="yellow")
    table.add_column("Due Date", style="red")

    for job in jobs:
        due_date = job["due_date"].strftime("%Y-%m-%d") if job.get("due_date") else "No Due Date"
        table.add_row(job["customer_email"], job["description"], job["status"], due_date)

    console.print(table)

@app.command()
def reminders(days: int = 7):
    """List jobs that are due within the next N days"""
    now = datetime.now().astimezone()
    upcoming_date = now + timedelta(days=days)
    
    jobs = jobs_collection.find({"due_date": {"$gte": now, "$lte": upcoming_date}}).sort("due_date", 1)

    table = Table(title=f"Upcoming Jobs in Next {days} Days")
    table.add_column("Customer Email", style="cyan")
    table.add_column("Description", style="magenta")
    table.add_column("Assigned To", style="blue")
    table.add_column("Due Date", style="red")

    for job in jobs:
        due_date = job["due_date"].strftime("%Y-%m-%d") if job.get("due_date") else "No Due Date"
        table.add_row(job["customer_email"], job["description"], job.get("assigned_to", "Not Assigned"), due_date)

    console.print(table)

@app.command()
def update(email: str, new_status: str):
    """Update job status"""
    result = jobs_collection.update_one({"customer_email": email}, {"$set": {"status": new_status}})
    
    if result.matched_count == 0:
        console.print("[bold red]Error: Job not found![/bold red]")
    else:
        console.print(f"[bold green]Job status updated for {email}![/bold green]")

@app.command()
def delete(email: str):
    """Delete a job by customer email"""
    result = jobs_collection.delete_one({"customer_email": email})
    
    if result.deleted_count == 0:
        console.print("[bold red]Error: Job not found![/bold red]")
    else:
        console.print(f"[bold green]Job for {email} deleted![/bold green]")

if __name__ == "__main__":
    app()

