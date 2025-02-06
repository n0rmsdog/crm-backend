import typer
from pymongo import MongoClient
from rich.console import Console
from rich.table import Table

app = typer.Typer()
console = Console()

# Connect to MongoDB Atlas
client = MongoClient("mongodb+srv://n0rms:2m6dUSyTbwvfpbFq@cluster0.nf19p.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["crm_backend"]  # Create or connect to the "crm_backend" database
customers_collection = db["customers"]  # Create or connect to the "customers" collection

@app.command()
def add(name: str, email: str):
    """Add a new customer"""
    if customers_collection.find_one({"email": email}):
        console.print("[bold red]Error: Email already exists![/bold red]")
        return

    customer = {"name": name, "email": email}
    customers_collection.insert_one(customer)
    console.print(f"[bold green]Customer {name} added![/bold green]")

@app.command()
def list():
    """List all customers"""
    customers = customers_collection.find()
    
    table = Table(title="Customers")
    table.add_column("Name", style="magenta")
    table.add_column("Email", style="yellow")

    for customer in customers:
        table.add_row(customer["name"], customer["email"])

    console.print(table)

@app.command()
def delete(email: str):
    """Delete a customer by email"""
    result = customers_collection.delete_one({"email": email})
    
    if result.deleted_count == 0:
        console.print("[bold red]Error: Customer not found![/bold red]")
    else:
        console.print(f"[bold green]Customer {email} deleted![/bold green]")

if __name__ == "__main__":
    app()

