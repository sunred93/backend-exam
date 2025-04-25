# db.py

import sqlite3
import os
# Import Flask context globals
from flask import current_app, g
import click

# Define default paths relative to this script
DEFAULT_DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'blog.db')
DEFAULT_SCHEMA_PATH = os.path.join(os.path.dirname(__file__), 'schema.sql')

# --- Connection Management ---

def get_db():
    """Gets the database connection for the current application context.

    If a connection doesn't exist, it creates one and stores it in flask.g.
    Also configures the connection to return dictionary-like rows.
    """
    if 'db' not in g:
        # Get DB path from config if available, else use default
        db_path = current_app.config.get('DATABASE', DEFAULT_DATABASE_PATH)
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    """Closes the database connection if it exists in the current context."""
    db_conn = g.pop('db', None)
    if db_conn is not None:
        db_conn.close()

def init_app(app):
    """Register database functions with the Flask app."""
    # Tell Flask to call close_db when cleaning up the context
    app.teardown_appcontext(close_db)
    # Add the init-db command (moved from app.py for better organization)
    app.cli.add_command(init_db_command_context)


# --- Database Initialization ---

# Modified init_db to use get_db for connection and context
def init_db_logic(schema_path=None):
    """Initializes the database using the schema.sql file (logic part)."""
    if schema_path is None:
        schema_path = DEFAULT_SCHEMA_PATH

    conn = None # Initialize conn
    try:
        if not os.path.exists(schema_path):
            # Use current_app logger if available, else print
            logger = current_app.logger if current_app else None
            err_msg = f"Schema file not found at: {schema_path}"
            if logger: logger.error(err_msg)
            print(f"Error: {err_msg}")
            return

        # Use the connection from the app context
        conn = get_db()
        with open(schema_path, 'r') as f:
            sql_script = f.read()
            conn.executescript(sql_script)
        # No commit needed here if autocommit is default or handled by context teardown
        # conn.commit() # Usually not needed with executescript in default mode

        db_path = current_app.config.get('DATABASE', DEFAULT_DATABASE_PATH)
        print(f"Database initialized successfully at {db_path}.")

    except sqlite3.Error as e:
        print(f"Database initialization failed: {e}")
    except IOError as e:
        print(f"Failed to read schema file {schema_path}: {e}")
    # Connection closing is handled by close_db via teardown_appcontext

# Command to run init_db_logic within app context
@click.command('init-db')
def init_db_command_context():
    """Clear existing data and create new tables."""
    init_db_logic()
    click.echo('Initialized the database.')


# --- Other DB functions ---
# Modify all functions to use get_db() instead of get_db_connection()

def get_all_posts(order_by="published_date DESC"):
    """Retrieves all posts from the database, optionally ordered."""
    conn = get_db() # Use context connection
    cursor = conn.cursor()
    allowed_orders = ["published_date DESC", "published_date ASC", "title ASC", "title DESC"]
    if order_by not in allowed_orders:
        order_by = "published_date DESC"
    query = f"SELECT id, title, content, published_date FROM posts ORDER BY {order_by}"
    posts = cursor.execute(query).fetchall()
    # No connection closing needed here
    return posts

def get_post_by_id(post_id):
    """Retrieves a single post by its ID."""
    conn = get_db() # Use context connection
    post = conn.execute(
        "SELECT id, title, content, published_date FROM posts WHERE id = ?", (post_id,)
    ).fetchone()
    return post

def add_post(title, content):
    """Adds a new post to the database."""
    conn = get_db() # Use context connection
    try:
        cursor = conn.execute(
            "INSERT INTO posts (title, content) VALUES (?, ?)",
            (title, content)
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"Database error in add_post: {e}")
        conn.rollback()
        return None

