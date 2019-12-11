import sqlite3
from flask import Flask, render_template, request, session
import requests
from secrets import CLIENT_SECRET
import create_test_data


app = Flask(__name__)
app.secret_key = "jose"

DISCORD_AUTH_URL = "https://discordapp.com/api/oauth2/authorize"
DISCORD_TOKEN_URL = "https://discordapp.com/api/oauth2/token"
DISCORD_GET_CURRENT_USER = "https://discordapp.com/api/users/@me"

CLIENT_ID = "654393272189321237"

FINAL_URI = f"{DISCORD_AUTH_URL}?client_id={CLIENT_ID}&redirect_uri=https%3A%2F%2Fteclado-polls.herokuapp.com%2Fauthorize&response_type=code&scope=identify"


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
        'redirect_uri': "https://teclado-polls.herokuapp.com//authorize",
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

    with sqlite3.connect("data.db") as connection:
        latest_poll_id = connection.execute("SELECT * FROM polls ORDER BY poll_id LIMIT 1").fetchone()[0]
        poll = connection.execute("SELECT * FROM polls JOIN options on polls.poll_id = options.poll_id WHERE polls.poll_id = ?", (latest_poll_id,)).fetchall()
        title = poll[0][1]

    return render_template("latest.html", title=title, poll=poll)


@app.route("/poll/<int:poll_id>")
def poll(poll_id):
    with sqlite3.connect("data.db") as connection:
        poll = connection.execute("SELECT * FROM polls JOIN options on polls.poll_id = options.poll_id WHERE polls.poll_id = ?", (poll_id,)).fetchall()
        title = poll[0][1]
    return render_template("latest.html", title=title, poll=poll)


@app.route("/vote", methods=["POST"])
def vote():
    selected_vote = request.form.get("vote")
    with sqlite3.connect("data.db") as connection:
        connection.execute(
            "INSERT INTO votes (username, discriminator, vote, poll_id) VALUES (?, ?, ?, ?)",
            (session['username'], session['discriminator'], selected_vote, 1)
        )

    return f"You voted for {selected_vote}"


@app.route("/view/<int:poll_id>")
def view_poll(poll_id):
    with sqlite3.connect("data.db") as connection:
        cursor = connection.execute("SELECT * FROM polls WHERE poll_id = ?", (poll_id,))
        poll = cursor.fetchone()

        votes_cursor = connection.execute("SELECT vote, COUNT(*) as count FROM votes WHERE poll_id = ? GROUP BY vote;", (poll_id,))
        votes = votes_cursor.fetchall()
    return render_template("view_poll.html", poll=poll, votes=votes)


@app.route("/create_poll", methods=["GET", "POST"])
def create_poll():
    if request.method == "POST":
        title = request.form.get("title")
        option_keys = ["option1", "option2", "option3", "option4"]

        with sqlite3.connect("data.db") as connection:
            connection.execute("INSERT INTO polls (title) VALUES (?)", (title,))
            last_inserted_id = connection.execute("SELECT last_insert_rowid();").fetchone()[0]

            options = [(request.form.get(option), last_inserted_id) for option in option_keys if request.form.get(option)]
            connection.executemany("INSERT INTO options (option_text, poll_id) VALUES (?, ?)", options)
    return render_template("create_poll.html")
