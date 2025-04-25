# app.py

import os
import sqlite3 # Import sqlite3 to catch its specific errors if needed
import click   # Import click for CLI commands
from flask import Flask, render_template
from dotenv import load_dotenv
import db     
from faker import Faker

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



# --- Database Seeding Command ---
@app.cli.command('seed-db')
@click.option('--posts', default=10, help='Number of posts to create.')
def seed_db_command(posts):
    """Seeds the database with fake posts and tags."""
    fake = Faker()
    # fake_no = Faker('nb_NO') # Example if you want Norwegian data

    click.echo(f'Seeding database with {posts} posts...')

    try:
        for i in range(posts):
            # Generate fake post data
            title = fake.sentence(nb_words=6).capitalize()
            # Generate 1 to 4 paragraphs for content
            content_paragraphs = fake.paragraphs(nb=fake.random_int(min=1, max=4))
            content = "\n\n".join(content_paragraphs)
            # Generate 1 to 5 unique tags
            tag_names = fake.words(nb=fake.random_int(min=1, max=5), unique=True)

            # Add the post to the database
            post_id = db.add_post(title, content)

            if post_id:
                click.echo(f"  Added post '{title}' (ID: {post_id})")
                # Add tags and link them to the post
                for tag_name in tag_names:
                    tag_id = db.add_or_get_tag(tag_name)
                    if tag_id:
                        linked = db.link_post_tag(post_id, tag_id)
                        if linked:
                             click.echo(f"    - Linked tag '{tag_name}' (ID: {tag_id})")
                        else:
                             click.echo(f"    - Failed to link tag '{tag_name}' (ID: {tag_id})", err=True)
                    else:
                        click.echo(f"    - Failed to add/get tag '{tag_name}'", err=True)
            else:
                click.echo(f"  Failed to add post '{title}'", err=True)

        click.echo('Database seeding completed.')

    except Exception as e:
        # Catch potential errors during seeding
        click.echo(f'Error during database seeding: {e}', err=True)



# --- Routes ---
@app.route('/')
def index():
    """Renders the homepage, listing all blog posts."""
    try:
        # Fetch all posts from the database using our db module function
        posts = db.get_all_posts() # Defaults to newest first

        # Render an HTML template, passing the posts data to it
        return render_template('index.html', posts=posts)
    except Exception as e:
        # Basic error handling for the route
        app.logger.error(f"Error fetching posts for index page: {e}")
        # You might want a proper error page later
        return "<h1>An error occurred fetching posts.</h1>", 500

# --- Add more routes and logic below ---
# We'll add the route for individual posts next




# --- Run the development server ---
if __name__ == '__main__':
    print("--- Attempting to run Flask app ---")
    app.run(debug=True, port=5001) # Using port 5001 as decided earlier
