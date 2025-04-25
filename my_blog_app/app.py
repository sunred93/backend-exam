# app.py

import os
import sqlite3 # Import sqlite3 to catch its specific errors if needed
import click   # Import click for CLI commands
from flask import Flask
from dotenv import load_dotenv
import db      # Import your db module

# Load environment variables from .env file
load_dotenv()

# Create the Flask application instance
app = Flask(__name__)

# Load configuration from environment variables
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'a_default_secret_key_for_dev')
# Add the database path to the config for potential future use (optional)
app.config['DATABASE'] = db.DATABASE_PATH


# --- Database Initialization Command ---
@app.cli.command('init-db')
@click.command(help='Initialize the database by creating tables from schema.sql.')
def init_db_command():
    """Clear existing data and create new tables."""
    try:
        db.init_db(app) # Call the init_db function from your db module
        click.echo('Initialized the database.') # Use click.echo for CLI output
    except Exception as e:
        # Catch potential errors during initialization
        click.echo(f'Error initializing database: {e}', err=True)

# --- Routes ---
@app.route('/')
def index():
    """Renders the homepage."""
    # We'll add database interaction here later
    return "<h1>Welcome to My Blog App!</h1>"

# --- Add more routes and logic below ---


# --- Run the development server ---
if __name__ == '__main__':
    print("--- Attempting to run Flask app ---")
    app.run(debug=True, port=5001) # Using port 5001 as decided earlier
