# app.py

import os
import sqlite3 # Import sqlite3 to catch its specific errors if needed
import click   # Import click for CLI commands
from flask import Flask, render_template, abort
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
@click.option('--posts', default=25, help='Number of posts to create (max based on static data).') # Default to max available
def seed_db_command(posts):
    """Seeds the database with sample blog posts and tags from static data."""
    fake = Faker() # Keep for potential random tags if needed

    # Define your static posts (using the Gemini data)
    static_posts = [
        {
            "title": "Discovering the Charm of Gamlebyen in Fredrikstad",
            "content": "Took a delightful day trip to Fredrikstad's Gamlebyen (Old Town) recently. The well-preserved fortifications and charming cobblestone streets were like stepping back in time. Definitely worth a visit if you're in the area!",
            "tags": ["travel", "history", "fredrikstad", "norway", "gamlebyen"]
        },
        {
            "title": "My First Attempt at Making Norwegian Lefse",
            "content": "I decided to try my hand at making traditional Norwegian lefse. Let's just say it was an... experience! While the first few attempts were less than perfect, I'm determined to master this delicious flatbread. Any seasoned lefse bakers out there with advice?",
            "tags": ["baking", "food", "norwegian", "lefse", "tradition"]
        },
        {
            "title": "A Guide to the Best Beaches in Vestfold for Summer",
            "content": "With summer just around the corner, it's time to start thinking about beach days! Vestfold boasts some stunning stretches of coastline. This guide highlights a few of my favorite spots for swimming, sunbathing, and enjoying the sea air.",
            "tags": ["summer", "beach", "vestfold", "norway", "travel"]
        },
        {
            "title": "Exploring the Viking History of Vestfold County",
            "content": "Vestfold has a rich Viking heritage, and there are fascinating historical sites scattered throughout the region. I spent some time exploring the Midgard Viking Centre and the Oseberg burial mound, and it truly brought history to life.",
            "tags": ["history", "viking", "vestfold", "norway", "museum"]
        },
        {
            "title": "Book Review: \"Project Hail Mary\" by Andy Weir",
            "content": "Absolutely loved \"Project Hail Mary\"! Andy Weir has done it again with this engaging and witty sci-fi thriller. The characters are fantastic, and the science is surprisingly accessible. A must-read for any sci-fi fan.",
            "tags": ["books", "review", "sci-fi", "andy weir", "reading"]
        },
        {
            "title": "Simple Tips for Growing Your Own Herbs Indoors",
            "content": "Fresh herbs can elevate any dish! I've started growing a small herb garden on my windowsill, and it's been surprisingly easy and rewarding. Here are a few simple tips to get you started with your own indoor herb garden.",
            "tags": ["gardening", "herbs", "diy", "food", "home"]
        },
        {
            "title": "A Day Trip to Jomfruland National Park",
            "content": "Jomfruland National Park is a true gem! This car-free island offers stunning natural beauty, perfect for hiking and birdwatching. The ferry ride over is also a treat. A fantastic escape from the mainland.",
            "tags": ["travel", "nature", "hiking", "norway", "national park", "jomfruland"]
        },
        {
            "title": "Supporting Local Craftspeople in the Tønsberg Area",
            "content": "I recently visited a local craft fair and was so impressed by the talent and artistry on display. Supporting local craftspeople not only gives you unique, handmade items but also strengthens our community. Let's celebrate their work!",
            "tags": ["local", "crafts", "tønsberg", "community", "shopping"]
        },
        {
            "title": "Quick and Healthy Breakfast Ideas for Busy Mornings",
            "content": "Mornings can be hectic, but skipping breakfast is never a good idea. Here are a few quick and healthy breakfast ideas that will fuel you up for the day ahead, even when you're short on time.",
            "tags": ["food", "health", "breakfast", "recipes", "quick meals"]
        },
        {
            "title": "The Architectural History of Tønsberg's Waterfront",
            "content": "Tønsberg's waterfront has a fascinating architectural history, reflecting different periods and styles. From the Brygga to more modern buildings, each structure tells a story about the town's development. Let's take a closer look at some of its key features.",
            "tags": ["architecture", "history", "tønsberg", "local", "waterfront"]
        },
        {
            "title": "Exploring the Hiking Trails of Rauland",
            "content": "Ventured a bit further to Rauland and was rewarded with some breathtaking hiking trails. The mountain scenery was stunning, and the fresh air was invigorating. A perfect destination for outdoor enthusiasts.",
            "tags": ["hiking", "nature", "mountains", "norway", "rauland", "travel"]
        },
        {
            "title": "My Favorite Norwegian Cookbooks for Culinary Inspiration",
            "content": "Looking to explore Norwegian cuisine? These are some of my favorite cookbooks that offer a fantastic introduction to traditional dishes and modern interpretations. Get ready to bring the flavors of Norway into your kitchen!",
            "tags": ["cookbooks", "food", "norwegian", "cuisine", "recipes", "review"]
        },
        {
            "title": "A Guide to Cycling Routes in Vestfold",
            "content": "Vestfold is a fantastic region to explore by bike. From coastal paths to scenic countryside roads, there are cycling routes for all levels. This guide highlights some of the best options for a two-wheeled adventure.",
            "tags": ["cycling", "vestfold", "norway", "outdoors", "sport", "guide"]
        },
        {
            "title": "The Importance of Preserving Local History",
            "content": "Preserving local history is crucial for understanding our roots and connecting with the past. Museums, archives, and historical societies play a vital role in this effort. Let's discuss the importance of supporting these institutions.",
            "tags": ["history", "local", "preservation", "community", "culture"]
        },
        {
            "title": "Book Review: \"Where the Crawdads Sing\" by Delia Owens",
            "content": "\"Where the Crawdads Sing\" is a beautifully written novel with a captivating story and vivid descriptions of the natural world. The characters are compelling, and the mystery at its heart keeps you hooked until the very end.",
            "tags": ["books", "review", "fiction", "nature", "reading"]
        },
        {
            "title": "Tips for Reducing Food Waste at Home",
            "content": "Food waste is a significant issue, but there are many simple steps we can take at home to minimize it. From meal planning to proper storage, every little effort makes a difference. Let's share our best food-saving tips!",
            "tags": ["sustainability", "food waste", "home", "tips", "environment"]
        },
        {
            "title": "A Visit to the Haugar Art Museum in Tønsberg",
            "content": "The Haugar Art Museum is a cultural gem in Tønsberg, showcasing a diverse range of contemporary and historical art. My recent visit was inspiring, and I highly recommend checking out their current exhibitions.",
            "tags": ["art", "museum", "tønsberg", "culture", "local"]
        },
        {
            "title": "Easy DIY Home Decor Projects to Spruce Up Your Space",
            "content": "Looking to refresh your home without breaking the bank? DIY home decor projects are a fun and creative way to personalize your space. Here are a few easy ideas to get you started.",
            "tags": ["diy", "home decor", "crafts", "interior design", "budget"]
        },
        {
            "title": "The Benefits of Spending Time in Nature for Well-being",
            "content": "Spending time in nature has been proven to have numerous benefits for our physical and mental well-being. Whether it's a walk in the park or a hike in the forest, connecting with the natural world can significantly improve our mood and reduce stress.",
            "tags": ["nature", "wellness", "health", "outdoors", "mental health"]
        },
        {
            "title": "Exploring the Coastal Path from Stavern to Nevlunghavn",
            "content": "The coastal path between Stavern and Nevlunghavn offers stunning views of the Skagerrak coastline. It's a beautiful walk with charming harbors and picturesque scenery along the way.",
            "tags": ["hiking", "coastal", "norway", "stavern", "travel", "nature"]
        },
        {
            "title": "My Journey Learning the Norwegian Language",
            "content": "Learning a new language can be challenging but also incredibly rewarding. I've been on a journey to learn Norwegian, and while there have been ups and downs, I'm enjoying the process of connecting with the local culture on a deeper level. Any fellow language learners out there?",
            "tags": ["language", "learning", "norwegian", "culture", "personal"]
        },
        {
            "title": "The Best Picnic Spots in the Tønsberg Area",
            "content": "With the weather getting warmer, it's the perfect time for a picnic! Tønsberg and its surroundings offer plenty of beautiful spots to enjoy a meal outdoors. Here are a few of my favorite picnic locations.",
            "tags": ["picnic", "tønsberg", "outdoors", "summer", "local", "food"]
        },
        {
            "title": "Supporting Local Farmers Markets in Vestfold",
            "content": "Farmers markets are a fantastic way to access fresh, seasonal produce and support local farmers. Vestfold has some great markets offering a variety of goods. Let's celebrate the bounty of our region!",
            "tags": ["farmers market", "local", "food", "vestfold", "support local", "community"]
        },
        {
            "title": "A Guide to Birdwatching in Vestfold's Wetlands",
            "content": "Vestfold's wetlands are a haven for birdlife. Birdwatching can be a relaxing and rewarding hobby, and there are several excellent spots in the region to observe various species.",
            "tags": ["birdwatching", "nature", "vestfold", "wetlands", "hobby", "wildlife"]
        },
        {
            "title": "Reflecting on the Beauty of the Changing Seasons in Norway",
            "content": "Norway's distinct seasons each offer their own unique beauty, from the vibrant greens of summer to the snowy landscapes of winter. Taking the time to appreciate these changes can bring a sense of wonder and connection to nature.",
            "tags": ["seasons", "norway", "nature", "reflection", "beauty"]
        }
    ]

    # Ensures it don't try to seed more posts than it  have static data for
    # Also respect the --posts option if it's less than the total available
    num_posts_to_seed = min(posts, len(static_posts))
    if posts > len(static_posts):
        click.echo(f"Warning: Requested {posts} posts, but only {len(static_posts)} static posts are available. Seeding {len(static_posts)}.")

    click.echo(f'Seeding database with {num_posts_to_seed} posts from static data...')

    try:
        # Loop through the static data up to the determined limit
        for post_data in static_posts[:num_posts_to_seed]:
            title = post_data["title"]
            content = post_data["content"]
            # Use the defined tags, default to empty list if missing
            tag_names = post_data.get("tags", [])

            # Add the post to the database
            post_id = db.add_post(title, content)

            if post_id:
                click.echo(f"  Added post '{title}' (ID: {post_id})")
                # Add tags and link them to the post
                if not tag_names:
                    # Optional: Add random tags if none are defined statically
                    # tag_names = fake.words(nb=fake.random_int(min=1, max=3), unique=True)
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
        # Catch potential errors during seeding
        click.echo(f'Error during database seeding: {e}', err=True)



