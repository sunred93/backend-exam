-- schema.sql

-- Table for storing blog posts
CREATE TABLE posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT, -- Unique identifier for each post
    title TEXT NOT NULL,                  -- Title of the blog post
    content TEXT NOT NULL,                -- Main body/content of the post
    published_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP -- When the post was created/published
);

-- Table for storing tags
CREATE TABLE tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT, -- Unique identifier for each tag
    name TEXT NOT NULL UNIQUE             -- Name of the tag (must be unique)
);

-- Table for storing comments on posts
CREATE TABLE comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT, -- Unique identifier for each comment
    post_id INTEGER NOT NULL,             -- Which post this comment belongs to
    author TEXT NOT NULL,                 -- Who wrote the comment (using 'author' instead of 'title' as per common practice)
    content TEXT NOT NULL,                -- The text of the comment
    published_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, -- When the comment was submitted
    FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE CASCADE -- If a post is deleted, delete its comments too
);

-- Linking table for the many-to-many relationship between posts and tags
CREATE TABLE post_tags (
    post_id INTEGER NOT NULL,             -- The ID of the post
    tag_id INTEGER NOT NULL,              -- The ID of the tag
    PRIMARY KEY (post_id, tag_id),        -- Ensures a post can only have a specific tag once
    FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE CASCADE, -- If a post is deleted, remove its tag associations
    FOREIGN KEY (tag_id) REFERENCES tags (id) ON DELETE CASCADE  -- If a tag is deleted, remove its post associations
);

-- Optional: Indexes can improve query performance, especially on larger tables
CREATE INDEX idx_posts_published_date ON posts (published_date);
CREATE INDEX idx_comments_post_id ON comments (post_id);
CREATE INDEX idx_tags_name ON tags (name);
CREATE INDEX idx_post_tags_tag_id ON post_tags (tag_id);

