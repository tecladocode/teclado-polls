import sqlite3

with sqlite3.connect("data.db") as connection:
    connection.execute("CREATE TABLE options (option_id INTEGER PRIMARY KEY, option_text TEXT, poll_id INTEGER);")
    connection.execute("CREATE TABLE polls (poll_id INTEGER PRIMARY KEY, title TEXT);")
    connection.execute("CREATE TABLE votes (username TEXT, discriminator TEXT, vote TEXT, poll_id TEXT);")