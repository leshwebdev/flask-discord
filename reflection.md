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