# --- Routes ---
@app.route('/')
def index():
    """Renders the homepage, listing all blog posts with their tags."""
    try:
        posts_raw = db.get_all_posts() # Get basic post data
        posts_with_tags = []
        for post in posts_raw:
            # Fetch tags for the current post
            tags = db.get_tags_for_post(post['id'])
            # Convert the sqlite3.Row post object to a dictionary
            post_dict = dict(post)
            # Add the list of tag objects (also sqlite3.Row) to the dictionary
            post_dict['tags'] = tags
            posts_with_tags.append(post_dict)

        # Pass the list of post dictionaries (each containing its tags) to the template
        return render_template('index.html', posts=posts_with_tags)
    except Exception as e:
        # Basic error handling for the route
        app.logger.error(f"Error fetching posts/tags for index page: {e}")
        # You might want a proper error page later
        return "<h1>An error occurred fetching posts.</h1>", 500


@app.route('/post/<int:post_id>')
def post(post_id):
    """Shows a single blog post identified by post_id, including tags."""
    post_data = db.get_post_by_id(post_id)
    if post_data is None:
        # If get_post_by_id returns None, the post wasn't found
        abort(404) # Let Flask handle this exception

    # Fetch the tags specifically for this post
    tags_data = db.get_tags_for_post(post_id)
    # TODO: Fetch comments for this post later

    # Pass both the post data and the tags data to the template
    return render_template('post.html', post=post_data, tags=tags_data)

# --- Add more routes and logic below ---
# We'll add the route for individual posts next




# --- Run the development server ---
if __name__ == '__main__':
    print("--- Attempting to run Flask app ---")
    app.run(debug=True, port=5001) # Using port 5001 as decided earlier