def add_or_get_tag(tag_name):
    """Adds a new tag if it doesn't exist, or gets the ID of an existing tag."""
    conn = get_db() # Use context connection
    tag_id = None
    try:
        # Check if tag exists
        result = conn.execute("SELECT id FROM tags WHERE name = ?", (tag_name,)).fetchone()
        if result:
            tag_id = result['id']
        else:
            # Insert if not found
            cursor = conn.execute("INSERT INTO tags (name) VALUES (?)", (tag_name,))
            conn.commit()
            tag_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        # Handle potential race condition
        result = conn.execute("SELECT id FROM tags WHERE name = ?", (tag_name,)).fetchone()
        if result:
            tag_id = result['id']
        else:
            print(f"Database error: Failed to insert or find tag '{tag_name}' after IntegrityError.")
            conn.rollback()
    except sqlite3.Error as e:
        print(f"Database error in add_or_get_tag for '{tag_name}': {e}")
        conn.rollback()
    return tag_id


def update_post(post_id, title, content):
    """Updates the title and content of an existing post."""
    conn = get_db() # Use context connection
    try:
        cursor = conn.execute(
            "UPDATE posts SET title = ?, content = ? WHERE id = ?",
            (title, content, post_id)
        )
        conn.commit()
        return cursor.rowcount > 0 # Return True if a row was updated
    except sqlite3.Error as e:
        print(f"Database error in update_post for post {post_id}: {e}")
        conn.rollback()
        return False

def link_post_tag(post_id, tag_id):
    """Creates an association between a post and a tag."""
    conn = get_db() # Use context connection
    try:
        conn.execute(
            "INSERT INTO post_tags (post_id, tag_id) VALUES (?, ?)",
            (post_id, tag_id)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # Link likely already exists, check just in case
        existing = conn.execute(
            "SELECT 1 FROM post_tags WHERE post_id = ? AND tag_id = ?", (post_id, tag_id)
        ).fetchone()
        if existing:
            print(f"Info: Link between post {post_id} and tag {tag_id} already exists.")
            return True # Consider it success if it exists
        else:
            conn.rollback() # Rollback if it failed for another reason
            return False
    except sqlite3.Error as e:
        print(f"Database error in link_post_tag ({post_id}, {tag_id}): {e}")
        conn.rollback()
        return False

def get_tags_for_post(post_id):
    """Retrieves all tags associated with a specific post."""
    conn = get_db() # Use context connection
    tags = conn.execute("""
        SELECT t.id, t.name
        FROM tags t
        JOIN post_tags pt ON t.id = pt.tag_id
        WHERE pt.post_id = ?
        ORDER BY t.name
    """, (post_id,)).fetchall()
    return tags

def get_posts_by_tag(tag_name):
    """Retrieves all posts associated with a specific tag name."""
    conn = get_db() # Use context connection
    posts = conn.execute("""
        SELECT p.id, p.title, p.content, p.published_date
        FROM posts p
        JOIN post_tags pt ON p.id = pt.post_id
        JOIN tags t ON pt.tag_id = t.id
        WHERE t.name = ?
        ORDER BY p.published_date DESC
    """, (tag_name,)).fetchall()
    return posts

def get_comments_for_post(post_id):
    """Retrieves all comments for a specific post."""
    conn = get_db() # Use context connection
    comments = conn.execute("""
        SELECT id, author, content, published_date
        FROM comments
        WHERE post_id = ?
        ORDER BY published_date ASC
    """, (post_id,)).fetchall()
    return comments

def add_comment(post_id, author, content):
    """Adds a new comment to a specific post."""
    conn = get_db() # Use context connection
    try:
        cursor = conn.execute(
            "INSERT INTO comments (post_id, author, content) VALUES (?, ?, ?)",
            (post_id, author, content)
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"Database error in add_comment for post {post_id}: {e}")
        conn.rollback()
        return None

def unlink_all_tags_for_post(post_id):
    """Removes all tag associations for a specific post."""
    conn = get_db() # Use context connection
    try:
        conn.execute("DELETE FROM post_tags WHERE post_id = ?", (post_id,))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Database error in unlink_all_tags_for_post for post {post_id}: {e}")
        conn.rollback()
        return False

