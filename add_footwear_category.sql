-- SQL script to add Footwear category to the database
-- Run this in your SQLite/PostgreSQL database

INSERT INTO categories (name, slug, image, is_active, created_at)
VALUES ('Footwear', 'footwear', '', 1, datetime('now'));

-- Verify the category was added
SELECT * FROM categories WHERE slug = 'footwear';
