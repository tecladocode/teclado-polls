import sqlite3

with sqlite3.connect("data.db") as connection:
    connection.execute("CREATE TABLE IF NOT EXISTS options (option_id INTEGER PRIMARY KEY, option_text TEXT, poll_id INTEGER);")
    connection.execute("CREATE TABLE IF NOT EXISTS polls (poll_id INTEGER PRIMARY KEY, title TEXT, owner TEXT, owner_discriminator TEXT);")
    connection.execute("CREATE TABLE IF NOT EXISTS votes (username TEXT, discriminator TEXT, vote TEXT, poll_id TEXT);")