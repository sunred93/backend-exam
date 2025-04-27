# db.py

import sqlite3
import os
import uuid # Import uuid for generating unique filenames
# Import Flask context globals and current_app for path finding and logging
from flask import current_app, g
import click

# Define default paths relative to this script
DEFAULT_DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'blog.db')
DEFAULT_SCHEMA_PATH = os.path.join(os.path.dirname(__file__), 'schema.sql')

# --- Define image upload folder relative to static ---
# This path is relative to the 'static' folder Flask serves
IMAGE_UPLOAD_FOLDER = 'uploads/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# --- Helper Functions ---

def allowed_file(filename):
    """Checks if the filename has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_image(image_file_storage):
    """Saves an uploaded image file and returns its unique relative path.

    Args:
        image_file_storage: The FileStorage object from Flask request.files.

    Returns:
        The relative path (from static folder) of the saved image, or None if failed.
    """
    if image_file_storage and allowed_file(image_file_storage.filename):
        # Create a unique filename to avoid conflicts and for security
        _, ext = os.path.splitext(image_file_storage.filename)
        # Use secure_filename from werkzeug if you want extra sanitization,
        # but UUID is generally safer against path traversal etc.
        unique_filename = f"{uuid.uuid4().hex}{ext}"

        # Ensure the upload directory exists within the static folder
        # Use current_app.static_folder which points to your 'static' directory
        # Make sure current_app is available (this function should be called within a request context)
        if not current_app:
             print("Error: Cannot access current_app. Function called outside of application context.")
             return None
        upload_path_full = os.path.join(current_app.static_folder, IMAGE_UPLOAD_FOLDER)
        os.makedirs(upload_path_full, exist_ok=True)

        # Save the file to the full path
        save_to = os.path.join(upload_path_full, unique_filename)
        try:
            image_file_storage.save(save_to)
            # Return the relative path (from static) to store in DB
            # Use forward slashes for web compatibility
            relative_path = os.path.join(IMAGE_UPLOAD_FOLDER, unique_filename).replace("\\", "/")
            current_app.logger.info(f"Saved image: {relative_path}")
            return relative_path
        except Exception as e:
            # Log the error if saving fails
            current_app.logger.error(f"Failed to save image {unique_filename}: {e}")
            return None
    elif image_file_storage and image_file_storage.filename != '':
        # Log if the file type was not allowed but a file was present
        current_app.logger.warning(f"Image upload failed: File type not allowed for {image_file_storage.filename}")
    return None # No file, or not allowed type

def delete_image_file(relative_image_path):
    """Deletes an image file given its relative path from the static folder."""
    if not relative_image_path:
        return False
    # Make sure current_app is available
    if not current_app:
         print("Error: Cannot access current_app. Function called outside of application context.")
         return False
    try:
        # Construct the full path relative to the static folder
        image_path_full = os.path.join(current_app.static_folder, relative_image_path)
        if os.path.exists(image_path_full):
            os.remove(image_path_full)
            current_app.logger.info(f"Deleted image file: {image_path_full}")
            return True
        else:
            # It's okay if the file doesn't exist, maybe it was already deleted
            current_app.logger.warning(f"Attempted to delete non-existent image: {image_path_full}")
            return False # Indicate file wasn't found/deleted now
    except OSError as e:
        current_app.logger.error(f"Error deleting image file {relative_image_path}: {e}")
        return False


# --- Connection Management ---

def get_db():
    """Gets the database connection for the current application context."""
    if 'db' not in g:
        db_path = current_app.config.get('DATABASE', DEFAULT_DATABASE_PATH)
        try:
            # Add detect_types parameter here!
            g.db = sqlite3.connect(
                db_path,
                detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
            )
            g.db.row_factory = sqlite3.Row # Keep using Row factory
        except sqlite3.Error as e:
            current_app.logger.error(f"Database connection failed for {db_path}: {e}")
            # Optionally raise the error or return None depending on desired handling
            raise e # Or handle more gracefully
    return g.db

def close_db(e=None):
    """Closes the database connection if it exists in the current context."""
    db_conn = g.pop('db', None)
    if db_conn is not None:
        db_conn.close()

def init_app(app):
    """Register database functions with the Flask app."""
    app.teardown_appcontext(close_db)
    # Add the init-db command defined below to the Flask CLI
    app.cli.add_command(init_db_command_context)
    # Note: seed-db command is defined directly in app.py, so not registered here


# --- Database Initialization ---

def init_db_logic(schema_path=None):
    """Initializes the database using the schema.sql file (logic part)."""
    if schema_path is None:
        schema_path = DEFAULT_SCHEMA_PATH

    conn = None
    try:
        if not os.path.exists(schema_path):
            # Use logger if available (within app context), otherwise print
            logger = current_app.logger if current_app else None
            err_msg = f"Schema file not found at: {schema_path}"
            if logger: logger.error(err_msg)
            else: print(f"Error: {err_msg}")
            return False # Indicate failure

        conn = get_db() # Get connection within app context
        with open(schema_path, 'r') as f:
            sql_script = f.read()
            conn.executescript(sql_script)
        conn.commit() # Commit the changes from executescript
        return True # Indicate success

    except sqlite3.Error as e:
        # Log the specific SQL error
        err_msg = f"Database initialization failed: {e}"
        logger = current_app.logger if current_app else None
        if logger: logger.error(err_msg)
        else: print(err_msg)
        if conn: conn.rollback() # Rollback any partial changes
        return False # Indicate failure
    except IOError as e:
        err_msg = f"Failed to read schema file {schema_path}: {e}"
        logger = current_app.logger if current_app else None
        if logger: logger.error(err_msg)
        else: print(err_msg)
        return False # Indicate failure
    # No finally block needed for conn.close() because get_db/close_db handle it

@click.command('init-db')
def init_db_command_context():
    """Clear existing data and create new tables from schema.sql."""
    if init_db_logic():
        click.echo('Initialized the database.')
    else:
        # Error message already printed/logged by init_db_logic
        click.echo('Database initialization failed. Check logs or console output.', err=True)


# --- CRUD Operations for Posts (with Image Handling) ---

def get_all_posts(order_by="published_date DESC"):
    """Retrieves all posts including image filename."""
    conn = get_db()
    cursor = conn.cursor()
    allowed_orders = ["published_date DESC", "published_date ASC", "title ASC", "title DESC"]
    if order_by not in allowed_orders:
        order_by = "published_date DESC"
    # Include image_filename in the SELECT
    query = f"SELECT id, title, content, published_date, image_filename FROM posts ORDER BY {order_by}"
    try:
        posts = cursor.execute(query).fetchall()
        return posts
    except sqlite3.Error as e:
        current_app.logger.error(f"DB error in get_all_posts: {e}")
        return [] # Return empty list on error

def get_post_by_id(post_id):
    """Retrieves a single post by its ID, including image filename."""
    conn = get_db()
    try:
        post = conn.execute(
            # Include image_filename in the SELECT
            "SELECT id, title, content, published_date, image_filename FROM posts WHERE id = ?", (post_id,)
        ).fetchone()
        return post # Returns None if not found, which is expected
    except sqlite3.Error as e:
        current_app.logger.error(f"DB error in get_post_by_id for post {post_id}: {e}")
        return None

def add_post(title, content, image_filename=None): # Add image_filename parameter
    """Adds a new post to the database, including the image filename."""
    conn = get_db()
    try:
        cursor = conn.execute(
            # Include image_filename in the INSERT
            "INSERT INTO posts (title, content, image_filename) VALUES (?, ?, ?)",
            (title, content, image_filename) # Pass the filename (can be None)
        )
        conn.commit()
        return cursor.lastrowid # Return the ID of the newly inserted post
    except sqlite3.Error as e:
        # Log the specific error
        current_app.logger.error(f"Database error in add_post: {e}")
        conn.rollback()
        return None # Indicate failure

def update_post(post_id, title, content, image_filename=None, update_image=False):
    """Updates an existing post. Can optionally update the image filename.

    Args:
        post_id: ID of the post to update.
        title: New title.
        content: New content.
        image_filename: New image filename (or None). Should be the relative path.
        update_image: Boolean indicating if the image_filename field should be updated.
                      If False, image_filename is ignored. If True, it's updated
                      (even if image_filename is None, which would remove the image link).
    """
    conn = get_db()
    try:
        if update_image:
            # Update title, content, AND image_filename
            sql = "UPDATE posts SET title = ?, content = ?, image_filename = ? WHERE id = ?"
            params = (title, content, image_filename, post_id)
        else:
            # Only update title and content, leave image_filename as is
            sql = "UPDATE posts SET title = ?, content = ? WHERE id = ?"
            params = (title, content, post_id)

        cursor = conn.execute(sql, params)
        conn.commit()
        return cursor.rowcount > 0 # True if a row was affected (post existed)
    except sqlite3.Error as e:
        current_app.logger.error(f"Database error in update_post for post {post_id}: {e}")
        conn.rollback()
        return False # Indicate failure

def delete_post(post_id):
    """Deletes a post and attempts to delete its associated image file."""
    conn = get_db()
    # First, get the image filename *before* deleting the post record
    post_data = get_post_by_id(post_id)
    image_to_delete = post_data['image_filename'] if post_data else None

    try:
        cursor = conn.execute("DELETE FROM posts WHERE id = ?", (post_id,))
        # Note: ON DELETE CASCADE in schema handles comments and post_tags automatically
        conn.commit()
        rows_affected = cursor.rowcount

        if rows_affected > 0:
            # If post deletion was successful, try deleting the image file
            if image_to_delete:
                delete_image_file(image_to_delete) # Attempt deletion, ignore result for now
            return True # Post deleted (image deletion attempt made)
        else:
            # Post with that ID didn't exist
            current_app.logger.warning(f"Attempted to delete non-existent post with ID: {post_id}")
            return False
    except sqlite3.Error as e:
        current_app.logger.error(f"Database error deleting post {post_id}: {e}")
        conn.rollback()
        return False


# --- Tag Operations (Generally Unchanged by Image Feature) ---

def add_or_get_tag(tag_name):
    """Adds a new tag if it doesn't exist, or gets the ID of an existing tag."""
    conn = get_db()
    tag_id = None
    try:
        # Try selecting first (more common case)
        result = conn.execute("SELECT id FROM tags WHERE name = ?", (tag_name,)).fetchone()
        if result:
            tag_id = result['id']
        else:
            # If not found, try inserting
            try:
                cursor = conn.execute("INSERT INTO tags (name) VALUES (?)", (tag_name,))
                conn.commit()
                tag_id = cursor.lastrowid
            except sqlite3.IntegrityError: # Handles race condition if tag inserted between SELECT and INSERT
                conn.rollback() # Rollback the failed INSERT attempt
                # Fetch again, it should exist now
                result = conn.execute("SELECT id FROM tags WHERE name = ?", (tag_name,)).fetchone()
                if result:
                    tag_id = result['id']
                else:
                    # This case should be rare, log if it happens
                    current_app.logger.error(f"DB error: Failed to find tag '{tag_name}' after IntegrityError.")
    except sqlite3.Error as e:
        current_app.logger.error(f"DB error in add_or_get_tag for '{tag_name}': {e}")
        if conn: conn.rollback() # Rollback if error occurred during SELECT/INSERT attempt
    return tag_id

