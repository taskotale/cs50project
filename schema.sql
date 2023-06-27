CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    username TEXT NOT NULL,
    hash TEXT NOT NULL
);

CREATE TABLE bookshelves (
    id INTEGER NOT NULL,
    description TEXT,
    image TEXT,
    PRIMARY KEY(id)
);

CREATE TABLE books (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    language TEXT NOT NULL,
    location INTEGER NOT NULL,
    description TEXT,
    image TEXT,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    bookshelf_id INTEGER,
    user_id INTEGER,
    FOREIGN KEY(bookshelf_id) REFERENCES bookshelves(id),
    FOREIGN KEY(user_id) REFERENCES users(id)
);
