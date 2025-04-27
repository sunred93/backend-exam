# app.py

import os
import sqlite3 # Import sqlite3 to catch its specific errors if needed
import click   # Import click for CLI commands
import datetime
from datetime import timezone

# Make sure request, redirect, url_for, flash are imported
from flask import Flask, render_template, abort, request, redirect, url_for, flash, current_app
from dotenv import load_dotenv
import db
from faker import Faker
# Optional: For secure filenames if you choose to use it alongside UUID
# from werkzeug.utils import secure_filename

# Load environment variables from .env file
load_dotenv()

# Create the Flask application instance
app = Flask(__name__)

# Load configuration from environment variables
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'a_default_secret_key_for_dev')
# Add the database path to the config
app.config['DATABASE'] = db.DEFAULT_DATABASE_PATH

# --- Initialize database functions and commands with the app ---
db.init_app(app)

@app.context_processor
def inject_now():
    """Injects the current UTC datetime into the template context."""
    # Using utcnow() is generally recommended for server-side time
    return {'now': datetime.datetime.now(timezone.utc)}

# --- Database Seeding Command (Updated for image_filename) ---
@app.cli.command('seed-db')
@click.option('--posts', default=25, help='Number of posts to create (max based on static data).')
def seed_db_command(posts):
    """Seeds the database with sample blog posts, tags, and placeholder images."""
    fake = Faker()

    # Define your static posts (Add image_filename, can be None or a path)
    # NOTE: Ensure these image files actually exist in static/uploads/images/
    #       or handle cases where they might be missing in templates.
    #       Using None is safer if you don't have placeholder images ready.
    static_posts = [
        {
            "title": "Discovering the Charm of Gamlebyen in Fredrikstad",
            "content": "Took a delightful day trip to Fredrikstad's Gamlebyen (Old Town) recently. The well-preserved fortifications and charming cobblestone streets were like stepping back in time. Definitely worth a visit if you're in the area!",
            "tags": ["travel", "history", "fredrikstad", "norway", "gamlebyen"],
            "image_filename": None
        },
        {
            "title": "My First Attempt at Making Norwegian Lefse",
            "content": "I decided to try my hand at making traditional Norwegian lefse. Let's just say it was an... experience! While the first few attempts were less than perfect, I'm determined to master this delicious flatbread. Any seasoned lefse bakers out there with advice?",
            "tags": ["baking", "food", "norwegian", "lefse", "tradition"],
            "image_filename": None
        },
        {
            "title": "A Guide to the Best Beaches in Vestfold for Summer",
            "content": "With summer just around the corner, it's time to start thinking about beach days! Vestfold boasts some stunning stretches of coastline. This guide highlights a few of my favorite spots for swimming, sunbathing, and enjoying the sea air.",
            "tags": ["summer", "beach", "vestfold", "norway", "travel"],
            "image_filename": None
        },
        {
            "title": "Exploring the Viking History of Vestfold County",
            "content": "Vestfold has a rich Viking heritage, and there are fascinating historical sites scattered throughout the region. I spent some time exploring the Midgard Viking Centre and the Oseberg burial mound, and it truly brought history to life.",
            "tags": ["history", "viking", "vestfold", "norway", "museum"],
            "image_filename": None
        },
        {
            "title": "Book Review: \"Project Hail Mary\" by Andy Weir",
            "content": "Absolutely loved \"Project Hail Mary\"! Andy Weir has done it again with this engaging and witty sci-fi thriller. The characters are fantastic, and the science is surprisingly accessible. A must-read for any sci-fi fan.",
            "tags": ["books", "review", "sci-fi", "andy weir", "reading"],
            "image_filename": None
        },
        {
            "title": "Simple Tips for Growing Your Own Herbs Indoors",
            "content": "Fresh herbs can elevate any dish! I've started growing a small herb garden on my windowsill, and it's been surprisingly easy and rewarding. Here are a few simple tips to get you started with your own indoor herb garden.",
            "tags": ["gardening", "herbs", "diy", "food", "home"],
            "image_filename": None
        },
        {
            "title": "A Day Trip to Jomfruland National Park",
            "content": "Jomfruland National Park is a true gem! This car-free island offers stunning natural beauty, perfect for hiking and birdwatching. The ferry ride over is also a treat. A fantastic escape from the mainland.",
            "tags": ["travel", "nature", "hiking", "norway", "national park", "jomfruland"],
            "image_filename": None
        },
        {
            "title": "Supporting Local Craftspeople in the Tønsberg Area",
            "content": "I recently visited a local craft fair and was so impressed by the talent and artistry on display. Supporting local craftspeople not only gives you unique, handmade items but also strengthens our community. Let's celebrate their work!",
            "tags": ["local", "crafts", "tønsberg", "community", "shopping"],
            "image_filename": None
        },
        {
            "title": "Quick and Healthy Breakfast Ideas for Busy Mornings",
            "content": "Mornings can be hectic, but skipping breakfast is never a good idea. Here are a few quick and healthy breakfast ideas that will fuel you up for the day ahead, even when you're short on time.",
            "tags": ["food", "health", "breakfast", "recipes", "quick meals"],
            "image_filename": None
        },
        {
            "title": "The Architectural History of Tønsberg's Waterfront",
            "content": "Tønsberg's waterfront has a fascinating architectural history, reflecting different periods and styles. From the Brygga to more modern buildings, each structure tells a story about the town's development. Let's take a closer look at some of its key features.",
            "tags": ["architecture", "history", "tønsberg", "local", "waterfront"],
            "image_filename": None
        },
        {
            "title": "Exploring the Hiking Trails of Rauland",
            "content": "Ventured a bit further to Rauland and was rewarded with some breathtaking hiking trails. The mountain scenery was stunning, and the fresh air was invigorating. A perfect destination for outdoor enthusiasts.",
            "tags": ["hiking", "nature", "mountains", "norway", "rauland", "travel"],
            "image_filename": None
        },
        {
            "title": "My Favorite Norwegian Cookbooks for Culinary Inspiration",
            "content": "Looking to explore Norwegian cuisine? These are some of my favorite cookbooks that offer a fantastic introduction to traditional dishes and modern interpretations. Get ready to bring the flavors of Norway into your kitchen!",
            "tags": ["cookbooks", "food", "norwegian", "cuisine", "recipes", "review"],
            "image_filename": None
        },
        {
            "title": "A Guide to Cycling Routes in Vestfold",
            "content": "Vestfold is a fantastic region to explore by bike. From coastal paths to scenic countryside roads, there are cycling routes for all levels. This guide highlights some of the best options for a two-wheeled adventure.",
            "tags": ["cycling", "vestfold", "norway", "outdoors", "sport", "guide"],
            "image_filename": None
        },
        {
            "title": "The Importance of Preserving Local History",
            "content": "Preserving local history is crucial for understanding our roots and connecting with the past. Museums, archives, and historical societies play a vital role in this effort. Let's discuss the importance of supporting these institutions.",
            "tags": ["history", "local", "preservation", "community", "culture"],
            "image_filename": None
        },
        {
            "title": "Book Review: \"Where the Crawdads Sing\" by Delia Owens",
            "content": "\Where the Crawdads Sing\" is a beautifully written novel with a captivating story and vivid descriptions of the natural world. The characters are compelling, and the mystery at its heart keeps you hooked until the very end.",
            "tags": ["books", "review", "fiction", "nature", "reading"],
            "image_filename": None
        },
        {
            "title": "Tips for Reducing Food Waste at Home",
            "content": "Food waste is a significant issue, but there are many simple steps we can take at home to minimize it. From meal planning to proper storage, every little effort makes a difference. Let's share our best food-saving tips!",
            "tags": ["sustainability", "food waste", "home", "tips", "environment"],
            "image_filename": None
        },
        {
            "title": "A Visit to the Haugar Art Museum in Tønsberg",
            "content": "The Haugar Art Museum is a cultural gem in Tønsberg, showcasing a diverse range of contemporary and historical art. My recent visit was inspiring, and I highly recommend checking out their current exhibitions.",
            "tags": ["art", "museum", "tønsberg", "culture", "local"],
            "image_filename": None
        },
        {
            "title": "Easy DIY Home Decor Projects to Spruce Up Your Space",
            "content": "Looking to refresh your home without breaking the bank? DIY home decor projects are a fun and creative way to personalize your space. Here are a few easy ideas to get you started..",
            "tags": ["diy", "home decor", "crafts", "interior design", "budget"],
            "image_filename": None
        },
        {
            "title": "The Benefits of Spending Time in Nature for Well-being",
            "content": "In our increasingly fast-paced and technology-driven lives,it's easy to become disconnected from the natural world. However, numerous studies have shown that spending time in nature offers profound benefits for both our physical and mental well-being. Whether it's a leisurely walk in a local park, an invigorating hike through a dense forest, or simply sitting by a tranquil lake, these moments of connection with the natural world can significantly improve our mood and reduce stress levels. The positive impacts extend beyond just our mental state. Physically, spending time outdoors encourages movement and exercise, contributing to better cardiovascular health and stronger immune systems. Breathing in fresh air, often cleaner and richer in oxygen than indoor environments, can revitalize our bodies. Sunlight exposure, in moderation, helps our bodies produce essential Vitamin D, crucial for bone health and overall immunity. Mentally and emotionally, nature provides a sanctuary from the demands of daily life. The sights, sounds, and smells of the natural world can have a calming effect, lowering cortisol levels (the stress hormone) and promoting a sense of peace. Studies have even shown that spending time in nature can improve focus and cognitive function, reduce symptoms of anxiety and depression, and foster a greater sense of creativity. Even small doses of nature can make a difference. Incorporating natural elements into our daily routines, such as bringing plants indoors or finding a green space during a lunch break, can offer subtle yet significant benefits. The key is to intentionally seek out opportunities to connect with the natural world, allowing ourselves to be present in the moment and absorb its restorative power. So, step outside, breathe deeply, and experience the incredible benefits that nature has to offer.",
            "tags": ["nature", "wellness", "health", "outdoors", "mental health"],
            "image_filename": "uploads/images/nature_wellbeing.jpg"
        },
        {
            "title": "Exploring the Coastal Path from Stavern to Nevlunghavn",
            "content": "The coastal path between Stavern and Nevlunghavn offers stunning views of the Skagerrak coastline. It's a beautiful walk with charming harbors and picturesque scenery along the way.",
            "tags": ["hiking", "coastal", "norway", "stavern", "travel", "nature"],
            "image_filename": None
        },
        {
            "title": "My Journey Learning the Norwegian Language",
            "content": "Learning a new language can be challenging but also incredibly rewarding. I've been on a journey to learn Norwegian, and while there have been ups and downs, I'm enjoying the process of connecting with the local culture on a deeper level. Any fellow language learners out there?",
            "tags": ["language", "learning", "norwegian", "culture", "personal"],
            "image_filename": None
        },
        {
            "title": "The Best Picnic Spots in the Tønsberg Area",
            "content": "With the weather getting warmer, it's the perfect time for a picnic! Tønsberg and its surroundings offer plenty of beautiful spots to enjoy a meal outdoors. Here are a few of my favorite picnic locations.",
            "tags": ["picnic", "tønsberg", "outdoors", "summer", "local", "food"],
            "image_filename": None
        },
        {
            "title": "Supporting Local Farmers Markets in Vestfold",
            "content": "Farmers markets are a fantastic way to access fresh, seasonal produce and support local farmers. Vestfold has some great markets offering a variety of goods. Let's celebrate the bounty of our region!",
            "tags": ["farmers market", "local", "food", "vestfold", "support local", "community"],
            "image_filename": None
        },
        {
            "title": "A Guide to Birdwatching in Vestfold's Wetlands",
            "content": "Vestfold's wetlands are a haven for birdlife. Birdwatching can be a relaxing and rewarding hobby, and there are several excellent spots in the region to observe various species.",
            "tags": ["birdwatching", "nature", "vestfold", "wetlands", "hobby", "wildlife"],
            "image_filename": None
        },
        {
            "title": "Reflecting on the Beauty of the Changing Seasons in Norway",
            "content": "Norway's distinct seasons each offer their own unique beauty, from the vibrant greens of summer to the snowy landscapes of winter. Taking the time to appreciate these changes can bring a sense of wonder and connection to nature.",
            "tags": ["seasons", "norway", "nature", "reflection", "beauty"],
            "image_filename": None
        }
    ]

    num_posts_to_seed = min(posts, len(static_posts))
    if posts > len(static_posts):
        click.echo(f"Warning: Requested {posts} posts, but only {len(static_posts)} static posts are available. Seeding {len(static_posts)}.")

    click.echo(f'Seeding database with {num_posts_to_seed} posts from static data...')

    try:
        for post_data in static_posts[:num_posts_to_seed]:
            title = post_data["title"]
            content = post_data["content"]
            tag_names = post_data.get("tags", [])
            # Get the image filename from static data
            image_filename = post_data.get("image_filename", None)

            # Add the post to the database, including the image filename
            post_id = db.add_post(title, content, image_filename=image_filename) # Pass image_filename

            if post_id:
                click.echo(f"  Added post '{title}' (ID: {post_id})")
                if image_filename:
                    click.echo(f"    - Associated image: {image_filename}")
                if not tag_names:
                    click.echo(f"    - No static tags defined for this post.")

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
        click.echo(f'Error during database seeding: {e}', err=True)


