from urllib.parse import quote
import os
import sqlite3
from flask import Flask, render_template, request, session, redirect, url_for
import requests
from secrets import CLIENT_SECRET
import create_tables


app = Flask(__name__)
app.secret_key = "jose"

DISCORD_AUTH_URL = "https://discordapp.com/api/oauth2/authorize"
DISCORD_TOKEN_URL = "https://discordapp.com/api/oauth2/token"
DISCORD_GET_CURRENT_USER = "https://discordapp.com/api/users/@me"

CLIENT_ID = "654393272189321237"
DISCORD_REDIRECT_URI = os.environ.get("DISCORD_AUTH_REDIRECT", "http://127.0.0.1:5000/authorize")

FINAL_URI = f"{DISCORD_AUTH_URL}?client_id={CLIENT_ID}&redirect_uri={quote(DISCORD_REDIRECT_URI)}&response_type=code&scope=identify"


@app.route("/")
def home():
    return render_template("home.html", discord_uri=FINAL_URI)


@app.route("/authorize")
def authorize():
    code = request.args.get("code")

    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': DISCORD_REDIRECT_URI,
        'scope': 'identify'
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    response = requests.post(DISCORD_TOKEN_URL, data=data, headers=headers)
    access_token = response.json().get("access_token")

    resp = requests.get(DISCORD_GET_CURRENT_USER, headers={"Authorization": f"Bearer {access_token}"})
    json_data = resp.json()
    session["username"] = json_data.get("username")
    session["discriminator"] = json_data.get("discriminator")

    if session.get('poll_id'):
        return redirect(url_for('poll', poll_id=session['poll_id']))

    with sqlite3.connect("data.db") as connection:
        latest_poll = connection.execute("SELECT * FROM polls ORDER BY poll_id DESC LIMIT 1").fetchone()
        if not latest_poll:
            return redirect(url_for("create_poll"))

        latest_poll_id = latest_poll[0]
        poll = connection.execute("SELECT * FROM polls JOIN options on polls.poll_id = options.poll_id WHERE polls.poll_id = ?", (latest_poll_id,)).fetchall()
        title = poll[0][1]

    return render_template("latest.html", title=title, poll=poll, poll_id=latest_poll_id, discord_uri=FINAL_URI)


@app.route("/poll/<int:poll_id>")
def poll(poll_id):
    session['poll_id'] = poll_id
    with sqlite3.connect("data.db") as connection:
        poll = connection.execute("SELECT * FROM polls JOIN options on polls.poll_id = options.poll_id WHERE polls.poll_id = ?", (poll_id,)).fetchall()
        title = poll[0][1]
    return render_template("latest.html", title=title, poll=poll, poll_id=poll_id, discord_uri=FINAL_URI)


@app.route("/vote/<int:poll_id>", methods=["POST"])
def vote(poll_id):
    selected_vote = request.form.get("vote")
    with sqlite3.connect("data.db") as connection:
        connection.execute(
            "INSERT INTO votes (username, discriminator, vote, poll_id) VALUES (?, ?, ?, ?)",
            (session['username'], session['discriminator'], selected_vote, poll_id)
        )

    return f"You voted for {selected_vote}"


@app.route("/view/<int:poll_id>")
def view_poll(poll_id):
    with sqlite3.connect("data.db") as connection:
        cursor = connection.execute("SELECT * FROM polls WHERE poll_id = ?", (poll_id,))
        poll = cursor.fetchone()

        votes_cursor = connection.execute("""
            SELECT options.option_text, COUNT(votes.vote) as count, COUNT(votes.vote) * 100.0 / sum(count(votes.vote)) over() as percentage FROM options
            LEFT JOIN votes on options.option_id = votes.vote
            WHERE options.poll_id = ?
            GROUP BY options.option_text;""", (poll_id,))
        votes = votes_cursor.fetchall()
    return render_template("view_poll.html", poll=poll, votes=votes, discord_uri=FINAL_URI)


@app.route("/create_poll", methods=["GET", "POST"])
def create_poll():
    if request.method == "POST":
        title = request.form.get("title")
        option_keys = ["option1", "option2", "option3", "option4"]

        with sqlite3.connect("data.db") as connection:
            cursor = connection.execute("INSERT INTO polls (title, owner, owner_discriminator) VALUES (?, ?, ?)", (title, session['username'], session['discriminator']))
            last_inserted_id = cursor.lastrowid

            options = [(request.form.get(option), last_inserted_id) for option in option_keys if request.form.get(option)]
            connection.executemany("INSERT INTO options (option_text, poll_id) VALUES (?, ?)", options)

        return redirect(url_for("poll", poll_id=last_inserted_id))
    return render_template("create_poll.html", discord_uri=FINAL_URI)


@app.route("/manage_polls")
def manage_polls():
    with sqlite3.connect("data.db") as connection:
        cursor = connection.execute("SELECT * FROM polls WHERE owner = ? AND owner_discriminator = ?",
                                    (session["username"], session["discriminator"]))

        return render_template("manage_polls.html", polls=cursor.fetchall())


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))