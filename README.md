# My Blog App - Backend Exam Project

A simple blog application built using Python, Flask, and SQLite as part of a backend exam project. It allows users to view blog posts, filter them by tags, add comments, and manage posts through create and edit functionalities.

## Project Overview

This application serves as a demonstration of backend web development principles using the Flask framework. It features dynamic content rendering via Jinja2 templates, data persistence using an SQLite database, and includes functionalities for managing blog posts, tags, and comments. The project also incorporates basic security measures and automated testing.

## Features

- **Homepage:** Displays a list of all blog posts, ordered by publication date (newest first), showing title, date, excerpt, and associated tags.
- **Single Post View:** Displays the full content of a selected blog post, including its title, date, tags, and any associated comments.
- **Tag Filtering:** Allows users to view a page listing all posts associated with a specific tag by clicking on tag links.
- **Comment System:** Users can view comments on a post and submit new comments via a form (includes basic validation).
- **Post Management:**
  - Create new blog posts with a title, content, and comma-separated tags.
  - Edit existing blog posts, updating title, content, and tags.
- **Database Interaction:** Uses SQLite for data storage, managed via a dedicated Python module (`db.py`).
- **Templating:** Utilizes Jinja2 for dynamic HTML rendering.
- **CLI Commands:** Includes commands (`flask init-db`, `flask seed-db`) for easy database setup and population with sample data.
- **Testing:** Incorporates automated tests using `pytest` to verify application functionality.
- **Security:** Implements parameterized queries to prevent SQL injection and relies on Jinja2's auto-escaping to mitigate XSS risks.

## Setup Instructions

1.  **Clone the repository:**

    ```bash
    git clone <https://github.com/sunred93/backend-exam>
    cd my_blog_app
    ```

2.  **Create and activate a virtual environment:**

    - It's recommended to use Python 3.10 or newer.
    - Navigate into the cloned `my_blog_app` directory.
    - Create the virtual environment:

      ```bash
      # Windows (Command Prompt/PowerShell)
      python -m venv .venv

      # macOS/Linux (Bash/Zsh)
      python3 -m venv .venv
      ```

    - Activate the virtual environment:

      ```bash
      # Windows (PowerShell)
      .\.venv\Scripts\Activate.ps1

      # Windows (Command Prompt)
      .\.venv\Scripts\activate.bat

      # macOS/Linux (Bash/Zsh)
      source .venv/bin/activate
      ```

    - You should see `(.venv)` at the beginning of your terminal prompt.

3.  **Install dependencies:**

    - Ensure your virtual environment is active.
    - Install the required packages:
      ```bash
      pip install -r requirements.txt
      ```

4.  **Set up environment variables:**

    - Create a file named `.env` in the root `my_blog_app` directory (alongside `app.py`).
    - Add the following line, replacing the example value with your own strong, random secret key:
      ```dotenv
      SECRET_KEY='a_very_strong_and_random_secret_key_here_!@#$%^&*()'
      ```
      _(The `SECRET_KEY` is used by Flask for session security and flash messages.)_

5.  **Initialize the Database:**

    - Ensure your virtual environment is active.
    - Run the following command to create the `blog.db` file and set up the necessary tables based on `schema.sql`:
      ```bash
      flask init-db
      ```

6.  **(Optional) Seed the Database:**
    - To populate the database with sample blog posts for testing and viewing:
      ```bash
      flask seed-db
      ```
      _(You can optionally specify the number of posts, e.g., `flask seed-db --posts 5`)_

## Running the Application

1.  Ensure your virtual environment is activated (`(.venv)` should be visible in your terminal prompt).
2.  Make sure the database has been initialized (and optionally seeded) using the `flask init-db` (and `flask seed-db`) commands.
3.  Run the Flask development server:
    ```bash
    python app.py
    ```
4.  The application will typically be available at `http://127.0.0.1:5001` (or check the address shown in the terminal output). Open this URL in your web browser.

## Running Tests

1.  Ensure your virtual environment is activated.
2.  Navigate to the root `my_blog_app` directory in your terminal.
3.  Run the automated tests using `pytest`:
    ```bash
    python -m pytest
    ```
4.  The output will show the number of tests collected and whether they passed or failed.