def link_post_tag(post_id, tag_id):
    """Creates an association between a post and a tag."""
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO post_tags (post_id, tag_id) VALUES (?, ?)",
            (post_id, tag_id)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError: # Link likely already exists or invalid ID
        conn.rollback() # Rollback the failed insert
        # Check if it's just a duplicate link (which is fine) or an invalid ID
        post_exists = conn.execute("SELECT 1 FROM posts WHERE id = ?", (post_id,)).fetchone()
        tag_exists = conn.execute("SELECT 1 FROM tags WHERE id = ?", (tag_id,)).fetchone()
        if post_exists and tag_exists:
             # Link probably already exists, treat as success
             # current_app.logger.info(f"Link already exists or race condition: post {post_id}, tag {tag_id}")
             return True
        else:
             current_app.logger.warning(f"IntegrityError linking post {post_id} and tag {tag_id}. Post/Tag might not exist.")
             return False # Indicate failure due to potentially invalid IDs
    except sqlite3.Error as e:
        current_app.logger.error(f"DB error in link_post_tag ({post_id}, {tag_id}): {e}")
        conn.rollback()
        return False

def unlink_all_tags_for_post(post_id):
    """Removes all tag associations for a specific post."""
    conn = get_db()
    try:
        conn.execute("DELETE FROM post_tags WHERE post_id = ?", (post_id,))
        conn.commit()
        return True
    except sqlite3.Error as e:
        current_app.logger.error(f"DB error in unlink_all_tags_for_post for post {post_id}: {e}")
        conn.rollback()
        return False

