import typer
from pymongo import MongoClient
from rich.console import Console
from rich.table import Table

app = typer.Typer()
console = Console()

# Connect to MongoDB Atlas
client = MongoClient("mongodb+srv://n0rms:2m6dUSyTbwvfpbFq@cluster0.nf19p.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["crm_backend"]  # Use the "crm_backend" database
users_collection = db["users"]  # Create or connect to the "users" collection

# Roles available in the system
ROLES = ["Employee", "Manager"]

@app.command()
def create(email: str, name: str, role: str):
    """Create a new user with a specific role"""
    role = role.capitalize()
    if role not in ROLES:
        console.print("[bold red]Error: Role must be 'Employee' or 'Manager'[/bold red]")
        return
    
    if users_collection.find_one({"email": email}):
        console.print("[bold red]Error: Email already exists![/bold red]")
        return

    user = {"email": email, "name": name, "role": role}
    users_collection.insert_one(user)
    console.print(f"[bold green]User {name} ({role}) added![/bold green]")

@app.command()
def list():
    """List all users"""
    users = users_collection.find()
    
    table = Table(title="Users")
    table.add_column("Name", style="magenta")
    table.add_column("Email", style="yellow")
    table.add_column("Role", style="cyan")

    for user in users:
        table.add_row(user["name"], user["email"], user["role"])

    console.print(table)

@app.command()
def delete(email: str):
    """Delete a user by email"""
    result = users_collection.delete_one({"email": email})
    
    if result.deleted_count == 0:
        console.print("[bold red]Error: User not found![/bold red]")
    else:
        console.print(f"[bold green]User {email} deleted![/bold green]")

if __name__ == "__main__":
    app()