# --- Routes ---
@app.route('/')
def index():
    """Renders the homepage, listing all blog posts with their tags."""
    try:
        # get_all_posts now includes image_filename
        posts_raw = db.get_all_posts()
        posts_with_tags = []
        for post in posts_raw:
            tags = db.get_tags_for_post(post['id'])
            post_dict = dict(post)
            post_dict['tags'] = tags
            posts_with_tags.append(post_dict)

        return render_template('index.html', posts=posts_with_tags)
    except Exception as e:
        app.logger.error(f"Error fetching posts/tags for index page: {e}")
        return "<h1>An error occurred fetching posts.</h1>", 500

@app.route('/post/<int:post_id>', methods=('GET', 'POST'))
def post(post_id):
    """Shows a single blog post and handles comment submission."""
    # get_post_by_id now includes image_filename
    post_data = db.get_post_by_id(post_id)
    if post_data is None:
        abort(404)

    if request.method == 'POST':
        author = request.form.get('author')
        content = request.form.get('content')

        if not author or not content:
            flash('Author Name and Comment content are required!', 'error')
        else:
            comment_id = db.add_comment(post_id, author, content)
            if comment_id:
                flash('Comment added successfully!', 'success')
            else:
                flash('Failed to add comment.', 'error')
            return redirect(url_for('post', post_id=post_id))

    # --- Handle GET request ---
    tags_data = db.get_tags_for_post(post_id)
    comments_data = db.get_comments_for_post(post_id)

    return render_template('post.html',
                           post=post_data,
                           tags=tags_data,
                           comments=comments_data)