def get_tags_for_post(post_id):
    """Retrieves all tags associated with a specific post."""
    conn = get_db()
    try:
        tags = conn.execute("""
            SELECT t.id, t.name
            FROM tags t
            JOIN post_tags pt ON t.id = pt.tag_id
            WHERE pt.post_id = ?
            ORDER BY t.name
        """, (post_id,)).fetchall()
        return tags
    except sqlite3.Error as e:
        current_app.logger.error(f"DB error in get_tags_for_post for post {post_id}: {e}")
        return []

def get_posts_by_tag(tag_name):
    """Retrieves all posts associated with a specific tag name, including image."""
    conn = get_db()
    try:
        posts = conn.execute("""
            SELECT p.id, p.title, p.content, p.published_date, p.image_filename -- Add image_filename
            FROM posts p
            JOIN post_tags pt ON p.id = pt.post_id
            JOIN tags t ON pt.tag_id = t.id
            WHERE t.name = ?
            ORDER BY p.published_date DESC
        """, (tag_name,)).fetchall()
        return posts
    except sqlite3.Error as e:
        current_app.logger.error(f"DB error in get_posts_by_tag for tag '{tag_name}': {e}")
        return []


# --- Comment Operations (Unchanged by Image Feature) ---

def get_comments_for_post(post_id):
    """Retrieves all comments for a specific post."""
    conn = get_db()
    try:
        comments = conn.execute("""
            SELECT id, author, content, published_date
            FROM comments
            WHERE post_id = ?
            ORDER BY published_date ASC
        """, (post_id,)).fetchall()
        return comments
    except sqlite3.Error as e:
        current_app.logger.error(f"DB error in get_comments_for_post for post {post_id}: {e}")
        return []

def add_comment(post_id, author, content):
    """Adds a new comment to a specific post."""
    conn = get_db()
    try:
        cursor = conn.execute(
            "INSERT INTO comments (post_id, author, content) VALUES (?, ?, ?)",
            (post_id, author, content)
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        current_app.logger.error(f"DB error in add_comment for post {post_id}: {e}")
        conn.rollback()
        return None
