I've been asked to develop a Flask-based web-app that integrates with Discord using its API and stores messages in a SQLite database.

***
MUST REMEMBER: to push initial commit to GitHub - WITH the .gitignore file, AND WITHOUT the .env file !!!
***

- need to figure out a way to have the /messages route display messages that are from the last 30 minutes
+ done using the variable:
thirty_minutes_ago = now - (30 * 60)
which uses:
now = int(time.time())
which uses:
import time
+ verified working - only messages younger than 30 minutes are showing up.

- refactored the /add_message route so that it called the two functions "save to DB" and "send to Discord" - keeps the code a little bit neater and more modular.

- for incorporating JSON, and integrating with API calls:
+ I thought it might be nicer to separate the two "display methods"-
"/api/messages" for future code integration - right now getting and posting programmatically.
"/messages" for the human-facing frontend

tested these API calls by:
browsing to /api/messages - and seeing the JSON'd reults.
CURLing:
curl -X POST http://localhost:5000/api/messages \
     -H "Content-Type: application/json" \
     -d '{"content": "___ typed in my test message here___"}'
+ and saw my test message appear both in Discord, and in the JSON list.