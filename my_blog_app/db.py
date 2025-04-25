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



def add_post(title, content):
    """Adds a new post to the database.

    Args:
        title (str): The title of the post.
        content (str): The body content of the post.

    Returns:
        int | None: The ID of the newly inserted post if successful,
                    otherwise None.
    """
    conn = None
    last_id = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Use parameterized query
        cursor.execute("INSERT INTO posts (title, content) VALUES (?, ?)",
                       (title, content))
        conn.commit() # Commit the transaction
        last_id = cursor.lastrowid # Get the ID of the row just inserted
    except sqlite3.Error as e:
        print(f"Database error in add_post: {e}")
        if conn:
            conn.rollback() # Rollback changes if error occurs
    finally:
        if conn:
            conn.close()
    return last_id

def add_or_get_tag(tag_name):
    """Adds a new tag if it doesn't exist, or gets the ID of an existing tag.

    Args:
        tag_name (str): The name of the tag.

    Returns:
        int | None: The ID of the tag (either newly created or existing)
                    if successful, otherwise None.
    """
    conn = None
    tag_id = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # First, try to find the tag
        cursor.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
        result = cursor.fetchone()

        if result:
            tag_id = result['id']
        else:
            # If not found, insert the new tag
            cursor.execute("INSERT INTO tags (name) VALUES (?)", (tag_name,))
            conn.commit() # Commit the insert
            tag_id = cursor.lastrowid # Get the ID of the new tag

    except sqlite3.IntegrityError:
        # Handle potential race condition if another process inserted the tag
        # between our SELECT and INSERT (less likely with SQLite's default locking)
        # Re-query to get the ID of the now existing tag
        if conn: # Ensure connection exists before re-querying
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
            result = cursor.fetchone()
            if result:
                tag_id = result['id']
            else:
                 print(f"Database error: Failed to insert or find tag '{tag_name}' after IntegrityError.")
                 conn.rollback() # Rollback if we still can't find it
        else:
             print(f"Database error: Connection lost during tag handling for '{tag_name}'.")

    except sqlite3.Error as e:
        print(f"Database error in add_or_get_tag for '{tag_name}': {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
    return tag_id


def update_post(post_id, title, content):
    """Updates the title and content of an existing post.

    Args:
        post_id (int): The ID of the post to update.
        title (str): The new title for the post.
        content (str): The new content for the post.

    Returns:
        bool: True if the update was successful (at least one row affected),
              False otherwise (e.g., post_id not found or error occurred).
    """
    conn = None
    success = False
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Use parameterized query for the UPDATE statement
        cursor.execute("""
            UPDATE posts
            SET title = ?, content = ?
            WHERE id = ?
        """, (title, content, post_id))
        conn.commit()
        # Check if any row was actually updated
        # cursor.rowcount will be 1 if the update was successful, 0 if id wasn't found
        if cursor.rowcount > 0:
            success = True
    except sqlite3.Error as e:
        print(f"Database error in update_post for post {post_id}: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
    return success

def link_post_tag(post_id, tag_id):
    """Creates an association between a post and a tag in the post_tags table.

    Args:
        post_id (int): The ID of the post.
        tag_id (int): The ID of the tag.

    Returns:
        bool: True if the link was created successfully, False otherwise.
    """
    conn = None
    success = False
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Use parameterized query
        cursor.execute("INSERT INTO post_tags (post_id, tag_id) VALUES (?, ?)",
                       (post_id, tag_id))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        # This likely means the link already exists (due to PRIMARY KEY constraint)
        # Or one of the foreign keys doesn't exist (shouldn't happen if IDs are valid)
        # We can often silently ignore this if duplicates are okay or expected.
        print(f"Info: Link between post {post_id} and tag {tag_id} likely already exists.")
        # Check if the link actually exists now
        cursor.execute("SELECT 1 FROM post_tags WHERE post_id = ? AND tag_id = ?", (post_id, tag_id))
        if cursor.fetchone():
            success = True # It exists, so consider it a success in this context
        else:
            if conn: conn.rollback() # Rollback if it doesn't exist after IntegrityError
    except sqlite3.Error as e:
        print(f"Database error in link_post_tag ({post_id}, {tag_id}): {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
    return success

def get_tags_for_post(post_id):
    """Retrieves all tags associated with a specific post.

    Args:
        post_id (int): The ID of the post.

    Returns:
        list[sqlite3.Row]: A list of tag objects (dictionary-like Rows),
                           each containing 'id' and 'name'. Returns an empty
                           list if no tags are found or an error occurs.
    """
    tags = []
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Join posts, post_tags, and tags tables to get tag names for a post_id
        cursor.execute("""
            SELECT t.id, t.name
            FROM tags t
            JOIN post_tags pt ON t.id = pt.tag_id
            WHERE pt.post_id = ?
            ORDER BY t.name
        """, (post_id,))
        tags = cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Database error in get_tags_for_post for post {post_id}: {e}")
    finally:
        if conn:
            conn.close()
    return tags

def get_posts_by_tag(tag_name):
    """Retrieves all posts associated with a specific tag name.

    Args:
        tag_name (str): The name of the tag.

    Returns:
        list[sqlite3.Row]: A list of post objects (dictionary-like Rows)
                           associated with the tag, ordered by newest first.
                           Returns an empty list if the tag doesn't exist,
                           has no posts, or an error occurs.
    """
    posts = []
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Join posts, post_tags, and tags tables. Filter by tag name.
        cursor.execute("""
            SELECT p.id, p.title, p.content, p.published_date
            FROM posts p
            JOIN post_tags pt ON p.id = pt.post_id
            JOIN tags t ON pt.tag_id = t.id
            WHERE t.name = ?
            ORDER BY p.published_date DESC
        """, (tag_name,))
        posts = cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Database error in get_posts_by_tag for tag '{tag_name}': {e}")
    finally:
        if conn:
            conn.close()
    return posts


def get_comments_for_post(post_id):
    """Retrieves all comments for a specific post, ordered by date ascending.

    Args:
        post_id (int): The ID of the post.

    Returns:
        list[sqlite3.Row]: A list of comment objects (dictionary-like Rows).
                           Returns an empty list if no comments are found
                           or an error occurs.
    """
    comments = []
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, author, content, published_date
            FROM comments
            WHERE post_id = ?
            ORDER BY published_date ASC
        """, (post_id,))
        comments = cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Database error in get_comments_for_post for post {post_id}: {e}")
    finally:
        if conn:
            conn.close()
    return comments

def add_comment(post_id, author, content):
    """Adds a new comment to a specific post.

    Args:
        post_id (int): The ID of the post to comment on.
        author (str): The name of the comment author.
        content (str): The text content of the comment.

    Returns:
        int | None: The ID of the newly inserted comment if successful,
                    otherwise None.
    """
    conn = None
    last_id = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO comments (post_id, author, content)
            VALUES (?, ?, ?)
        """, (post_id, author, content))
        conn.commit()
        last_id = cursor.lastrowid
    except sqlite3.Error as e:
        print(f"Database error in add_comment for post {post_id}: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
    return last_id


def unlink_all_tags_for_post(post_id):
    """Removes all tag associations for a specific post from post_tags.

    Args:
        post_id (int): The ID of the post whose tag links should be removed.

    Returns:
        bool: True if the deletion was successful or if no links existed,
              False if an error occurred.
    """
    conn = None
    success = False
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Use parameterized query for the DELETE statement
        cursor.execute("DELETE FROM post_tags WHERE post_id = ?", (post_id,))
        conn.commit()
        # rowcount will be >= 0. Consider successful if no error.
        success = True
    except sqlite3.Error as e:
        print(f"Database error in unlink_all_tags_for_post for post {post_id}: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
    return success
# --- We will add functions for comments, updating posts later ---
