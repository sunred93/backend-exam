print("--- Script starting ---") # Add this line

import os
from flask import Flask
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create the Flask application instance
app = Flask(__name__)

# Optional: Load configuration from environment variables (example)
# You might want a secret key for sessions, etc.
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'a_default_secret_key_for_dev')

# Define a simple route for the homepage
@app.route('/')
def index():
    """Renders the homepage."""
    return "<h1>Welcome to My Blog App!</h1>"

# --- Add more routes and logic below ---


# --- Run the development server ---
if __name__ == '__main__':
    print("--- Attempting to run Flask app ---") # Add this line
    # Debug=True enables auto-reloading and detailed error pages
    # Use host='0.0.0.0' to make it accessible on your network (optional)
    # Use port=xxxx to specify a different port (default is 5000)
    app.run(debug=True, port=5001)

