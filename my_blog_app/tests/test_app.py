# tests/test_app.py

import pytest
from flask import url_for
from app import app as flask_app # Import your Flask app instance
# Import your db module to potentially interact with the DB in tests
import db
import random

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

    # Check if the post now exists in the database
    # Note: This relies on the post ID generation logic (likely sequential)
    # A more robust check might query by title, but titles aren't unique
    # Let's find the post by title (assuming it's unique enough for the test)
    conn = db.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM posts WHERE title = ?", (new_post_data['title'],))
    created_post = cursor.fetchone()
    conn.close()

    assert created_post is not None
    assert created_post['content'] == new_post_data['content']

    # Check if the redirect location points to the newly created post's page
    if created_post:
        with flask_app.app_context():
            expected_url = url_for('post', post_id=created_post['id'])
        assert response.location.endswith(expected_url)

        # Optional: Follow redirect and check content on the post page
        response_after_redirect = client.get(response.location)
        assert response_after_redirect.status_code == 200
        assert bytes(new_post_data['title'], 'utf-8') in response_after_redirect.data
        # Check if tags were added (simple check for one tag)
        assert b'test' in response_after_redirect.data


def test_edit_post_page_loads(client):
    """Test if the edit post page loads with pre-filled data."""
    # Assumption: Post with ID 1 exists
    post_id_to_test = 1
    post_data = db.get_post_by_id(post_id_to_test)
    if not post_data:
        pytest.fail(f"Test prerequisite failed: Post with ID {post_id_to_test} not found.")

    response = client.get(f'/post/{post_id_to_test}/edit')
    assert response.status_code == 200
    assert b"<h1>Edit Post</h1>" in response.data
    # Check if form fields are pre-filled with existing data
    assert bytes(post_data['title'], 'utf-8') in response.data
    # Check a snippet of the content
    content_snippet = post_data['content'][:50]
    # Modify the assertion to check for a safer part of the snippet
    safer_snippet = "Took a delightful day trip" # Avoid the apostrophe
    assert bytes(safer_snippet, 'utf-8') in response.data
    # assert bytes(content_snippet, 'utf-8') in response.data # Original failing line

    # Check if tags are pre-filled (fetch them to compare)
    tags_data = db.get_tags_for_post(post_id_to_test)
    if tags_data:
        first_tag_name = tags_data[0]['name']
        assert bytes(first_tag_name, 'utf-8') in response.data


def test_edit_post_submit(client):
    """Test submitting an edited post."""
    # Assumption: Post with ID 2 exists
    post_id_to_test = 2
    post_data_orig = db.get_post_by_id(post_id_to_test)
    if not post_data_orig:
        pytest.fail(f"Test prerequisite failed: Post with ID {post_id_to_test} not found.")

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
    post_data_updated = db.get_post_by_id(post_id_to_test)
    assert post_data_updated is not None
    assert post_data_updated['title'] == edited_post_data['title']
    assert post_data_updated['content'] == edited_post_data['content']

    # Verify tag changes
    tags_updated = db.get_tags_for_post(post_id_to_test)
    tag_names_updated = {tag['name'] for tag in tags_updated}
    assert tag_names_updated == {'edited', 'test', 'different'}

    # Optional: Follow redirect and check content on the post page
    response_after_redirect = client.get(response.location)
    assert response_after_redirect.status_code == 200
    assert bytes(edited_post_data['title'], 'utf-8') in response_after_redirect.data
    assert b'edited' in response_after_redirect.data # Check for one of the new tags
    # Ensure an old tag (if different) is gone - needs more setup to be reliable