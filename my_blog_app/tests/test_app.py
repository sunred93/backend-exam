# tests/test_app.py

import pytest
from flask import url_for
from app import app as flask_app # Import your Flask app instance
# Import your db module to potentially interact with the DB in tests
import db

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # You might want to configure the app for testing here
    # e.g., using a separate test database or config
    flask_app.config.update({
        "TESTING": True,
        # Add other test-specific configurations if needed
        # "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:", # Example for DB
        # If using a file DB, ensure tests don't interfere with dev DB
        # "DATABASE": "test_blog.db" # Example: Use a separate test DB file
    })

    # TODO: Consider setting up and tearing down a test database here
    # For now, assumes the dev DB (blog.db) might have data from seeding

    yield flask_app

    # TODO: Add cleanup logic here if needed (e.g., delete test_blog.db)


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

# --- Existing Test ---
def test_index_page_loads(client):
    """Test if the index page (/) loads successfully."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"<h1>All Blog Posts</h1>" in response.data

# --- New Tests ---
def test_post_page_loads(client):
    """Test if a valid single post page loads."""
    # Assumption: A post with ID 1 exists (e.g., from seeding)
    # A more robust test would create a known post first
    post_id_to_test = 1
    response = client.get(f'/post/{post_id_to_test}')

    # Check if the post exists in the database first
    # (This makes the test more robust if seeding changes)
    post_data = db.get_post_by_id(post_id_to_test)

    if post_data:
        assert response.status_code == 200
        # Check if the post title is in the response data
        # Encode title to bytes for comparison with response.data
        assert bytes(post_data['title'], 'utf-8') in response.data
    else:
        # If post 1 doesn't exist, the test should reflect that
        # or be skipped. For now, let's assume it should exist.
        pytest.fail(f"Test prerequisite failed: Post with ID {post_id_to_test} not found in database.")


def test_post_not_found(client):
    """Test accessing a non-existent post returns 404."""
    non_existent_post_id = 99999 # Choose an ID unlikely to exist
    response = client.get(f'/post/{non_existent_post_id}')
    assert response.status_code == 404

def test_add_comment(client):
    """Test submitting a comment to a post."""
    # Assumption: Post with ID 1 exists
    post_id_to_test = 1
    comment_data = {
        'author': 'Test Author',
        'content': 'This is a test comment.'
    }

    # Ensure the post exists before trying to comment
    post_data = db.get_post_by_id(post_id_to_test)
    if not post_data:
        pytest.fail(f"Test prerequisite failed: Post with ID {post_id_to_test} not found.")

    # Simulate POST request to the specific post URL
    response = client.post(f'/post/{post_id_to_test}', data=comment_data)

    # Check for redirect after successful POST (Post/Redirect/Get pattern)
    assert response.status_code == 302
    # Check if the redirect location is the same post page
    # Use url_for within the app context to generate the expected URL
    with flask_app.app_context():
        expected_url = url_for('post', post_id=post_id_to_test)
    # response.location might be relative or absolute, check if it ends with expected
    assert response.location.endswith(expected_url)

    # Optional: Follow the redirect and check if the comment appears
    response_after_redirect = client.get(f'/post/{post_id_to_test}')
    assert response_after_redirect.status_code == 200
    assert bytes(comment_data['author'], 'utf-8') in response_after_redirect.data
    assert bytes(comment_data['content'], 'utf-8') in response_after_redirect.data


def test_tag_page(client):
    """Test loading the page for a specific tag."""
    # Assumption: The tag 'travel' exists and has posts (from seeding)
    tag_name_to_test = 'travel'

    response = client.get(f'/tag/{tag_name_to_test}')

    assert response.status_code == 200
    # Check if the tag name appears in the heading
    assert bytes(f'Posts tagged with "{tag_name_to_test}"', 'utf-8') in response.data

    # Optional: More robust check - get posts for this tag from DB
    # and verify at least one title appears in the response.
    posts_for_tag = db.get_posts_by_tag(tag_name_to_test)
    if posts_for_tag:
        # Check if the title of the first post for this tag is present
        first_post_title = posts_for_tag[0]['title']
        assert bytes(first_post_title, 'utf-8') in response.data
    else:
        # If the tag has no posts, the page should still load but show a message
        assert b"No posts found for the tag" in response.data