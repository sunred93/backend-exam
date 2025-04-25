# tests/test_app.py

import pytest
from flask import url_for, current_app # Import current_app
from app import app as flask_app # Import your Flask app instance
# Import your db module to potentially interact with the DB in tests
import db
import random
import os
import tempfile # For creating temporary files/directories
import click # Needed for init_db_command_context if called directly

@pytest.fixture
def app():
    """Create and configure a new app instance for each test session."""
    # Create a temporary file for the database
    db_fd, db_path = tempfile.mkstemp(suffix='.sqlite')
    # print(f"Using test database: {db_path}") # Optional: for debugging

    flask_app.config.update({
        "TESTING": True,
        "DATABASE": db_path, # Set the database path for the test app context
        # Disable WTF_CSRF_ENABLED if you add forms with CSRF later
        # "WTF_CSRF_ENABLED": False,
    })

    # Initialize the temporary database within the app context
    # init_db_logic will now use the path from current_app.config['DATABASE']
    with flask_app.app_context():
        db.init_db_logic() # Call the logic function directly

    yield flask_app # Provide the configured app to the tests

    # --- Teardown ---
    # Close the file descriptor
    os.close(db_fd)
    # Remove the temporary database file
    os.unlink(db_path)
    # print(f"Cleaned up test database: {db_path}") # Optional: for debugging


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

# --- Tests ---
def test_index_page_loads(client):
    """Test if the index page (/) loads successfully."""
    # This test doesn't rely on specific data, just the template structure
    response = client.get('/')
    assert response.status_code == 200
    assert b"<h1>All Blog Posts</h1>" in response.data


def test_post_page_loads(client):
    """Test if a valid single post page loads."""
    # --- Test Setup: Ensure post exists in the test DB ---
    with flask_app.app_context(): # Need app context to use db functions
        test_title = f"Post for Test {random.randint(100,999)}"
        test_content = "Content for testing post page load."
        post_id_to_test = db.add_post(test_title, test_content)
        assert post_id_to_test is not None, "Failed to create post for test setup"
    # --- End Test Setup ---

    response = client.get(f'/post/{post_id_to_test}')
    assert response.status_code == 200
    assert bytes(test_title, 'utf-8') in response.data


def test_post_not_found(client):
    """Test accessing a non-existent post returns 404."""
    non_existent_post_id = 99999 # Choose an ID unlikely to exist
    response = client.get(f'/post/{non_existent_post_id}')
    assert response.status_code == 404


def test_add_comment(client):
    """Test submitting a comment to a post."""
    # --- Test Setup: Create a post to comment on ---
    with flask_app.app_context():
        post_id_to_test = db.add_post("Comment Test Post", "Content...")
        assert post_id_to_test is not None, "Failed to create post for comment test"
    # --- End Test Setup ---

    comment_data = {
        'author': 'Test Comment Author',
        'content': 'This is a test comment for isolation.'
    }

    # Simulate POST request to the specific post URL
    response = client.post(f'/post/{post_id_to_test}', data=comment_data)

    # Check for redirect after successful POST (Post/Redirect/Get pattern)
    assert response.status_code == 302
    # Check if the redirect location is the same post page
    with flask_app.app_context():
        expected_url = url_for('post', post_id=post_id_to_test)
    assert response.location.endswith(expected_url)

    # Follow the redirect and check if the comment appears
    response_after_redirect = client.get(f'/post/{post_id_to_test}')
    assert response_after_redirect.status_code == 200
    assert bytes(comment_data['author'], 'utf-8') in response_after_redirect.data
    assert bytes(comment_data['content'], 'utf-8') in response_after_redirect.data


def test_tag_page(client):
    """Test loading the page for a specific tag."""
    # --- Test Setup: Create a post and associate it with the tag ---
    tag_name_to_test = f'test_tag_{random.randint(100,999)}'
    post_data = None # Define post_data outside the 'with' block
    with flask_app.app_context():
        post_id = db.add_post(f"Post for {tag_name_to_test}", "Content...")
        assert post_id is not None
        tag_id = db.add_or_get_tag(tag_name_to_test)
        assert tag_id is not None
        linked = db.link_post_tag(post_id, tag_id)
        assert linked, f"Failed to link post {post_id} and tag {tag_id}"
        # Fetch the post data to check later
        post_data = db.get_post_by_id(post_id)
        assert post_data is not None
    # --- End Test Setup ---

    response = client.get(f'/tag/{tag_name_to_test}')

    assert response.status_code == 200
    # Check if the tag name appears in the heading
    assert bytes(f'Posts tagged with "{tag_name_to_test}"', 'utf-8') in response.data

    # Check if the title of the post created for this tag is present
    assert bytes(post_data['title'], 'utf-8') in response.data


def test_create_post_page_loads(client):
    """Test if the create post page (/post/new) loads successfully."""
    response = client.get('/post/new')
    assert response.status_code == 200
    assert b"<h1>Create New Post</h1>" in response.data
    assert b'<form method="post">' in response.data