@app.route('/tag/<string:tag_name>')
def posts_by_tag(tag_name):
    """Shows all posts associated with a specific tag."""
    try:
        # get_posts_by_tag now includes image_filename
        posts = db.get_posts_by_tag(tag_name)
        return render_template('tag_posts.html', tag_name=tag_name, posts=posts)
    except Exception as e:
        app.logger.error(f"Error fetching posts for tag '{tag_name}': {e}")
        return "<h1>An error occurred fetching posts for this tag.</h1>", 500


def process_tags(tags_string):
    """Helper function to process a comma-separated tag string."""
    if not tags_string:
        return []
    tags = [tag.strip() for tag in tags_string.split(',') if tag.strip()]
    return tags

# --- Create Post Route (Updated for Image Upload) ---
@app.route('/post/new', methods=('GET', 'POST'))
def create_post():
    """Handles creation of a new blog post, including image upload."""
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        tags_string = request.form.get('tags', '')
        image_file = request.files.get('image') # Get the uploaded file object

        if not title or not content:
            flash('Title and Content are required!', 'error')
            # Pass back entered data
            return render_template('create_edit_post.html',
                                   post={'title': title, 'content': content, 'tags_string': tags_string})
        else:
            saved_image_filename = None # Initialize filename as None
            if image_file:
                # Attempt to save the image using the helper function from db.py
                saved_image_filename = db.save_image(image_file)
                if not saved_image_filename:
                    # save_image returns None on failure (e.g., wrong file type)
                    flash('Image upload failed. Allowed types: png, jpg, jpeg, gif.', 'warning')
                    # Decide if you want to proceed without image or stop
                    # Let's proceed without image for now, but keep the warning
                    pass # saved_image_filename remains None

            # Add post to DB, passing the saved filename (or None)
            post_id = db.add_post(title, content, image_filename=saved_image_filename)

            if post_id:
                # Process and link tags (existing logic)
                tag_names = process_tags(tags_string)
                for tag_name in tag_names:
                    tag_id = db.add_or_get_tag(tag_name)
                    if tag_id:
                        db.link_post_tag(post_id, tag_id)
                    else:
                        flash(f"Failed to add or find tag '{tag_name}'.", 'warning')

                flash('Post created successfully!', 'success')
                return redirect(url_for('post', post_id=post_id))
            else:
                flash('Failed to create post in database.', 'error')
                # If post creation failed, maybe delete the uploaded image if it exists?
                if saved_image_filename:
                     db.delete_image_file(saved_image_filename) # Attempt to clean up
                return render_template('create_edit_post.html',
                                       post={'title': title, 'content': content, 'tags_string': tags_string})

    # --- Handle GET request ---
    return render_template('create_edit_post.html')


