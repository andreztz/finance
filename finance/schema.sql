CREATE TABLE users (
            id INTEGER,
            username TEXT NOT NULL,
            hash TEXT NOT NULL,
            cash REAL NOT NULL DEFAULT 10000.00,
            PRIMARY KEY(id)
        );
CREATE TABLE transactions (
            id INTEGER,
            user_id INTEGER NOT NULL,
            symbol_id INTEGER NOT NULL,
            created_at DATETIME NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%s', 'now')),
            price REAL NOT NULL,
            shares_qtd INTEGER NOT NULL,
            type TEXT NOT NULL CHECK (type in ('buy', 'sell')),
            PRIMARY KEY(id),
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(symbol_id) REFERENCES symbols(id)
        );
CREATE TABLE symbols (
            id INTEGER,
            name TEXT NOT NULL,
            symbol TEXT NOT NULL,
            PRIMARY KEY(id)
        );
CREATE UNIQUE INDEX username ON users(username);
