# db.py

import sqlite3
import os

# Define the path to the database file relative to this script
# This makes it work regardless of where you run the main script from
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'blog.db')
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), 'schema.sql')

def get_db_connection():
    """Establishes a connection to the SQLite database.

    Returns:
        sqlite3.Connection: A database connection object.
                            The connection is configured to return rows
                            that behave like dictionaries.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    # Return rows as dictionary-like objects (access columns by name)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(app):
    """Initializes the database using the schema.sql file.

    Connects to the database, reads the schema file, and executes it.
    This function is typically called once, perhaps via a Flask CLI command.

    Args:
        app: The Flask application instance (used for logging/context if needed).
    """
    try:
        # Check if the schema file exists
        if not os.path.exists(SCHEMA_PATH):
            app.logger.error(f"Schema file not found at: {SCHEMA_PATH}")
            print(f"Error: Schema file not found at: {SCHEMA_PATH}") # Also print to console
            return # Exit if schema is missing

        conn = get_db_connection()
        with open(SCHEMA_PATH, 'r') as f:
            # Read the entire SQL script
            sql_script = f.read()
            # Execute the script (can contain multiple statements)
            conn.executescript(sql_script)
        conn.commit() # Save the changes
        app.logger.info("Database initialized successfully.")
        print("Database initialized successfully.") # Also print to console
    except sqlite3.Error as e:
        app.logger.error(f"Database initialization failed: {e}")
        print(f"Database initialization failed: {e}") # Also print to console
    except IOError as e:
        app.logger.error(f"Failed to read schema file: {e}")
        print(f"Failed to read schema file: {e}") # Also print to console
    finally:
        if conn:
            conn.close() # Always close the connection



def get_all_posts(order_by="published_date DESC"):
    """Retrieves all posts from the database, optionally ordered.

    Args:
        order_by (str): SQL fragment for the ORDER BY clause.
                        Defaults to 'published_date DESC' (newest first).

    Returns:
        list[sqlite3.Row]: A list of all posts, where each post is a
                           dictionary-like Row object. Returns an empty
                           list if no posts are found or an error occurs.
    """
    posts = []
    conn = None # Initialize conn to None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Basic sanitization for order_by to prevent injection (allow only specific patterns)
        # A more robust solution might involve mapping input strings to allowed columns/orders
        allowed_orders = ["published_date DESC", "published_date ASC", "title ASC", "title DESC"]
        if order_by not in allowed_orders:
            order_by = "published_date DESC" # Default to safe ordering

        query = f"SELECT id, title, content, published_date FROM posts ORDER BY {order_by}"
        cursor.execute(query)
        posts = cursor.fetchall()
    except sqlite3.Error as e:
        # In a real app, you'd want more robust logging here
        print(f"Database error in get_all_posts: {e}")
    finally:
        if conn:
            conn.close()
    return posts

def get_post_by_id(post_id):
    """Retrieves a single post by its ID.

    Args:
        post_id (int): The unique ID of the post to retrieve.

    Returns:
        sqlite3.Row | None: A dictionary-like Row object representing the post
                            if found, otherwise None. Returns None if an
                            error occurs.
    """
    post = None
    conn = None # Initialize conn to None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Use parameterized query to prevent SQL injection
        cursor.execute("SELECT id, title, content, published_date FROM posts WHERE id = ?", (post_id,))
        post = cursor.fetchone() # fetchone() gets the first result or None
    except sqlite3.Error as e:
        print(f"Database error in get_post_by_id: {e}")
    finally:
        if conn:
            conn.close()
    return post