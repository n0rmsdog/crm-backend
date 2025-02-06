import typer
from customers import app as customers_app
from jobs import app as jobs_app
from invoices import app as invoices_app
from users import app as users_app
from time_tracking import app as time_tracking_app
from job_calendar import app as calendar_app  # Job Calendar Integration

app = typer.Typer()

# Add subcommands for each module
app.add_typer(customers_app, name="customers")
app.add_typer(jobs_app, name="jobs")
app.add_typer(invoices_app, name="invoices")
app.add_typer(users_app, name="users")
app.add_typer(time_tracking_app, name="time-tracking")
app.add_typer(calendar_app, name="calendar")  # Add Calendar to CRM

if __name__ == "__main__":
    app()