# --- Edit Post Route (Updated for Image Upload/Update) ---
@app.route('/post/<int:post_id>/edit', methods=('GET', 'POST'))
def edit_post(post_id):
    """Handles editing of an existing blog post, including image update."""
    # Fetch the existing post (needed for both GET and POST)
    post_data = db.get_post_by_id(post_id)
    if post_data is None:
        abort(404)

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        tags_string = request.form.get('tags', '')
        image_file = request.files.get('image') # Check for new image upload

        # Basic validation
        if not title or not content:
            flash('Title and Content are required!', 'error')
            # Re-render form with existing post_id and entered data
            # Need to reconstruct the 'post' dict for the template, including original image
            current_tags = db.get_tags_for_post(post_id)
            tags_string_orig = ', '.join([t['name'] for t in current_tags])
            post_for_template = dict(post_data) # Start with original data
            post_for_template['title'] = title # Overwrite with user input
            post_for_template['content'] = content # Overwrite with user input
            post_for_template['tags_string'] = tags_string or tags_string_orig
            return render_template('create_edit_post.html', post=post_for_template)

        # --- Handle Image Update Logic ---
        new_image_filename = None
        update_image_flag = False # Flag to tell update_post whether to change image field

        if image_file: # If a new file was uploaded
            old_image_filename = post_data['image_filename'] # Get current image path
            # Attempt to save the new image
            saved_path = db.save_image(image_file)
            if saved_path:
                new_image_filename = saved_path
                update_image_flag = True # We have a new image, so update the DB field
                # Delete the old image *after* successfully saving the new one
                if old_image_filename:
                    db.delete_image_file(old_image_filename)
            else:
                # Failed to save new image (e.g., wrong type)
                flash('New image upload failed. Allowed types: png, jpg, jpeg, gif. Image not updated.', 'warning')
                # Keep update_image_flag as False, new_image_filename as None

        # --- Update Post in Database ---
        # Pass the new filename (or None) and the update flag
        updated = db.update_post(post_id, title, content,
                                 image_filename=new_image_filename,
                                 update_image=update_image_flag)

        if updated:
            # Update tags (existing logic)
            db.unlink_all_tags_for_post(post_id)
            tag_names = process_tags(tags_string)
            for tag_name in tag_names:
                tag_id = db.add_or_get_tag(tag_name)
                if tag_id:
                    db.link_post_tag(post_id, tag_id)
                else:
                    flash(f"Failed to add or find tag '{tag_name}'.", 'warning')

            flash('Post updated successfully!', 'success')
            return redirect(url_for('post', post_id=post_id))
        else:
            flash('Failed to update post in database.', 'error')
            # If update failed, maybe delete the newly uploaded image if it exists?
            if update_image_flag and new_image_filename:
                 db.delete_image_file(new_image_filename) # Attempt cleanup
            # Re-render form with entered data
            current_tags = db.get_tags_for_post(post_id)
            tags_string_orig = ', '.join([t['name'] for t in current_tags])
            post_for_template = dict(post_data) # Start with original data
            post_for_template['title'] = title
            post_for_template['content'] = content
            post_for_template['tags_string'] = tags_string or tags_string_orig
            # Keep original image if update failed
            return render_template('create_edit_post.html', post=post_for_template)

    # --- Handle GET request ---
    # Fetch current tags and format them as a string for the input field
    current_tags = db.get_tags_for_post(post_id)
    tags_string = ', '.join([tag['name'] for tag in current_tags])

    # Convert Row to dict and add tags_string for template consistency
    # post_data already includes 'image_filename' from get_post_by_id
    post_for_template = dict(post_data)
    post_for_template['tags_string'] = tags_string

    return render_template('create_edit_post.html', post=post_for_template)


# --- Optional: Add a Delete Route ---
@app.route('/post/<int:post_id>/delete', methods=('POST',))
def delete_post_route(post_id):
    """Handles deletion of a post."""
    # You might want to add authentication/authorization checks here later
    deleted = db.delete_post(post_id) # This now also handles image file deletion
    if deleted:
        flash('Post deleted successfully.', 'success')
    else:
        flash('Failed to delete post. It might have already been removed.', 'error')
    return redirect(url_for('index'))


# --- Run the development server ---
if __name__ == '__main__':
    print("--- Attempting to run Flask app ---")
    # Ensure the static/uploads/images directory exists on startup
    upload_dir = os.path.join(app.static_folder, db.IMAGE_UPLOAD_FOLDER)
    os.makedirs(upload_dir, exist_ok=True)
    print(f"Static folder: {app.static_folder}")
    print(f"Upload directory ensured: {upload_dir}")

    app.run(debug=True, port=5001)