def test_create_post_submit(client):
    """Test submitting a new post."""
    # Generate unique data for this test run
    unique_suffix = random.randint(1000, 9999)
    new_post_data = {
        'title': f'Test Create Post Title {unique_suffix}',
        'content': f'Test content for create post {unique_suffix}.',
        'tags': 'test, create, pytest'
    }

    # Simulate POST request to the create URL
    response = client.post('/post/new', data=new_post_data)

    # Check for redirect after successful POST
    assert response.status_code == 302

    # Check if the post now exists in the database by title
    created_post = None
    with flask_app.app_context():
        # Use get_db() which respects the app context and config
        conn = db.get_db()
        created_post = conn.execute(
            "SELECT * FROM posts WHERE title = ?", (new_post_data['title'],)
        ).fetchone()
        # No need to close conn here, handled by teardown_appcontext

    assert created_post is not None
    assert created_post['content'] == new_post_data['content']

    # Check if the redirect location points to the newly created post's page
    with flask_app.app_context():
        expected_url = url_for('post', post_id=created_post['id'])
    assert response.location.endswith(expected_url)

    # Follow redirect and check content on the post page
    response_after_redirect = client.get(response.location)
    assert response_after_redirect.status_code == 200
    assert bytes(new_post_data['title'], 'utf-8') in response_after_redirect.data
    # Check if tags were added (simple check for one tag)
    assert b'test' in response_after_redirect.data # Check within the rendered HTML


def test_edit_post_page_loads(client):
    """Test if the edit post page loads with pre-filled data."""
    # --- Test Setup: Create a post to edit ---
    tag_name_orig = f'orig_tag_{random.randint(100,999)}'
    post_title_orig = None # Define outside 'with'
    post_id_to_test = None # Define outside 'with'
    with flask_app.app_context():
        post_title_orig = f"Original Title {random.randint(100,999)}"
        post_content_orig = "Original content to be edited."
        post_id_to_test = db.add_post(post_title_orig, post_content_orig)
        assert post_id_to_test is not None
        tag_id_orig = db.add_or_get_tag(tag_name_orig)
        assert tag_id_orig is not None
        linked = db.link_post_tag(post_id_to_test, tag_id_orig)
        assert linked
    # --- End Test Setup ---

    response = client.get(f'/post/{post_id_to_test}/edit')
    assert response.status_code == 200
    assert b"<h1>Edit Post</h1>" in response.data
    # Check if form fields are pre-filled with existing data
    assert bytes(post_title_orig, 'utf-8') in response.data
    # Check a snippet of the content (safer check)
    safer_snippet = "Original content"
    assert bytes(safer_snippet, 'utf-8') in response.data
    # Check if original tag is pre-filled in the input value
    # Need quotes around value for HTML attribute matching
    assert bytes(f'value="{tag_name_orig}"', 'utf-8') in response.data


def test_edit_post_submit(client):
    """Test submitting an edited post."""
    # --- Test Setup: Create a post to edit ---
    tag_name_orig = f'orig_edit_tag_{random.randint(100,999)}'
    post_id_to_test = None # Define outside 'with'
    with flask_app.app_context():
        post_title_orig = f"Edit Test Original Title {random.randint(100,999)}"
        post_content_orig = "Content before editing."
        post_id_to_test = db.add_post(post_title_orig, post_content_orig)
        assert post_id_to_test is not None
        tag_id_orig = db.add_or_get_tag(tag_name_orig)
        assert tag_id_orig is not None
        linked = db.link_post_tag(post_id_to_test, tag_id_orig)
        assert linked
    # --- End Test Setup ---

    # Generate unique data for the update
    unique_suffix = random.randint(1000, 9999)
    edited_post_data = {
        'title': f'Test Edited Post Title {unique_suffix}',
        'content': f'Test edited content {unique_suffix}.',
        'tags': 'edited, test, different' # New set of tags
    }

    # Simulate POST request to the edit URL
    response = client.post(f'/post/{post_id_to_test}/edit', data=edited_post_data)

    # Check for redirect after successful POST
    assert response.status_code == 302
    with flask_app.app_context():
        expected_url = url_for('post', post_id=post_id_to_test)
    assert response.location.endswith(expected_url)

    # Verify the changes in the database
    with flask_app.app_context():
        post_data_updated = db.get_post_by_id(post_id_to_test)
        assert post_data_updated is not None
        assert post_data_updated['title'] == edited_post_data['title']
        assert post_data_updated['content'] == edited_post_data['content']

        # Verify tag changes
        tags_updated = db.get_tags_for_post(post_id_to_test)
        tag_names_updated = {tag['name'] for tag in tags_updated}
        assert tag_names_updated == {'edited', 'test', 'different'}
        # Ensure original tag is gone
        assert tag_name_orig not in tag_names_updated

    # Follow redirect and check content on the post page
    response_after_redirect = client.get(response.location)
    assert response_after_redirect.status_code == 200
    assert bytes(edited_post_data['title'], 'utf-8') in response_after_redirect.data
    assert b'edited' in response_after_redirect.data # Check for one of the new tags
    assert bytes(tag_name_orig, 'utf-8') not in response_after_redirect.data # Check old tag is not displayed

