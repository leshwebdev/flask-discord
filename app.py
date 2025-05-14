import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect
from discord_webhook import DiscordWebhook
import sqlite3
import time
from datetime import datetime
#import json

app = Flask(__name__)

now = int(time.time())
# define the "in the last 30 minutes" variable
thirty_minutes_ago = now - (30 * 60)

# decorate the timestamp so that it's human readable
@app.template_filter('format_timestamp')
def format_timestamp(unix_time):
    return datetime.fromtimestamp(unix_time).strftime('%Y-%m-%d %H:%M:%S')

# Load .env variables
load_dotenv()

#load Discord webhook url, which has been neatly redacted in .gitignore
uri = os.getenv("DISCORDWEBHOOK_URL")

## Load JSON file
#with open('products.json') as file:
#    data = json.load(file)  # Load JSON as Python list

#@app.route('/')
#def home():
#    return "Hello, Home Page!"

@app.route('/messages')
def messages():
    conn = db_connect()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Messages WHERE timestamp >= ?", (thirty_minutes_ago,))
#    cursor.execute("SELECT * FROM Messages")
    rows = cursor.fetchall()
    conn.close()
    return render_template('messages.html', messages=rows)

def db_connect():
    conn = sqlite3.connect("messages.db")
    conn.row_factory = sqlite3.Row
    return conn

# timesatamp will be an integer in UNIX time - might have to convert later on...
def init_db():
    conn = db_connect()
    conn.execute("""
    CREATE TABLE IF NOT EXISTS Messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT,
        timestamp INTEGER
    )
    """)
    print("DB INIT")
    conn.close()

@app.route('/add_message', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
# this saves the new message to the [local] SQLite3 DB and then publishes to Discord via the webhook
def add_message():
    if request.method == 'POST':
 #       id = request.form['id']
        content = request.form['content']
        timestamp = int(time.time())
        conn = db_connect()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO messages (content, timestamp) VALUES (?, ?)', (content, timestamp))
        conn.commit()
        conn.close()
        send_to_discord(content)
        return redirect('/messages')
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <title>Add Message</title>
      <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="bg-light">
      <div class="container mt-5">
        <h1>Add a New Message</h1>
        <form method="post">
          <div class="mb-3">
            <label for="content" class="form-label">Your Message</label>
            <input type="text" name="content" class="form-control" required>
          </div>
          <button type="submit" class="btn btn-success">Send Message</button>
          <a href="/messages" class="btn btn-secondary ms-2">Back to Messages</a>
        </form>
      </div>
    </body>
    </html>
    '''

# this sends the new message to Discord 
def send_to_discord(text):
    webhook = DiscordWebhook(url=uri, content=text)
    webhook.execute()

def save_to_database(text):
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO messages (content, timestamp) VALUES (?, ?)', (text, datetime.now()))
    conn.commit()
    conn.close()

if __name__  == '__main__':
    init_db()
    app.run(debug=True,port=5000)