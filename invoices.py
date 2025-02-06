import typer
from pymongo import MongoClient
from rich.console import Console
from rich.table import Table

app = typer.Typer()
console = Console()

# Connect to MongoDB Atlas
client = MongoClient("mongodb+srv://n0rms:2m6dUSyTbwvfpbFq@cluster0.nf19p.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["crm_backend"]  # Use the "crm_backend" database
invoices_collection = db["invoices"]  # Create or connect to the "invoices" collection

@app.command()
def create(email: str, amount: float, description: str):
    """Create a new invoice for a customer"""
    invoice = {"customer_email": email, "amount": amount, "description": description, "status": "Unpaid"}
    invoices_collection.insert_one(invoice)
    console.print(f"[bold green]Invoice created for {email} - ${amount}[/bold green]")

@app.command()
def list():
    """List all invoices"""
    invoices = invoices_collection.find()
    
    table = Table(title="Invoices")
    table.add_column("Customer Email", style="cyan")
    table.add_column("Amount", style="magenta")
    table.add_column("Description", style="yellow")
    table.add_column("Status", style="green")

    for invoice in invoices:
        table.add_row(invoice["customer_email"], f"${invoice['amount']}", invoice["description"], invoice["status"])

    console.print(table)

@app.command()
def pay(email: str):
    """Mark an invoice as paid"""
    result = invoices_collection.update_one({"customer_email": email, "status": "Unpaid"}, {"$set": {"status": "Paid"}})
    
    if result.matched_count == 0:
        console.print("[bold red]Error: No unpaid invoice found for this customer![/bold red]")
    else:
        console.print(f"[bold green]Invoice for {email} marked as Paid![/bold green]")

@app.command()
def delete(email: str):
    """Delete an invoice by customer email"""
    result = invoices_collection.delete_one({"customer_email": email})
    
    if result.deleted_count == 0:
        console.print("[bold red]Error: Invoice not found![/bold red]")
    else:
        console.print(f"[bold green]Invoice for {email} deleted![/bold green]")

if __name__ == "__main__":
    app()

