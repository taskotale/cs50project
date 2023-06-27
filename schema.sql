CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    username TEXT NOT NULL,
    hash TEXT NOT NULL
);

CREATE TABLE bookshelves (
    id INTEGER NOT NULL,
    description TEXT,
    image BLOB,
    PRIMARY KEY(id)
);

CREATE TABLE books (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    language TEXT NOT NULL,
    location INTEGER NOT NULL,
    description TEXT,
    image BLOB, 
    bookshelf_id INTEGER,
    user_id INTEGER,
    FOREIGN KEY(bookshelf_id) REFERENCES bookshelves(id),
    FOREIGN KEY(user_id) REFERENCES users(id)
);

ALTER TABLE books ADD date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL;