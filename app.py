import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, jsonify
from discord_webhook import DiscordWebhook
import sqlite3
import time
from datetime import datetime

app = Flask(__name__)

now = int(time.time())
# define the "in the last 30 minutes" variable
thirty_minutes_ago = now - (30 * 60)

# decorate the timestamp so that it's human readable
@app.template_filter('format_timestamp')
def format_timestamp(unix_time):
    return datetime.fromtimestamp(unix_time).strftime('%Y-%m-%d %H:%M:%S')

# Load .env 
load_dotenv()

# load Discord webhook url, which has been neatly redacted in .gitignore
uri = os.getenv("DISCORDWEBHOOK_URL")

# connect to the SQLite3 DB
def db_connect():
    conn = sqlite3.connect("messages.db")
    conn.row_factory = sqlite3.Row
    return conn

# initialize the SQLite3 DB, creating the "messages" table if !exists
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

# this displays the messages from the last 30 minutes, in the Flask frontend
@app.route('/messages')
def messages():
    conn = db_connect()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Messages WHERE timestamp >= ?", (thirty_minutes_ago,))
    rows = cursor.fetchall()
    conn.close()
    return render_template('messages.html', messages=rows)

# this displays the messages from the last 30 minutes, in the API
@app.route('/api/messages')
def api_messages():
    conn = db_connect()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Messages WHERE timestamp >= ?", (thirty_minutes_ago,))
    rows = cursor.fetchall()
    conn.close()
    messages = [dict(row) for row in rows]
    return jsonify(messages)

# this saves the new message to the [local] SQLite3 DB and then publishes to Discord via the webhook
@app.route('/', methods=['GET', 'POST'])
def add_message():
    if request.method == 'POST':
        content = request.form['content']
        timestamp = int(time.time())
        save_to_database(content, timestamp)
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

# this is the API route for posting messages
@app.route('/api/messages', methods=['POST'])
def api_add_message():
    data = request.get_json()
    if not data or 'content' not in data:
        return jsonify({'error': 'Invalid request, must include "content"'}), 400

    content = data['content']
    timestamp = int(time.time())

    save_to_database(content, timestamp)
    send_to_discord(content)

    return jsonify({'status': 'success', 'content': content, 'timestamp': timestamp}), 201

# this saves to the local SQLite3 DB
def save_to_database(content, timestamp):
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO messages (content, timestamp) VALUES (?, ?)', (content, timestamp))    
    conn.commit()
    conn.close()

# this sends the new message to Discord 
def send_to_discord(text):
    webhook = DiscordWebhook(url=uri, content=text)
    webhook.execute()

if __name__  == '__main__':
    init_db()
    app.run(debug=True,port=5000)