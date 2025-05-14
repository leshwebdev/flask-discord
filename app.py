import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect
from discord_webhook import DiscordWebhook
import sqlite3
#import json

app = Flask(__name__)

#load Discord webhook url
uri = os.getenv("DISCORDWEBHOOK_URL")

# Load .env variables
load_dotenv()

## Load JSON file
#with open('products.json') as file:
#    data = json.load(file)  # Load JSON as Python list

@app.route('/')
def home():
    return "Hello, Home Page!"

# need to figure out a way to have this route display messages that are from the last 30 minutes
@app.route('/messages')
def messages():
    conn = db_connect()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Messages")
    rows = cursor.fetchall()
    conn.close
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
    conn.close

@app.route('/add_message', methods=['GET', 'POST'])
# this saves the new message to the [local] SQLite3 DB
def add_message():
    if request.method == 'POST':
        id = request.form['id']
        content = request.form['content']
        timestamp = request.form['timestamp']
        conn = db_connect()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO messages (id, content, timestamp) VALUES (?, ?, ?)', (id, content, timestamp))
        conn.commit()
        conn.close()
        return redirect('/messages')
    return '''
        <form method="post">
            Your message: <input type="text" content="content"><br>
            <input type="submit" value="Send Message">
        </form>
    '''
# this sends the new message to Discord 
def send_to_discord(text):
    webhook = DiscordWebhook(url=uri, content=text)
    webhook.execute()

def save_to_database(text):
    conn = get_db_connect()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO messages (content, timestamp) VALUES (?, ?)', (text, datetime.now()))
    conn.commit()
    conn.close()

if __name__  == '__main__':
    init_db()
    app.run(debug=True,port=5000)