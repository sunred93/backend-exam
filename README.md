# backend-exam

a new reposatory for easier creation of enviroment

# My Blog App - Backend Exam Project

A simple blog application built with Flask and SQLite for the backend exam.

## Project Overview

_(Briefly describe the purpose of the application here later - e.g., allows users to create, view, and comment on blog posts, filter by tags, etc.)_

## Features

_(List the main features here as you implement them, based on the requirements)_

- View all blog posts on the homepage
- View individual blog posts
- Add comments to posts
- Create and update blog posts
- View posts by tag
- ...

## Setup Instructions

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd my_blog_app
    ```
2.  **Create and activate a virtual environment:**

    ```bash
    # Windows (PowerShell)
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1

    # macOS/Linux
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Set up environment variables:**

    - Create a `.env` file in the `my_blog_app` directory.
    - Add the following line, replacing the value with a strong secret:
      ```dotenv
      SECRET_KEY='your_super_secret_random_string_here'
      ```
    - _(Add instructions for database setup here later)_

5.  **Initialize the database:**
    _(Add command or instructions on how to create the database tables here later)_
    ```bash
    # Example: flask init-db
    ```

## Running the Application

1.  Ensure your virtual environment is activated (`(.venv)` should be visible in your terminal prompt).
2.  Run the Flask development server:
    ```bash
    python app.py
    ```
3.  Open your web browser and navigate to `http://127.0.0.1:5001` (or the address shown in the terminal).

## Running Tests

_(Add instructions on how to run your tests here later)_

```bash
# Example: pytest
```
