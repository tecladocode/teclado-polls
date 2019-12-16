import os
import psycopg2

DATABASE_URI = os.environ.get("DATABASE", "postgres://postgres:1234@localhost:5432/polling")

with psycopg2.connect(DATABASE_URI) as connection:
    with connection.cursor() as cur:
        cur.execute("CREATE TABLE IF NOT EXISTS options (option_id SERIAL PRIMARY KEY, option_text TEXT, poll_id INTEGER);")
        cur.execute("CREATE TABLE IF NOT EXISTS polls (poll_id SERIAL PRIMARY KEY, title TEXT, owner TEXT, owner_discriminator TEXT);")
        cur.execute("CREATE TABLE IF NOT EXISTS votes (username TEXT, discriminator TEXT, vote INTEGER, poll_id INTEGER);")