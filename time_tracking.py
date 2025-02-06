import typer
from pymongo import MongoClient
from rich.console import Console
from datetime import datetime
import random

app = typer.Typer()
console = Console()

# Connect to MongoDB Atlas
client = MongoClient("mongodb+srv://n0rms:2m6dUSyTbwvfpbFq@cluster0.nf19p.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["crm_backend"]  # Use the "crm_backend" database
time_tracking_collection = db["time_tracking"]  # Create or connect to "time_tracking" collection

def get_random_location():
    """Simulates a GPS location (latitude, longitude)"""
    lat = round(random.uniform(-90, 90), 6)
    lon = round(random.uniform(-180, 180), 6)
    return f"{lat}, {lon}"

@app.command()
def clock_in(email: str):
    """Clock in an employee with GPS location"""
    now = datetime.now().astimezone()
    location = get_random_location()

    entry = {
        "email": email,
        "clock_in": now,
        "clock_out": None,
        "location_in": location,
        "location_out": None
    }
    time_tracking_collection.insert_one(entry)
    console.print(f"[bold green]{email} clocked in at {now} (Location: {location})[/bold green]")

@app.command()
def clock_out(email: str):
    """Clock out an employee with GPS location"""
    now = datetime.now().astimezone()
    location = get_random_location()

    result = time_tracking_collection.find_one_and_update(
        {"email": email, "clock_out": None},
        {"$set": {"clock_out": now, "location_out": location}}
    )

    if result:
        console.print(f"[bold green]{email} clocked out at {now} (Location: {location})[/bold green]")
    else:
        console.print("[bold red]Error: No active clock-in found for this user![/bold red]")

@app.command()
def list():
    """List all time tracking entries"""
    entries = time_tracking_collection.find()
    
    for entry in entries:
        console.print(f"{entry['email']} - In: {entry['clock_in']} (Loc: {entry['location_in']}), "
                      f"Out: {entry['clock_out']} (Loc: {entry['location_out']})")

if __name__ == "__main__":
    app()

